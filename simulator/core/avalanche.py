"""
Avalanche cascade system for Esqueleto Explosivo 3.

This module implements the core game loop that orchestrates the cascading
avalanche mechanics, managing state transitions, multiplier progression,
and coordination of all subsystems.
"""

from enum import Enum, auto
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
import logging

from simulator.core.symbol import Symbol, is_scatter
from simulator.core.grid import Grid, ROWS, COLS
from simulator.core.rng import SpinRNG
from simulator.core.clusters import ClusterDetector, Cluster
from simulator.core.wild_spawning import WildSpawningSystem
from simulator.core.explosions import ExplosionSystem
from simulator.config import (
    BG_SYMBOL_NAMES, BG_WEIGHTS,
    FS_SYMBOL_NAMES, FS_WEIGHTS,
    CLUSTER_PAYS, MAX_WIN_MULTIPLIER
)

logger = logging.getLogger(__name__)


class GameState(Enum):
    """Game flow states matching PRD section 11."""
    REEL_DROP = auto()
    CHECK_SCATTERS = auto()
    CHECK_CLUSTERS = auto()
    CHECK_EXPLOSIONS = auto()
    SEQUENCE_COMPLETE = auto()


class MultiplierLevel(Enum):
    """Multiplier progression levels."""
    X1 = 1
    X2 = 2
    X4 = 4
    X8 = 8
    X16 = 16
    X32 = 32
    
    def next_level(self) -> 'MultiplierLevel':
        """Get the next multiplier level in progression."""
        progression = [
            MultiplierLevel.X1,
            MultiplierLevel.X2,
            MultiplierLevel.X4,
            MultiplierLevel.X8,
            MultiplierLevel.X16,
            MultiplierLevel.X32
        ]
        
        try:
            current_idx = progression.index(self)
            if current_idx < len(progression) - 1:
                return progression[current_idx + 1]
        except ValueError:
            pass
        
        return self  # Already at max


@dataclass
class CascadeResult:
    """Result of a complete cascade sequence."""
    total_win: int = 0
    max_multiplier_reached: int = 1
    total_cascades: int = 0
    scatters_found: int = 0
    free_spins_triggered: bool = False
    max_win_reached: bool = False
    win_details: List[Dict[str, Any]] = field(default_factory=list)
    state_history: List[GameState] = field(default_factory=list)


@dataclass
class AvalancheState:
    """Current state of the avalanche system."""
    current_state: GameState = GameState.REEL_DROP
    multiplier: MultiplierLevel = MultiplierLevel.X1
    cascade_count: int = 0
    total_win: int = 0
    scatters_found: int = 0
    free_spins_triggered: bool = False
    is_initial_drop: bool = True
    is_free_spins: bool = False
    bet_amount: int = 100  # Default bet in cents
    

