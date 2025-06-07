"""Unit tests for Explosivo Wild explosion mechanics."""

import pytest
from simulator.core.grid import Grid
from simulator.core.symbol import Symbol
from simulator.core.explosions import ExplosionSystem, EWTracker, ExplosionEvent
from simulator.core.clusters import Cluster


class TestEWTracker:
    """Test EW eligibility tracking."""
    
    def test_reset_cascade(self):
        """Test cascade state reset."""
        tracker = EWTracker()
        
        # Add some data
        tracker.landed_this_drop.add((1, 1))
        tracker.in_winning_clusters.add((2, 2))
        tracker.spawned_this_cascade.add((3, 3))
        tracker.collected_count = 5
        
        # Reset cascade
        tracker.reset_cascade()
        
        # Check cascade data cleared but collection count preserved
        assert len(tracker.landed_this_drop) == 0
        assert len(tracker.in_winning_clusters) == 0
        assert len(tracker.spawned_this_cascade) == 0
        assert tracker.collected_count == 5  # Not reset
    
    def test_eligibility_landed_ew(self):
        """Test eligibility for EW that landed this drop."""
        tracker = EWTracker()
        tracker.landed_this_drop.add((1, 1))
        
        assert tracker.is_eligible_to_explode((1, 1)) == True
        assert tracker.is_eligible_to_explode((2, 2)) == False
    
    def test_eligibility_cluster_ew(self):
        """Test eligibility for EW in winning cluster."""
        tracker = EWTracker()
        tracker.in_winning_clusters.add((2, 2))
        
        assert tracker.is_eligible_to_explode((2, 2)) == True
        assert tracker.is_eligible_to_explode((1, 1)) == False
    
    def test_eligibility_spawned_ew(self):
        """Test spawned EWs are never eligible."""
        tracker = EWTracker()
        tracker.landed_this_drop.add((1, 1))
        tracker.spawned_this_cascade.add((1, 1))  # Same position
        
        # Spawned status overrides landed status
        assert tracker.is_eligible_to_explode((1, 1)) == False


