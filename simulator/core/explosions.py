"""
Explosivo Wild explosion mechanics for Esqueleto Explosivo 3.

This module implements the explosion feature where Explosivo Wilds destroy
low-pay symbols in a 3x3 area. Key features:
- EW explodes in 3x3 area centered on its position
- Only destroys low-pay symbols (PNK, GRN, BLU, ORG, CYN)
- Preserves high-pay, wilds, other EWs, and scatters
- All eligible EWs explode simultaneously
"""

from typing import List, Set, Tuple, Dict, Optional
from dataclasses import dataclass, field
from simulator.core.symbol import Symbol, is_low_pay, is_explosivo_wild
from simulator.core.grid import Grid, ROWS, COLS
from simulator.core.clusters import Cluster
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExplosionEvent:
    """Represents a single EW explosion event."""
    ew_position: Tuple[int, int]  # Position of the exploding EW
    affected_area: List[Tuple[int, int]]  # 3x3 area around EW
    destroyed_positions: List[Tuple[int, int]]  # Positions actually destroyed
    from_cluster: bool = False  # Whether EW was in winning cluster


@dataclass 
class EWTracker:
    """Tracks Explosivo Wild states for explosion eligibility."""
    # EWs that landed this drop (from symbol generation)
    landed_this_drop: Set[Tuple[int, int]] = field(default_factory=set)
    
    # EWs that were in winning clusters
    in_winning_clusters: Set[Tuple[int, int]] = field(default_factory=set)
    
    # EWs spawned this cascade (not eligible)
    spawned_this_cascade: Set[Tuple[int, int]] = field(default_factory=set)
    
    # EWs collected for free spins feature
    collected_count: int = 0
    
    def reset_cascade(self):
        """Reset cascade-specific tracking."""
        self.landed_this_drop.clear()
        self.in_winning_clusters.clear()
        self.spawned_this_cascade.clear()
    
    def is_eligible_to_explode(self, position: Tuple[int, int]) -> bool:
        """Check if an EW at given position is eligible to explode."""
        # Spawned EWs are never eligible in their spawn cascade
        if position in self.spawned_this_cascade:
            return False
        
        # EW is eligible if it landed this drop OR was in a winning cluster
        return position in self.landed_this_drop or position in self.in_winning_clusters


