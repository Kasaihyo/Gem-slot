"""Integration tests for the complete avalanche system."""

import pytest
from simulator.core.avalanche import AvalancheSystem, GameState, MultiplierLevel
from simulator.core.symbol import Symbol
from simulator.core.rng import SpinRNG


class TestCompleteGameFlow:
    """Test complete game flows from start to finish."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.system = AvalancheSystem()
        self.rng = SpinRNG(seed=42)
        
    def test_simple_spin_no_wins(self):
        """Test a spin with no wins."""
        # Instead of relying on RNG, set up a grid with no possible wins
        self.system.reset()
        
        # Create alternating pattern that can't form clusters
        for row in range(5):
            for col in range(5):
                if (row + col) % 2 == 0:
                    self.system.grid.set_symbol(row, col, Symbol.PINK_SK)
                else:
                    self.system.grid.set_symbol(row, col, Symbol.BLUE_SK)
                    
        # Start from cluster check to skip initial fill
        self.system.state.current_state = GameState.CHECK_CLUSTERS
        self.system.state.is_initial_drop = False
        
        result = self.system.play_spin(self.rng)
        
        # Verify no wins
        assert result.total_cascades == 0  # No winning cascades
        assert result.max_multiplier_reached == 1  # Never increased
        assert result.total_win == 0
        assert not result.max_win_reached
        
        # Verify state progression (we started from CHECK_CLUSTERS)
        assert GameState.CHECK_CLUSTERS in result.state_history
        assert GameState.CHECK_EXPLOSIONS in result.state_history
        
    def test_cascade_with_wild_spawn(self):
        """Test cascade that spawns a wild."""
        self.system.reset()
        
        # Manually set up a winning cluster
        for col in range(5):
            self.system.grid.set_symbol(2, col, Symbol.ORANGE_SK)
            
        # Fill rest to avoid additional wins
        for row in range(5):
            for col in range(5):
                if row != 2:
                    self.system.grid.set_symbol(row, col, Symbol.SCATTER)
                    
        # Play from cluster check
        self.system.state.current_state = GameState.CHECK_CLUSTERS
        self.system.state.is_initial_drop = False
        
        result = self.system.play_spin(self.rng)
        
        # Should have one cascade
        assert result.total_cascades == 1
        assert result.max_multiplier_reached == 2
        assert result.total_win > 0
        
        # Check that wild was spawned (grid should have a wild or EW)
        wild_found = False
        for row in range(5):
            for col in range(5):
                symbol = self.system.grid.get_symbol(row, col)
                if symbol in [Symbol.WILD, Symbol.E_WILD]:
                    wild_found = True
                    break
                    
        assert wild_found
        
    def test_explosion_cascade_chain(self):
        """Test cascade triggered by explosion."""
        self.system.reset()
        
        # Set up EW with destructible symbols that will cascade
        # E P P P P  (EW will destroy pinks, creating space)
        # G . . . .  (Green will fall and potentially form cluster)
        # G . . . .
        # G . . . .
        # G . . . .
        self.system.grid.set_symbol(0, 0, Symbol.E_WILD)
        for col in range(1, 5):
            self.system.grid.set_symbol(0, col, Symbol.PINK_SK)
            
        for row in range(1, 5):
            self.system.grid.set_symbol(row, 0, Symbol.GREEN_SK)
            
        # Fill rest with scatters (non-clustering)
        for row in range(1, 5):
            for col in range(1, 5):
                self.system.grid.set_symbol(row, col, Symbol.SCATTER)
                
        # Track EW as landed
        self.system.explosion_system.track_landed_ews(self.system.grid)
        
        # Start from explosion check
        self.system.state.current_state = GameState.CHECK_EXPLOSIONS
        self.system.state.is_initial_drop = False
        
        result = self.system.play_spin(self.rng)
        
        # Should have at least one cascade from explosion
        assert result.total_cascades >= 1
        assert result.max_multiplier_reached >= 2
        
    def test_free_spins_trigger_flow(self):
        """Test complete flow with free spins trigger."""
        self.system.reset()
        
        # Place exactly 3 scatters
        self.system.grid.set_symbol(0, 0, Symbol.SCATTER)
        self.system.grid.set_symbol(2, 2, Symbol.SCATTER)  
        self.system.grid.set_symbol(4, 4, Symbol.SCATTER)
        
        # Add a small winning cluster
        for col in range(5):
            self.system.grid.set_symbol(3, col, Symbol.CYAN_SK)
            
        # Fill remaining
        for row in range(5):
            for col in range(5):
                if self.system.grid.get_symbol(row, col) == Symbol.EMPTY:
                    self.system.grid.set_symbol(row, col, Symbol.LADY_SK)
                    
        # Play from scatter check
        self.system.state.current_state = GameState.CHECK_SCATTERS
        self.system.state.is_initial_drop = False
        
        result = self.system.play_spin(self.rng)
        
        # Should trigger free spins
        assert result.free_spins_triggered
        assert result.scatters_found == 3
        
        # Should still process the win
        assert result.total_win > 0
        assert len(result.win_details) >= 1
        
    def test_multiplier_progression_through_cascades(self):
        """Test multiplier increases through multiple cascades."""
        self.system.reset()
        
        # We'll manually control cascades to test progression
        # Start with a win
        for col in range(5):
            self.system.grid.set_symbol(0, col, Symbol.BLUE_SK)
            
        # Process first cascade
        self.system.state.current_state = GameState.CHECK_CLUSTERS
        self.system.state.is_initial_drop = False
        
        from simulator.core.avalanche import CascadeResult
        result = CascadeResult()
        
        # First cascade - 1x
        self.system._handle_cluster_check(self.rng, result)
        assert self.system.state.multiplier.value == 2
        assert self.system.state.cascade_count == 1
        
        # Set up another win
        self.system.grid.clear()
        for row in range(5):
            self.system.grid.set_symbol(row, 2, Symbol.PINK_SK)
            
        self.system.state.current_state = GameState.CHECK_CLUSTERS
        
        # Second cascade - 2x
        self.system._handle_cluster_check(self.rng, result)
        assert self.system.state.multiplier.value == 4
        assert self.system.state.cascade_count == 2
        
        # Continue to test full progression
        multipliers = [8, 16, 32, 32]  # Stays at 32
        for i, expected_mult in enumerate(multipliers):
            self.system.grid.clear()
            for col in range(5):
                self.system.grid.set_symbol(1, col, Symbol.GREEN_SK)
                
            self.system.state.current_state = GameState.CHECK_CLUSTERS
            self.system._handle_cluster_check(self.rng, result)
            
            assert self.system.state.multiplier.value == expected_mult
            assert self.system.state.cascade_count == 3 + i


class TestMaxWinScenarios:
    """Test max win cap scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.system = AvalancheSystem()
        self.rng = SpinRNG(seed=12345)
        
    def test_max_win_immediate_termination(self):
        """Test that reaching max win immediately ends the spin."""
        self.system.reset(bet_amount=1000)  # $10 bet
        
        # Set initial win very close to max
        self.system.state.total_win = 7499000  # 7499x
        
        # Set up a small cluster to push over max
        for col in range(5):
            self.system.grid.set_symbol(0, col, Symbol.PINK_SK)
                
        # Process with low multiplier to control the win
        self.system.state.current_state = GameState.CHECK_CLUSTERS
        self.system.state.is_initial_drop = False
        
        result = self.system.play_spin(self.rng)
        
        # Should hit max win
        assert result.max_win_reached
        assert result.total_win == 7500000  # Exactly 7500x
        
    def test_max_win_cancels_features(self):
        """Test that max win cancels pending features."""
        self.system.reset(bet_amount=100)
        
        # Set near max win
        self.system.state.total_win = 749000  # 7490x
        
        # Add scatters for free spins
        self.system.grid.set_symbol(0, 0, Symbol.SCATTER)
        self.system.grid.set_symbol(0, 1, Symbol.SCATTER)
        self.system.grid.set_symbol(0, 2, Symbol.SCATTER)
        
        # Add small win to push over
        for col in range(5):
            self.system.grid.set_symbol(1, col, Symbol.PINK_SK)
            
        # Process
        self.system.state.current_state = GameState.CHECK_SCATTERS
        self.system.state.is_initial_drop = False
        
        result = self.system.play_spin(self.rng)
        
        # Should hit max win
        assert result.max_win_reached
        # Total win should be capped at exactly 7500x
        assert result.total_win <= 750000  # Max 7500x
        # It hit max win, so should be at the cap
        assert result.total_win == 750000  # Exactly 7500x


class TestDeterministicBehavior:
    """Test that the system behaves deterministically."""
    
    def test_same_seed_same_result(self):
        """Test that same seed produces same results."""
        results = []
        
        for _ in range(3):
            system = AvalancheSystem()
            rng = SpinRNG(seed=777)
            system.reset()
            
            result = system.play_spin(rng)
            results.append({
                'total_win': result.total_win,
                'cascades': result.total_cascades,
                'max_mult': result.max_multiplier_reached,
                'scatters': result.scatters_found,
                'fs_triggered': result.free_spins_triggered
            })
            
        # All results should be identical
        for i in range(1, len(results)):
            assert results[i] == results[0]
            
    def test_different_seeds_different_results(self):
        """Test that different seeds produce different results."""
        results = []
        
        for seed in [111, 222, 333]:
            system = AvalancheSystem()
            rng = SpinRNG(seed=seed)
            system.reset()
            
            result = system.play_spin(rng)
            results.append(result.total_cascades)
            
        # Results should vary (extremely unlikely to be all the same)
        assert len(set(results)) > 1


if __name__ == "__main__":
    pytest.main([__file__])