class TestExplosionArea:
    """Test explosion area calculation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.system = ExplosionSystem()
    
    def test_center_explosion_area(self):
        """Test 3x3 area in center of grid."""
        area = self.system.calculate_explosion_area((2, 2))
        
        expected = [
            (1, 1), (1, 2), (1, 3),
            (2, 1), (2, 2), (2, 3),
            (3, 1), (3, 2), (3, 3)
        ]
        
        assert sorted(area) == sorted(expected)
        assert len(area) == 9
    
    def test_corner_explosion_area(self):
        """Test 3x3 area at grid corner."""
        # Top-left corner
        area = self.system.calculate_explosion_area((0, 0))
        
        expected = [
            (0, 0), (0, 1),
            (1, 0), (1, 1)
        ]
        
        assert sorted(area) == sorted(expected)
        assert len(area) == 4
    
    def test_edge_explosion_area(self):
        """Test 3x3 area at grid edge."""
        # Bottom edge
        area = self.system.calculate_explosion_area((4, 2))
        
        expected = [
            (3, 1), (3, 2), (3, 3),
            (4, 1), (4, 2), (4, 3)
        ]
        
        assert sorted(area) == sorted(expected)
        assert len(area) == 6


class TestExplosionMechanics:
    """Test core explosion mechanics."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.system = ExplosionSystem()
        self.grid = Grid()
    
    def test_track_landed_ews(self):
        """Test tracking of landed EWs."""
        # Place some EWs
        self.grid.set_symbol(1, 1, Symbol.E_WILD)
        self.grid.set_symbol(3, 3, Symbol.E_WILD)
        self.grid.set_symbol(2, 2, Symbol.WILD)  # Regular wild
        
        self.system.track_landed_ews(self.grid)
        
        assert len(self.system.ew_tracker.landed_this_drop) == 2
        assert (1, 1) in self.system.ew_tracker.landed_this_drop
        assert (3, 3) in self.system.ew_tracker.landed_this_drop
        assert (2, 2) not in self.system.ew_tracker.landed_this_drop
    
    def test_track_cluster_ews(self):
        """Test tracking of EWs in winning clusters."""
        # Set up grid with cluster containing EW
        self.grid.set_symbol(1, 1, Symbol.PINK_SK)
        self.grid.set_symbol(1, 2, Symbol.E_WILD)
        self.grid.set_symbol(1, 3, Symbol.PINK_SK)
        
        # Create cluster
        cluster = Cluster(
            symbol=Symbol.PINK_SK,
            positions=[(1, 1), (1, 2), (1, 3)],
            size=3
        )
        
        self.system.track_cluster_ews([cluster], self.grid)
        
        assert len(self.system.ew_tracker.in_winning_clusters) == 1
        assert (1, 2) in self.system.ew_tracker.in_winning_clusters
    
    def test_find_eligible_ews(self):
        """Test finding eligible EWs."""
        # Place EWs
        self.grid.set_symbol(1, 1, Symbol.E_WILD)
        self.grid.set_symbol(2, 2, Symbol.E_WILD)
        self.grid.set_symbol(3, 3, Symbol.E_WILD)
        
        # Track different types
        self.system.ew_tracker.landed_this_drop.add((1, 1))
        self.system.ew_tracker.in_winning_clusters.add((2, 2))
        self.system.ew_tracker.spawned_this_cascade.add((3, 3))
        
        eligible = self.system.find_eligible_ews(self.grid)
        
        assert len(eligible) == 2
        assert (1, 1) in eligible  # Landed
        assert (2, 2) in eligible  # From cluster
        assert (3, 3) not in eligible  # Spawned
    
    def test_basic_explosion(self):
        """Test basic explosion destroying low-pay symbols."""
        # Set up grid with EW surrounded by symbols
        # . P .
        # G E B
        # . O .
        self.grid.set_symbol(0, 1, Symbol.PINK_SK)
        self.grid.set_symbol(1, 0, Symbol.GREEN_SK)
        self.grid.set_symbol(1, 1, Symbol.E_WILD)
        self.grid.set_symbol(1, 2, Symbol.BLUE_SK)
        self.grid.set_symbol(2, 1, Symbol.ORANGE_SK)
        
        # Track as landed
        self.system.ew_tracker.landed_this_drop.add((1, 1))
        
        # Execute explosion
        events = self.system.execute_explosions(self.grid)
        
        assert len(events) == 1
        event = events[0]
        
        # Check destroyed positions
        assert len(event.destroyed_positions) == 4
        assert (0, 1) in event.destroyed_positions
        assert (1, 0) in event.destroyed_positions
        assert (1, 2) in event.destroyed_positions
        assert (2, 1) in event.destroyed_positions
        
        # Check grid state
        assert self.grid.get_symbol(0, 1) == Symbol.EMPTY
        assert self.grid.get_symbol(1, 0) == Symbol.EMPTY
        assert self.grid.get_symbol(1, 1) == Symbol.EMPTY  # EW also destroyed
        assert self.grid.get_symbol(1, 2) == Symbol.EMPTY
        assert self.grid.get_symbol(2, 1) == Symbol.EMPTY
    
    def test_explosion_preserves_special_symbols(self):
        """Test explosion preserves high-pay, wilds, scatters."""
        # Set up grid with mixed symbols
        # L W S
        # P E B
        # E C L
        self.grid.set_symbol(0, 0, Symbol.LADY_SK)  # High-pay
        self.grid.set_symbol(0, 1, Symbol.WILD)     # Wild
        self.grid.set_symbol(0, 2, Symbol.SCATTER)  # Scatter
        self.grid.set_symbol(1, 0, Symbol.PINK_SK)  # Low-pay
        self.grid.set_symbol(1, 1, Symbol.E_WILD)   # Exploding EW
        self.grid.set_symbol(1, 2, Symbol.BLUE_SK)  # Low-pay
        self.grid.set_symbol(2, 0, Symbol.E_WILD)   # Another EW
        self.grid.set_symbol(2, 1, Symbol.CYAN_SK)  # Low-pay
        self.grid.set_symbol(2, 2, Symbol.LADY_SK)  # High-pay
        
        # Track as landed
        self.system.ew_tracker.landed_this_drop.add((1, 1))
        
        # Execute explosion
        events = self.system.execute_explosions(self.grid)
        
        # Check preserved symbols
        assert self.grid.get_symbol(0, 0) == Symbol.LADY_SK  # High-pay preserved
        assert self.grid.get_symbol(0, 1) == Symbol.WILD     # Wild preserved
        assert self.grid.get_symbol(0, 2) == Symbol.SCATTER  # Scatter preserved
        assert self.grid.get_symbol(2, 0) == Symbol.E_WILD   # Other EW preserved
        assert self.grid.get_symbol(2, 2) == Symbol.LADY_SK  # High-pay preserved
        
        # Check destroyed symbols
        assert self.grid.get_symbol(1, 0) == Symbol.EMPTY  # Low-pay destroyed
        assert self.grid.get_symbol(1, 2) == Symbol.EMPTY  # Low-pay destroyed
        assert self.grid.get_symbol(2, 1) == Symbol.EMPTY  # Low-pay destroyed
    
    def test_multiple_simultaneous_explosions(self):
        """Test multiple EWs exploding simultaneously."""
        # Set up grid with two EWs
        # E P . . E
        # C . . . G
        # . . . . .
        # . . . . .
        # . . . . .
        self.grid.set_symbol(0, 0, Symbol.E_WILD)
        self.grid.set_symbol(0, 1, Symbol.PINK_SK)
        self.grid.set_symbol(0, 4, Symbol.E_WILD)
        self.grid.set_symbol(1, 0, Symbol.CYAN_SK)
        self.grid.set_symbol(1, 4, Symbol.GREEN_SK)
        
        # Track both as landed
        self.system.ew_tracker.landed_this_drop.add((0, 0))
        self.system.ew_tracker.landed_this_drop.add((0, 4))
        
        # Execute explosions
        events = self.system.execute_explosions(self.grid)
        
        assert len(events) == 2
        
        # Check all affected low-pay symbols destroyed
        assert self.grid.get_symbol(0, 1) == Symbol.EMPTY  # Pink destroyed
        assert self.grid.get_symbol(1, 0) == Symbol.EMPTY  # Cyan destroyed
        assert self.grid.get_symbol(1, 4) == Symbol.EMPTY  # Green destroyed
        
        # Both EWs destroyed
        assert self.grid.get_symbol(0, 0) == Symbol.EMPTY
        assert self.grid.get_symbol(0, 4) == Symbol.EMPTY
    
    def test_overlapping_explosions(self):
        """Test overlapping explosion areas."""
        # Set up grid with adjacent EWs
        # . P .
        # E . E
        # . G .
        self.grid.set_symbol(0, 1, Symbol.PINK_SK)
        self.grid.set_symbol(1, 0, Symbol.E_WILD)
        self.grid.set_symbol(1, 2, Symbol.E_WILD)
        self.grid.set_symbol(2, 1, Symbol.GREEN_SK)
        
        # Track both as landed
        self.system.ew_tracker.landed_this_drop.add((1, 0))
        self.system.ew_tracker.landed_this_drop.add((1, 2))
        
        # Execute explosions
        events = self.system.execute_explosions(self.grid)
        
        assert len(events) == 2
        
        # Center position should only be destroyed once
        assert self.grid.get_symbol(0, 1) == Symbol.EMPTY
        assert self.grid.get_symbol(2, 1) == Symbol.EMPTY
        
        # Both EWs destroyed
        assert self.grid.get_symbol(1, 0) == Symbol.EMPTY
        assert self.grid.get_symbol(1, 2) == Symbol.EMPTY
    
    def test_ew_collection_tracking(self):
        """Test EW collection for free spins."""
        # Set up grid with cluster EW and landed EW
        self.grid.set_symbol(1, 1, Symbol.E_WILD)
        self.grid.set_symbol(3, 3, Symbol.E_WILD)
        
        # Create a fake cluster for the first EW
        from simulator.core.clusters import Cluster
        cluster = Cluster(
            symbol=Symbol.PINK_SK,
            positions=[(1, 0), (1, 1), (1, 2)],  # Include the EW position
            size=3
        )
        
        # Track cluster EW properly (this will increment collected count)
        self.system.track_cluster_ews([cluster], self.grid)
        
        # Track the other as landed
        self.system.ew_tracker.landed_this_drop.add((3, 3))
        
        # Execute explosions
        events = self.system.execute_explosions(self.grid)
        
        # Both should be collected (1 from cluster tracking + 1 from explosion)
        assert self.system.get_collected_count() == 2
        
        # Check event tracking
        assert events[0].from_cluster == True or events[1].from_cluster == True
        assert events[0].from_cluster == False or events[1].from_cluster == False