class ExplosionSystem:
    """
    Manages Explosivo Wild explosions.
    
    Key responsibilities:
    - Track EW eligibility for explosions
    - Calculate 3x3 explosion areas
    - Apply destruction rules (low-pay only)
    - Handle simultaneous explosions
    - Track EW collections for free spins
    """
    
    def __init__(self):
        """Initialize the explosion system."""
        self.ew_tracker = EWTracker()
        self._explosion_offsets = self._calculate_explosion_offsets()
    
    def _calculate_explosion_offsets(self) -> List[Tuple[int, int]]:
        """
        Pre-calculate the 3x3 offsets for explosion area.
        
        Returns:
            List of (row_offset, col_offset) tuples for 3x3 area
        """
        offsets = []
        for row_offset in range(-1, 2):
            for col_offset in range(-1, 2):
                offsets.append((row_offset, col_offset))
        return offsets
    
    def track_landed_ews(self, grid: Grid):
        """
        Track all EWs that landed this drop (from symbol generation).
        
        Args:
            grid: The game grid after symbols dropped
        """
        self.ew_tracker.landed_this_drop.clear()
        
        for row in range(ROWS):
            for col in range(COLS):
                if is_explosivo_wild(grid.get_symbol(row, col)):
                    self.ew_tracker.landed_this_drop.add((row, col))
        
        logger.debug(f"Tracked {len(self.ew_tracker.landed_this_drop)} landed EWs")
    
    def track_cluster_ews(self, clusters: List[Cluster], grid: Grid):
        """
        Track EWs that are part of winning clusters.
        
        Args:
            clusters: List of winning clusters
            grid: The game grid
        """
        self.ew_tracker.in_winning_clusters.clear()
        
        for cluster in clusters:
            for pos in cluster.positions:
                if is_explosivo_wild(grid.get_symbol(pos[0], pos[1])):
                    self.ew_tracker.in_winning_clusters.add(pos)
                    # Collect EW immediately when in winning cluster
                    self.ew_tracker.collected_count += 1
                    logger.debug(f"Collected EW from winning cluster (total: {self.ew_tracker.collected_count})")
        
        logger.debug(f"Tracked {len(self.ew_tracker.in_winning_clusters)} cluster EWs")
    
    def track_spawned_ew(self, position: Tuple[int, int]):
        """
        Track an EW that was spawned (not eligible this cascade).
        
        Args:
            position: Position where EW was spawned
        """
        self.ew_tracker.spawned_this_cascade.add(position)
        logger.debug(f"Tracked spawned EW at {position}")
    
    def calculate_explosion_area(self, ew_position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Calculate the 3x3 area affected by an EW explosion.
        
        Args:
            ew_position: Position of the exploding EW
            
        Returns:
            List of positions in the explosion area (on-grid only)
        """
        row, col = ew_position
        affected_positions = []
        
        for row_offset, col_offset in self._explosion_offsets:
            new_row = row + row_offset
            new_col = col + col_offset
            
            # Only include positions that are on the grid
            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                affected_positions.append((new_row, new_col))
        
        return affected_positions
    
    def find_eligible_ews(self, grid: Grid) -> List[Tuple[int, int]]:
        """
        Find all EWs eligible to explode in the current state.
        
        Args:
            grid: The current game grid
            
        Returns:
            List of positions containing eligible EWs
        """
        eligible_positions = []
        
        for row in range(ROWS):
            for col in range(COLS):
                pos = (row, col)
                if (is_explosivo_wild(grid.get_symbol(row, col)) and 
                    self.ew_tracker.is_eligible_to_explode(pos)):
                    eligible_positions.append(pos)
        
        return eligible_positions
    
    def execute_explosions(self, grid: Grid, eligible_ews: Optional[List[Tuple[int, int]]] = None) -> List[ExplosionEvent]:
        """
        Execute all eligible EW explosions simultaneously.
        
        Args:
            grid: The game grid to modify
            eligible_ews: Optional list of eligible EW positions (if None, will find them)
            
        Returns:
            List of ExplosionEvent objects describing what happened
        """
        # Find eligible EWs if not provided
        if eligible_ews is None:
            eligible_ews = self.find_eligible_ews(grid)
        
        if not eligible_ews:
            logger.debug("No eligible EWs to explode")
            return []
        
        logger.info(f"Executing explosions for {len(eligible_ews)} EWs")
        
        # Track all positions to be destroyed (use set to avoid duplicates)
        positions_to_destroy = set()
        explosion_events = []
        
        # Calculate all explosion areas first
        for ew_pos in eligible_ews:
            explosion_area = self.calculate_explosion_area(ew_pos)
            destroyed_in_area = []
            
            # Check each position in explosion area
            for pos in explosion_area:
                symbol = grid.get_symbol(pos[0], pos[1])
                
                # Only destroy low-pay symbols
                if is_low_pay(symbol):
                    positions_to_destroy.add(pos)
                    destroyed_in_area.append(pos)
            
            # Create explosion event
            from_cluster = ew_pos in self.ew_tracker.in_winning_clusters
            event = ExplosionEvent(
                ew_position=ew_pos,
                affected_area=explosion_area,
                destroyed_positions=destroyed_in_area,
                from_cluster=from_cluster
            )
            explosion_events.append(event)
        
        # Apply all destructions simultaneously
        for pos in positions_to_destroy:
            grid.set_symbol(pos[0], pos[1], Symbol.EMPTY)
        
        logger.info(f"Destroyed {len(positions_to_destroy)} symbols in explosions")
        
        # EWs that exploded are also destroyed
        for ew_pos in eligible_ews:
            grid.set_symbol(ew_pos[0], ew_pos[1], Symbol.EMPTY)
            # Count non-cluster EWs as collected too
            if ew_pos not in self.ew_tracker.in_winning_clusters:
                self.ew_tracker.collected_count += 1
        
        return explosion_events
    
    def should_check_explosions(self, clusters_found: bool) -> bool:
        """
        Determine if explosions should be checked based on game state.
        
        Explosions occur when no winning clusters are found.
        
        Args:
            clusters_found: Whether any winning clusters were found
            
        Returns:
            True if explosions should be checked
        """
        return not clusters_found
    
    def reset_cascade_state(self):
        """Reset cascade-specific tracking for next cascade."""
        self.ew_tracker.reset_cascade()
    
    def get_collected_count(self) -> int:
        """Get the total number of EWs collected."""
        return self.ew_tracker.collected_count
    
    def reset_collected_count(self):
        """Reset the collected EW count (e.g., when entering free spins)."""
        self.ew_tracker.collected_count = 0