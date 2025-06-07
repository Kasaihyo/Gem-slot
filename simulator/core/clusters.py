"""
Cluster detection system for Esqueleto Explosivo 3.

This module implements the cluster pays winning system using the Union-Find
algorithm for efficient detection of connected symbol groups.
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from simulator.core.symbol import (
    Symbol, is_paying, is_wild, is_scatter, is_empty,
    symbols_match_for_cluster, get_config_string
)
from simulator.core.union_find import GridUnionFind
from simulator.core.grid import Grid, ROWS, COLS


@dataclass
class Cluster:
    """Represents a winning cluster of symbols."""
    symbol: Symbol  # The paying symbol type (not wild)
    positions: List[Tuple[int, int]]  # All positions in cluster
    size: int  # Number of symbols (including wilds)
    
    def __repr__(self) -> str:
        return f"Cluster({get_config_string(self.symbol)}, size={self.size})"


class ClusterDetector:
    """
    Detects winning clusters in the game grid.
    
    Uses Union-Find algorithm for efficient O(α(n)) detection where α is the
    inverse Ackermann function (practically constant).
    """
    
    def __init__(self):
        """Initialize cluster detector with reusable Union-Find structure."""
        self._union_find = GridUnionFind()
        self._adjacent_cache = self._precompute_adjacents()
    
    def _precompute_adjacents(self) -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
        """
        Precompute adjacent positions for each grid position.
        
        Returns:
            Dictionary mapping positions to their adjacent positions
        """
        adjacents = {}
        
        for row in range(ROWS):
            for col in range(COLS):
                adj = []
                # Check all 4 directions (no diagonals)
                if row > 0:  # Up
                    adj.append((row - 1, col))
                if row < ROWS - 1:  # Down
                    adj.append((row + 1, col))
                if col > 0:  # Left
                    adj.append((row, col - 1))
                if col < COLS - 1:  # Right
                    adj.append((row, col + 1))
                
                adjacents[(row, col)] = adj
        
        return adjacents
    
    def find_clusters(self, grid: Grid) -> List[Cluster]:
        """
        Find all winning clusters in the grid.
        
        A cluster is a group of 5 or more symbols connected horizontally
        or vertically. Wilds can participate in multiple clusters.
        
        Args:
            grid: The game grid to analyze
            
        Returns:
            List of Cluster objects representing all winning clusters
        """
        # Reset Union-Find for new detection
        self._union_find.reset()
        
        # Track which symbols are at which positions for wild handling
        symbol_positions: Dict[Symbol, List[Tuple[int, int]]] = {}
        position_symbols: Dict[Tuple[int, int], Symbol] = {}
        
        # First pass: collect all non-empty, non-scatter positions
        for row in range(ROWS):
            for col in range(COLS):
                symbol = grid.get_symbol(row, col)
                
                if is_empty(symbol) or is_scatter(symbol):
                    continue
                
                pos = (row, col)
                position_symbols[pos] = symbol
                
                if is_paying(symbol):  # Track paying symbols by type
                    if symbol not in symbol_positions:
                        symbol_positions[symbol] = []
                    symbol_positions[symbol].append(pos)
        
        # Process each paying symbol type separately to handle wild participation
        clusters = []
        
        for symbol, positions in symbol_positions.items():
            # Create a new Union-Find for this symbol type
            uf = GridUnionFind()
            
            # Track all positions that could be in this symbol's clusters
            relevant_positions = set(positions)
            
            # Add all wild positions as potentially relevant
            for pos, sym in position_symbols.items():
                if is_wild(sym):
                    relevant_positions.add(pos)
            
            # Union adjacent positions that match
            for pos in relevant_positions:
                row, col = pos
                pos_symbol = position_symbols[pos]
                
                # Check adjacent positions
                for adj_row, adj_col in self._adjacent_cache[pos]:
                    adj_pos = (adj_row, adj_col)
                    
                    if adj_pos not in position_symbols:
                        continue
                    
                    adj_symbol = position_symbols[adj_pos]
                    
                    # Check if these symbols can form a cluster
                    # For this symbol type's cluster:
                    # - Same symbol connects
                    # - Wild connects to paying symbol
                    # - Wild connects to wild
                    can_connect = False
                    
                    if is_wild(pos_symbol) and is_wild(adj_symbol):
                        # Wild to wild always connects
                        can_connect = True
                    elif is_wild(pos_symbol) and adj_symbol == symbol:
                        # Wild to this symbol type
                        can_connect = True
                    elif pos_symbol == symbol and is_wild(adj_symbol):
                        # This symbol type to wild
                        can_connect = True
                    elif pos_symbol == symbol and adj_symbol == symbol:
                        # Same symbol type
                        can_connect = True
                    
                    if can_connect:
                        uf.union_positions(row, col, adj_row, adj_col)
            
            # Extract clusters for this symbol type
            cluster_groups = uf.get_sets()
            
            for root_idx, member_indices in cluster_groups.items():
                # Convert indices to positions
                cluster_positions = []
                has_paying_symbol = False
                
                for idx in member_indices:
                    pos = uf._index_to_pos(idx)
                    if pos in position_symbols:
                        cluster_positions.append(pos)
                        if position_symbols[pos] == symbol:
                            has_paying_symbol = True
                
                # Valid cluster must have at least 5 symbols and contain
                # at least one non-wild symbol
                if len(cluster_positions) >= 5 and has_paying_symbol:
                    cluster = Cluster(
                        symbol=symbol,
                        positions=cluster_positions,
                        size=min(len(cluster_positions), 15)  # Cap at 15
                    )
                    clusters.append(cluster)
        
        # Sort clusters for consistent processing order
        clusters.sort(key=lambda c: (get_config_string(c.symbol), c.size), reverse=True)
        
        return clusters
    
    def get_winning_positions(self, clusters: List[Cluster]) -> Set[Tuple[int, int]]:
        """
        Get all positions that are part of winning clusters.
        
        Args:
            clusters: List of winning clusters
            
        Returns:
            Set of all positions in any winning cluster
        """
        winning_positions = set()
        for cluster in clusters:
            winning_positions.update(cluster.positions)
        return winning_positions
    
    def get_cluster_footprint(self, clusters: List[Cluster]) -> Set[Tuple[int, int]]:
        """
        Get the footprint of all clusters (for wild spawning).
        
        The footprint includes all positions that were part of any cluster,
        which determines where wilds can spawn.
        
        Args:
            clusters: List of winning clusters
            
        Returns:
            Set of all positions in cluster footprints
        """
        return self.get_winning_positions(clusters)
    
    def find_clusters_simple(self, grid: Grid) -> List[Cluster]:
        """
        Simplified cluster detection for testing.
        
        Uses basic Union-Find without complex wild handling.
        
        Args:
            grid: The game grid to analyze
            
        Returns:
            List of clusters found
        """
        self._union_find.reset()
        
        # Union all adjacent matching symbols
        for row in range(ROWS):
            for col in range(COLS):
                symbol = grid.get_symbol(row, col)
                
                if is_empty(symbol) or is_scatter(symbol):
                    continue
                
                # Check right and down only (to avoid double-checking)
                if col < COLS - 1:  # Right
                    right_symbol = grid.get_symbol(row, col + 1)
                    if symbols_match_for_cluster(symbol, right_symbol):
                        self._union_find.union_positions(row, col, row, col + 1)
                
                if row < ROWS - 1:  # Down
                    down_symbol = grid.get_symbol(row + 1, col)
                    if symbols_match_for_cluster(symbol, down_symbol):
                        self._union_find.union_positions(row, col, row + 1, col)
        
        # Extract clusters
        clusters = []
        processed = set()
        
        for row in range(ROWS):
            for col in range(COLS):
                if (row, col) in processed:
                    continue
                
                symbol = grid.get_symbol(row, col)
                if is_empty(symbol) or is_scatter(symbol):
                    continue
                
                # Get all positions in this cluster
                cluster_positions = self._union_find.get_cluster_positions(row, col)
                
                if len(cluster_positions) >= 5:
                    # Determine the paying symbol in the cluster
                    paying_symbol = None
                    for pos in cluster_positions:
                        sym = grid.get_symbol(pos[0], pos[1])
                        if is_paying(sym):
                            paying_symbol = sym
                            break
                    
                    if paying_symbol:
                        cluster = Cluster(
                            symbol=paying_symbol,
                            positions=cluster_positions,
                            size=min(len(cluster_positions), 15)
                        )
                        clusters.append(cluster)
                
                processed.update(cluster_positions)
        
        return clusters