class TestExplosionIntegration:
    """Test explosion system integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.system = ExplosionSystem()
        self.grid = Grid()
    
    def test_should_check_explosions(self):
        """Test explosion check conditions."""
        # Should check when no clusters found
        assert self.system.should_check_explosions(clusters_found=False) == True
        
        # Should not check when clusters found
        assert self.system.should_check_explosions(clusters_found=True) == False
    
    def test_cascade_flow(self):
        """Test full cascade flow with explosions."""
        # Set up initial grid state
        self.grid.set_symbol(2, 2, Symbol.E_WILD)
        self.grid.set_symbol(2, 3, Symbol.PINK_SK)
        
        # Track landed EW
        self.system.track_landed_ews(self.grid)
        
        # No clusters found - should check explosions
        assert self.system.should_check_explosions(clusters_found=False) == True
        
        # Execute explosions
        events = self.system.execute_explosions(self.grid)
        
        assert len(events) == 1
        assert self.grid.get_symbol(2, 3) == Symbol.EMPTY
        
        # Reset for next cascade
        self.system.reset_cascade_state()
        
        # Verify state cleared
        assert len(self.system.ew_tracker.landed_this_drop) == 0
        assert len(self.system.ew_tracker.in_winning_clusters) == 0
    
    def test_prd_example(self):
        """Test the example from PRD documentation."""
        # Set up exact grid from PRD
        # Row 0
        self.grid.set_symbol(0, 0, Symbol.PINK_SK)
        self.grid.set_symbol(0, 1, Symbol.BLUE_SK)
        self.grid.set_symbol(0, 2, Symbol.CYAN_SK)
        self.grid.set_symbol(0, 3, Symbol.GREEN_SK)
        self.grid.set_symbol(0, 4, Symbol.LADY_SK)
        
        # Row 1
        self.grid.set_symbol(1, 0, Symbol.LADY_SK)
        self.grid.set_symbol(1, 1, Symbol.ORANGE_SK)
        self.grid.set_symbol(1, 2, Symbol.GREEN_SK)
        self.grid.set_symbol(1, 3, Symbol.BLUE_SK)
        self.grid.set_symbol(1, 4, Symbol.ORANGE_SK)
        
        # Row 2
        self.grid.set_symbol(2, 0, Symbol.CYAN_SK)
        self.grid.set_symbol(2, 1, Symbol.PINK_SK)
        self.grid.set_symbol(2, 2, Symbol.WILD)
        self.grid.set_symbol(2, 3, Symbol.CYAN_SK)
        self.grid.set_symbol(2, 4, Symbol.GREEN_SK)
        
        # Row 3
        self.grid.set_symbol(3, 0, Symbol.BLUE_SK)
        self.grid.set_symbol(3, 1, Symbol.GREEN_SK)
        self.grid.set_symbol(3, 2, Symbol.E_WILD)
        self.grid.set_symbol(3, 3, Symbol.BLUE_SK)
        self.grid.set_symbol(3, 4, Symbol.LADY_SK)
        
        # Row 4
        self.grid.set_symbol(4, 0, Symbol.SCATTER)
        self.grid.set_symbol(4, 1, Symbol.CYAN_SK)
        self.grid.set_symbol(4, 2, Symbol.GREEN_SK)
        self.grid.set_symbol(4, 3, Symbol.SCATTER)
        self.grid.set_symbol(4, 4, Symbol.ORANGE_SK)
        
        # Track EW as landed
        self.system.ew_tracker.landed_this_drop.add((3, 2))
        
        # Execute explosion
        events = self.system.execute_explosions(self.grid)
        
        assert len(events) == 1
        event = events[0]
        
        # Verify correct positions destroyed
        # From PRD: PNK & CYN at (2,1) and (2,3) destroyed
        assert self.grid.get_symbol(2, 1) == Symbol.EMPTY  # Pink destroyed
        assert self.grid.get_symbol(2, 3) == Symbol.EMPTY  # Cyan destroyed
        
        # From PRD: GRN & BLU at (3,1) and (3,3) destroyed
        assert self.grid.get_symbol(3, 1) == Symbol.EMPTY  # Green destroyed
        assert self.grid.get_symbol(3, 3) == Symbol.EMPTY  # Blue destroyed
        
        # From PRD: CYN & GRN at (4,1) and (4,2) destroyed
        assert self.grid.get_symbol(4, 1) == Symbol.EMPTY  # Cyan destroyed
        assert self.grid.get_symbol(4, 2) == Symbol.EMPTY  # Green destroyed
        
        # From PRD: WLD at (2,2), LDY at (3,4), and SCR at (4,3) survive
        assert self.grid.get_symbol(2, 2) == Symbol.WILD     # Wild preserved
        assert self.grid.get_symbol(3, 4) == Symbol.LADY_SK  # Lady preserved
        assert self.grid.get_symbol(4, 3) == Symbol.SCATTER  # Scatter preserved
        
        # EW itself destroyed
        assert self.grid.get_symbol(3, 2) == Symbol.EMPTY


if __name__ == "__main__":
    pytest.main([__file__])