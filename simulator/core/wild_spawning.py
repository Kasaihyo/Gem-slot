"""
Wild spawning system for Esqueleto Explosivo 3.

This module implements the guaranteed wild spawning mechanic that triggers after
each winning cluster is removed. Features include:
- 100% spawn chance per winning cluster
- 50/50 probability split between regular Wild and Explosivo Wild
- Random position selection within cluster footprint
- Collision handling for multiple simultaneous spawns
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from simulator.core.symbol import Symbol
from simulator.core.grid import Grid
from simulator.core.clusters import Cluster
from simulator.core.rng import SpinRNG
import logging

logger = logging.getLogger(__name__)


@dataclass
class WildSpawn:
    """Represents a wild spawn attempt."""
    cluster_id: int  # Unique identifier for the cluster
    wild_type: Symbol  # Either Symbol.WILD or Symbol.E_WILD
    footprint: List[Tuple[int, int]]  # Original cluster positions
    spawned_position: Optional[Tuple[int, int]] = None  # Where it was placed
    success: bool = False  # Whether spawn succeeded


class WildSpawningSystem:
    """
    Manages wild spawning after winning clusters.
    
    Key responsibilities:
    - Track cluster footprints before removal
    - Select wild type (50/50 split)
    - Find empty positions within footprint
    - Handle collision resolution
    - Coordinate multi-cluster spawning
    """
    
    # Configuration for wild type probabilities (must sum to 1.0)
    WILD_PROBABILITY = 0.5
    EXPLOSIVO_WILD_PROBABILITY = 0.5
    
    def __init__(self):
        """Initialize the wild spawning system."""
        # Validate probabilities
        if abs(self.WILD_PROBABILITY + self.EXPLOSIVO_WILD_PROBABILITY - 1.0) > 0.0001:
            raise ValueError("Wild spawn probabilities must sum to 1.0")
    
    def spawn_wilds_for_clusters(
        self, 
        grid: Grid, 
        clusters: List[Cluster], 
        rng: SpinRNG
    ) -> List[WildSpawn]:
        """
        Spawn wilds for all winning clusters.
        
        This is the main entry point for wild spawning. It processes all
        clusters and handles collision resolution.
        
        Args:
            grid: Current game grid (after cluster removal)
            clusters: List of winning clusters with their original positions
            rng: Random number generator for spawn decisions
            
        Returns:
            List of WildSpawn objects describing spawn attempts
        """
        if not clusters:
            return []
        
        spawn_attempts = []
        occupied_positions = set()
        
        # Process each cluster in order (deterministic for reproducibility)
        for cluster_id, cluster in enumerate(clusters):
            # Create spawn attempt for this cluster
            spawn = self._create_spawn_attempt(cluster_id, cluster, rng)
            
            # Try to place the wild
            success = self._place_wild(
                grid, 
                spawn, 
                occupied_positions, 
                rng
            )
            
            if success:
                occupied_positions.add(spawn.spawned_position)
                logger.debug(
                    f"Spawned {spawn.wild_type.name} at {spawn.spawned_position} "
                    f"for cluster {cluster_id}"
                )
            else:
                logger.debug(
                    f"Failed to spawn wild for cluster {cluster_id} - "
                    f"no available positions"
                )
            
            spawn_attempts.append(spawn)
        
        return spawn_attempts
    
    def _create_spawn_attempt(
        self, 
        cluster_id: int, 
        cluster: Cluster, 
        rng: SpinRNG
    ) -> WildSpawn:
        """
        Create a wild spawn attempt for a cluster.
        
        Args:
            cluster_id: Unique identifier for this cluster
            cluster: The winning cluster
            rng: Random number generator
            
        Returns:
            WildSpawn object with selected wild type
        """
        # Select wild type using 50/50 probability
        if rng.random() < self.WILD_PROBABILITY:
            wild_type = Symbol.WILD
        else:
            wild_type = Symbol.E_WILD
        
        return WildSpawn(
            cluster_id=cluster_id,
            wild_type=wild_type,
            footprint=cluster.positions.copy(),
            spawned_position=None,
            success=False
        )
    
    def _place_wild(
        self, 
        grid: Grid, 
        spawn: WildSpawn, 
        occupied_positions: Set[Tuple[int, int]], 
        rng: SpinRNG
    ) -> bool:
        """
        Attempt to place a wild on the grid.
        
        Args:
            grid: Current game grid
            spawn: The spawn attempt to process
            occupied_positions: Positions already claimed by other spawns
            rng: Random number generator
            
        Returns:
            True if wild was successfully placed, False otherwise
        """
        # Find empty positions within the cluster footprint
        available_positions = []
        
        for pos in spawn.footprint:
            row, col = pos
            # Position must be empty and not claimed by another spawn
            if grid.is_empty(row, col) and pos not in occupied_positions:
                available_positions.append(pos)
        
        # If no positions available, spawn fails
        if not available_positions:
            spawn.success = False
            return False
        
        # Select random position from available ones
        selected_position = rng.choice(available_positions)
        row, col = selected_position
        
        # Place the wild on the grid
        grid.set_symbol(row, col, spawn.wild_type)
        
        # Update spawn record
        spawn.spawned_position = selected_position
        spawn.success = True
        
        return True
    
    def get_spawn_statistics(self, spawn_attempts: List[WildSpawn]) -> Dict[str, int]:
        """
        Calculate statistics about spawn attempts.
        
        Args:
            spawn_attempts: List of spawn attempts to analyze
            
        Returns:
            Dictionary with spawn statistics
        """
        stats = {
            'total_attempts': len(spawn_attempts),
            'successful_spawns': 0,
            'failed_spawns': 0,
            'wild_spawns': 0,
            'explosivo_wild_spawns': 0
        }
        
        for spawn in spawn_attempts:
            if spawn.success:
                stats['successful_spawns'] += 1
                if spawn.wild_type == Symbol.WILD:
                    stats['wild_spawns'] += 1
                else:
                    stats['explosivo_wild_spawns'] += 1
            else:
                stats['failed_spawns'] += 1
        
        return stats
    
    def validate_spawn_configuration(self) -> bool:
        """
        Validate that spawn configuration is valid.
        
        Returns:
            True if configuration is valid
        """
        # Check probabilities sum to 1.0
        total_prob = self.WILD_PROBABILITY + self.EXPLOSIVO_WILD_PROBABILITY
        if abs(total_prob - 1.0) > 0.0001:
            return False
        
        # Check probabilities are non-negative
        if self.WILD_PROBABILITY < 0 or self.EXPLOSIVO_WILD_PROBABILITY < 0:
            return False
        
        return True