class AvalancheSystem:
    """
    Manages the complete avalanche cascade system.
    
    This is the main game controller that orchestrates all game mechanics
    in the correct sequence according to the PRD flow.
    """
    
    def __init__(self):
        """Initialize the avalanche system with all subsystems."""
        self.grid = Grid()
        self.cluster_detector = ClusterDetector()
        self.wild_spawner = WildSpawningSystem()
        self.explosion_system = ExplosionSystem()
        self.state = AvalancheState()
        
    def reset(self, bet_amount: int = 100, is_free_spins: bool = False):
        """
        Reset the system for a new spin.
        
        Args:
            bet_amount: Bet amount in cents
            is_free_spins: Whether this is a free spins round
        """
        self.grid.clear()
        self.explosion_system.reset_cascade_state()
        self.state = AvalancheState(
            bet_amount=bet_amount,
            is_free_spins=is_free_spins
        )
        logger.info(f"Avalanche system reset - bet: {bet_amount}, FS: {is_free_spins}")
        
    def play_spin(self, rng: SpinRNG, force_enrico: bool = False) -> CascadeResult:
        """
        Play a complete spin with all cascades.
        
        Args:
            rng: Random number generator
            force_enrico: Force "The Enrico Show" (1 EW on initial drop)
            
        Returns:
            CascadeResult with all spin outcomes
        """
        result = CascadeResult()
        
        # Main game loop
        while self.state.current_state != GameState.SEQUENCE_COMPLETE:
            # Record state for debugging
            result.state_history.append(self.state.current_state)
            
            # Execute current state
            if self.state.current_state == GameState.REEL_DROP:
                self._handle_reel_drop(rng, force_enrico)
                
            elif self.state.current_state == GameState.CHECK_SCATTERS:
                self._handle_scatter_check(result)
                
            elif self.state.current_state == GameState.CHECK_CLUSTERS:
                self._handle_cluster_check(rng, result)
                
            elif self.state.current_state == GameState.CHECK_EXPLOSIONS:
                self._handle_explosion_check(result)
                
            # Check for max win after any win event
            if self.state.total_win >= MAX_WIN_MULTIPLIER * self.state.bet_amount:
                # Cap at exactly max win
                self.state.total_win = MAX_WIN_MULTIPLIER * self.state.bet_amount
                logger.info(f"MAX WIN REACHED: {self.state.total_win / self.state.bet_amount}x")
                result.max_win_reached = True
                self.state.current_state = GameState.SEQUENCE_COMPLETE
        
        # Finalize result
        result.total_win = self.state.total_win
        result.max_multiplier_reached = self.state.multiplier.value
        result.total_cascades = self.state.cascade_count
        result.scatters_found = self.state.scatters_found
        result.free_spins_triggered = self.state.free_spins_triggered
        
        return result
        
    def _handle_reel_drop(self, rng: SpinRNG, force_enrico: bool = False):
        """Handle the REEL_DROP state."""
        logger.debug(f"REEL_DROP - cascade {self.state.cascade_count}")
        
        # Fill empty positions
        if self.state.is_initial_drop:
            # Initial spin - fill all positions
            self._fill_grid(rng, force_enrico)
            self.state.is_initial_drop = False
        else:
            # Cascade drop - only fill empty positions
            self._fill_empty_positions(rng)
            
        # Track landed EWs for explosion eligibility
        self.explosion_system.track_landed_ews(self.grid)
        
        # Always proceed to scatter check
        self.state.current_state = GameState.CHECK_SCATTERS
        
    def _handle_scatter_check(self, result: CascadeResult):
        """Handle the CHECK_SCATTERS state."""
        logger.debug("CHECK_SCATTERS")
        
        # Count all visible scatters
        scatter_count = self._count_scatters()
        self.state.scatters_found = max(self.state.scatters_found, scatter_count)
        
        # Check for free spins trigger
        if scatter_count >= 3 and not self.state.free_spins_triggered:
            self.state.free_spins_triggered = True
            logger.info(f"FREE SPINS TRIGGERED with {scatter_count} scatters!")
        
        # Always proceed to cluster check
        self.state.current_state = GameState.CHECK_CLUSTERS
        
    def _handle_cluster_check(self, rng: SpinRNG, result: CascadeResult):
        """Handle the CHECK_CLUSTERS state."""
        logger.debug("CHECK_CLUSTERS")
        
        # Detect all clusters
        clusters = self.cluster_detector.find_clusters(self.grid)
        
        if clusters:
            # Process wins
            cascade_win = self._process_cluster_wins(clusters, result)
            self.state.total_win += cascade_win
            
            # Track cluster EWs before removal
            self.explosion_system.track_cluster_ews(clusters, self.grid)
            
            # Remove winning symbols
            for cluster in clusters:
                for pos in cluster.positions:
                    self.grid.set_symbol(pos[0], pos[1], Symbol.EMPTY)
            
            # Spawn wilds
            spawns = self.wild_spawner.spawn_wilds_for_clusters(self.grid, clusters, rng)
            for spawn in spawns:
                if spawn.success and spawn.wild_type == Symbol.E_WILD:
                    self.explosion_system.track_spawned_ew(spawn.spawned_position)
            
            # Apply gravity
            self.grid.apply_gravity()
            
            # Increment multiplier and cascade count
            self.state.multiplier = self.state.multiplier.next_level()
            self.state.cascade_count += 1
            
            # Loop back to reel drop
            self.state.current_state = GameState.REEL_DROP
        else:
            # No clusters - check for explosions
            self.state.current_state = GameState.CHECK_EXPLOSIONS
            
    def _handle_explosion_check(self, result: CascadeResult):
        """Handle the CHECK_EXPLOSIONS state."""
        logger.debug("CHECK_EXPLOSIONS")
        
        # Check if explosions should occur
        if self.explosion_system.should_check_explosions(clusters_found=False):
            events = self.explosion_system.execute_explosions(self.grid)
            
            if events:
                logger.info(f"Executed {len(events)} explosions")
                
                # Apply gravity after explosions
                self.grid.apply_gravity()
                
                # Increment multiplier and cascade count
                self.state.multiplier = self.state.multiplier.next_level()
                self.state.cascade_count += 1
                
                # Reset explosion tracking for next cascade
                self.explosion_system.reset_cascade_state()
                
                # Loop back to reel drop
                self.state.current_state = GameState.REEL_DROP
                return
        
        # No explosions - sequence complete
        self.state.current_state = GameState.SEQUENCE_COMPLETE
        
    def _fill_grid(self, rng: SpinRNG, force_enrico: bool = False):
        """Fill the entire grid with new symbols."""
        # Choose weights based on game mode
        if self.state.is_free_spins:
            symbols = FS_SYMBOL_NAMES
            weights = FS_WEIGHTS
        else:
            symbols = BG_SYMBOL_NAMES
            weights = BG_WEIGHTS
            
        # Fill all positions
        for row in range(ROWS):
            for col in range(COLS):
                symbol_name = rng.weighted_choice_numpy(symbols, weights)
                symbol = Symbol[symbol_name]
                self.grid.set_symbol(row, col, symbol)
        
        # Handle "The Enrico Show" - force one EW
        if force_enrico and not self.state.is_free_spins:
            row = rng.randint(0, ROWS - 1)
            col = rng.randint(0, COLS - 1)
            self.grid.set_symbol(row, col, Symbol.E_WILD)
            logger.info(f"The Enrico Show! EW forced at ({row}, {col})")
            
    def _fill_empty_positions(self, rng: SpinRNG):
        """Fill only empty positions with new symbols."""
        # Choose weights based on game mode
        if self.state.is_free_spins:
            symbols = FS_SYMBOL_NAMES
            weights = FS_WEIGHTS
        else:
            symbols = BG_SYMBOL_NAMES
            weights = BG_WEIGHTS
            
        # Fill empty positions
        filled_count = 0
        for row in range(ROWS):
            for col in range(COLS):
                if self.grid.get_symbol(row, col) == Symbol.EMPTY:
                    symbol_name = rng.weighted_choice_numpy(symbols, weights)
                    symbol = Symbol[symbol_name]
                    self.grid.set_symbol(row, col, symbol)
                    filled_count += 1
                    
        logger.debug(f"Filled {filled_count} empty positions")
        
    def _count_scatters(self) -> int:
        """Count all visible scatter symbols."""
        count = 0
        for row in range(ROWS):
            for col in range(COLS):
                if is_scatter(self.grid.get_symbol(row, col)):
                    count += 1
        return count
        
    def _process_cluster_wins(self, clusters: List[Cluster], result: CascadeResult) -> int:
        """
        Process all cluster wins and return total win amount.
        
        Args:
            clusters: List of winning clusters
            result: Cascade result to update
            
        Returns:
            Total win amount for this cascade
        """
        cascade_win = 0
        
        for cluster in clusters:
            # Get base payout for cluster
            symbol_key = cluster.symbol.name
            cluster_size = min(cluster.size, 15)  # Cap at 15
            
            if symbol_key in CLUSTER_PAYS and cluster_size >= 5:
                base_pay = CLUSTER_PAYS[symbol_key][cluster_size - 5]
                win_amount = base_pay * self.state.bet_amount * self.state.multiplier.value
                cascade_win += win_amount
                
                # Record win details
                result.win_details.append({
                    'cascade': self.state.cascade_count,
                    'symbol': symbol_key,
                    'size': cluster_size,
                    'base_pay': base_pay,
                    'multiplier': self.state.multiplier.value,
                    'win': win_amount
                })
                
                logger.info(
                    f"Cluster win: {symbol_key} x{cluster_size} = "
                    f"{base_pay} x {self.state.multiplier.value}x = {win_amount}"
                )
                
        return cascade_win
        
    def get_grid_state(self) -> List[List[str]]:
        """Get current grid state for display."""
        return self.grid.get_display_grid()
        
    def get_current_multiplier(self) -> int:
        """Get current multiplier value."""
        return self.state.multiplier.value
        
    def get_total_win(self) -> int:
        """Get total win amount."""
        return self.state.total_win