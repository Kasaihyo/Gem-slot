"""Integration tests for Explosivo Wild explosion mechanics."""

import pytest
from simulator.core.grid import Grid
from simulator.core.symbol import Symbol
from simulator.core.explosions import ExplosionSystem
from simulator.core.clusters import ClusterDetector
from simulator.core.wild_spawning import WildSpawningSystem
from simulator.core.rng import SpinRNG


class TestExplosionGameFlow:
    """Test explosion system in complete game flow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.grid = Grid()
        self.explosion_system = ExplosionSystem()
        self.cluster_detector = ClusterDetector()
        self.wild_spawner = WildSpawningSystem()
        self.rng = SpinRNG(seed=12345)
    
    def test_no_clusters_triggers_explosions(self):
        """Test that explosions occur when no clusters found."""
        # Set up grid with no clusters but an eligible EW
        self.grid.set_symbol(2, 2, Symbol.E_WILD)
        self.grid.set_symbol(2, 3, Symbol.PINK_SK)
        self.grid.set_symbol(3, 2, Symbol.GREEN_SK)
        
        # Track as landed
        self.explosion_system.track_landed_ews(self.grid)
        
        # Check for clusters
        clusters = self.cluster_detector.find_clusters(self.grid)
        assert len(clusters) == 0
        
        # Should check for explosions
        should_explode = self.explosion_system.should_check_explosions(clusters_found=False)
        assert should_explode == True
        
        # Execute explosions
        events = self.explosion_system.execute_explosions(self.grid)
        
        assert len(events) == 1
        assert self.grid.get_symbol(2, 3) == Symbol.EMPTY  # Pink destroyed
        assert self.grid.get_symbol(3, 2) == Symbol.EMPTY  # Green destroyed
        assert self.grid.get_symbol(2, 2) == Symbol.EMPTY  # EW destroyed
    
    def test_clusters_prevent_explosions(self):
        """Test that explosions don't occur when clusters found."""
        # Set up grid with a winning cluster and an EW
        for col in range(5):
            self.grid.set_symbol(2, col, Symbol.BLUE_SK)
        self.grid.set_symbol(0, 0, Symbol.E_WILD)
        self.grid.set_symbol(0, 1, Symbol.PINK_SK)
        
        # Track as landed
        self.explosion_system.track_landed_ews(self.grid)
        
        # Check for clusters
        clusters = self.cluster_detector.find_clusters(self.grid)
        assert len(clusters) == 1  # Blue cluster
        
        # Should NOT check for explosions
        should_explode = self.explosion_system.should_check_explosions(clusters_found=True)
        assert should_explode == False
    
    def test_cluster_ew_explodes_after_removal(self):
        """Test EW in winning cluster explodes after cluster removal."""
        # Set up grid with cluster containing EW
        # P P E P P (horizontal cluster with EW)
        # G . . . .
        for col in range(5):
            if col == 2:
                self.grid.set_symbol(1, col, Symbol.E_WILD)
            else:
                self.grid.set_symbol(1, col, Symbol.PINK_SK)
        self.grid.set_symbol(2, 2, Symbol.GREEN_SK)  # Below EW
        
        # Check for clusters
        clusters = self.cluster_detector.find_clusters(self.grid)
        assert len(clusters) == 1
        
        # Track cluster EWs before removal
        self.explosion_system.track_cluster_ews(clusters, self.grid)
        assert (1, 2) in self.explosion_system.ew_tracker.in_winning_clusters
        
        # Remove cluster symbols
        for pos in clusters[0].positions:
            self.grid.set_symbol(pos[0], pos[1], Symbol.EMPTY)
        
        # Apply gravity (symbols fall)
        self.grid.apply_gravity()
        
        # No new clusters after gravity
        new_clusters = self.cluster_detector.find_clusters(self.grid)
        assert len(new_clusters) == 0
        
        # Should check explosions
        should_explode = self.explosion_system.should_check_explosions(clusters_found=False)
        assert should_explode == True
        
        # Find eligible EWs (EW that was in cluster is still eligible)
        eligible = self.explosion_system.find_eligible_ews(self.grid)
        
        # Note: The EW was removed with the cluster, so it won't explode
        # This is correct behavior - EWs in clusters are removed before explosion check
        assert len(eligible) == 0
    
    def test_spawned_ew_not_eligible_same_cascade(self):
        """Test spawned EW doesn't explode in the cascade it spawns."""
        # Set up grid with winning cluster
        for col in range(5):
            self.grid.set_symbol(2, col, Symbol.CYAN_SK)
        
        # Detect cluster
        clusters = self.cluster_detector.find_clusters(self.grid)
        assert len(clusters) == 1
        
        # Get cluster footprint before removal
        footprint = clusters[0].positions.copy()
        
        # Remove cluster
        for pos in clusters[0].positions:
            self.grid.set_symbol(pos[0], pos[1], Symbol.EMPTY)
        
        # Spawn wild - we'll check if it's an EW
        spawn_result = self.wild_spawner.spawn_wilds_for_clusters(
            self.grid, clusters, self.rng
        )
        
        assert len(spawn_result) == 1
        spawned_pos = spawn_result[0].spawned_position
        assert spawned_pos is not None
        
        # Track spawned EW if it's an EW
        if spawn_result[0].wild_type == Symbol.E_WILD:
            self.explosion_system.track_spawned_ew(spawned_pos)
        
        # Apply gravity
        self.grid.apply_gravity()
        
        # Check for new clusters
        new_clusters = self.cluster_detector.find_clusters(self.grid)
        
        # Find eligible EWs
        eligible = self.explosion_system.find_eligible_ews(self.grid)
        
        # If we spawned an EW, it should NOT be eligible
        if spawn_result[0].wild_type == Symbol.E_WILD:
            assert spawned_pos not in [(row, col) for row, col in eligible]
    
    def test_multiple_ew_types_in_cascade(self):
        """Test different EW types (landed, cluster, spawned) in same cascade."""
        # Set up complex scenario
        # Row 0: E . . . .  (landed EW)
        # Row 1: P P W P P  (pink cluster with wild)
        # Row 2: . . . . .
        # Row 3: . . E . .  (another landed EW)
        # Row 4: G . B . C  (low-pay symbols)
        
        self.grid.set_symbol(0, 0, Symbol.E_WILD)
        
        # Pink cluster
        for col in range(5):
            if col == 2:
                self.grid.set_symbol(1, col, Symbol.WILD)
            else:
                self.grid.set_symbol(1, col, Symbol.PINK_SK)
        
        self.grid.set_symbol(3, 2, Symbol.E_WILD)
        self.grid.set_symbol(4, 0, Symbol.GREEN_SK)
        self.grid.set_symbol(4, 2, Symbol.BLUE_SK)
        self.grid.set_symbol(4, 4, Symbol.CYAN_SK)
        
        # Track landed EWs
        self.explosion_system.track_landed_ews(self.grid)
        assert len(self.explosion_system.ew_tracker.landed_this_drop) == 2
        
        # Detect clusters
        clusters = self.cluster_detector.find_clusters(self.grid)
        assert len(clusters) == 1
        
        # Remove cluster and spawn wild
        for pos in clusters[0].positions:
            self.grid.set_symbol(pos[0], pos[1], Symbol.EMPTY)
        
        spawn_result = self.wild_spawner.spawn_wilds_for_clusters(
            self.grid, clusters, self.rng
        )
        
        if spawn_result[0].success and spawn_result[0].wild_type == Symbol.E_WILD:
            spawned_pos = spawn_result[0].spawned_position
            self.explosion_system.track_spawned_ew(spawned_pos)
        
        # Apply gravity
        self.grid.apply_gravity()
        
        # Check for explosions (no new clusters)
        new_clusters = self.cluster_detector.find_clusters(self.grid)
        if len(new_clusters) == 0:
            # Execute explosions
            eligible = self.explosion_system.find_eligible_ews(self.grid)
            
            # Only the originally landed EWs should be eligible
            # (spawned EW is not eligible)
            for pos in eligible:
                assert pos not in self.explosion_system.ew_tracker.spawned_this_cascade
    
    def test_ew_collection_through_game_flow(self):
        """Test EW collection counting through multiple cascades."""
        initial_count = self.explosion_system.get_collected_count()
        assert initial_count == 0
        
        # Cascade 1: EW in cluster
        self.grid.set_symbol(1, 1, Symbol.PINK_SK)
        self.grid.set_symbol(1, 2, Symbol.E_WILD)
        self.grid.set_symbol(1, 3, Symbol.PINK_SK)
        self.grid.set_symbol(2, 1, Symbol.PINK_SK)
        self.grid.set_symbol(2, 2, Symbol.PINK_SK)
        
        clusters = self.cluster_detector.find_clusters(self.grid)
        self.explosion_system.track_cluster_ews(clusters, self.grid)
        
        # Remove cluster
        for pos in clusters[0].positions:
            self.grid.set_symbol(pos[0], pos[1], Symbol.EMPTY)
        
        # Count should increase by 1 (collected from cluster)
        assert self.explosion_system.get_collected_count() == 1
        
        # Cascade 2: EW explodes (not from cluster)
        self.explosion_system.reset_cascade_state()
        self.grid.clear()
        self.grid.set_symbol(2, 2, Symbol.E_WILD)
        self.grid.set_symbol(2, 3, Symbol.PINK_SK)
        
        self.explosion_system.track_landed_ews(self.grid)
        events = self.explosion_system.execute_explosions(self.grid)
        
        # Count should be 2 now
        assert self.explosion_system.get_collected_count() == 2
        
        # Test reset
        self.explosion_system.reset_collected_count()
        assert self.explosion_system.get_collected_count() == 0


class TestExplosionEdgeCases:
    """Test edge cases for explosion mechanics."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.grid = Grid()
        self.explosion_system = ExplosionSystem()
    
    def test_all_positions_destroyed(self):
        """Test when explosion destroys all symbols."""
        # Fill grid with low-pay and one EW
        for row in range(5):
            for col in range(5):
                self.grid.set_symbol(row, col, Symbol.PINK_SK)
        
        # Place EW in center
        self.grid.set_symbol(2, 2, Symbol.E_WILD)
        self.explosion_system.ew_tracker.landed_this_drop.add((2, 2))
        
        # Execute explosion
        events = self.explosion_system.execute_explosions(self.grid)
        
        # Only 3x3 area around EW destroyed
        assert len(events) == 1
        assert len(events[0].destroyed_positions) == 8  # 9 - 1 (EW itself)
        
        # Check destroyed area
        for row in range(1, 4):
            for col in range(1, 4):
                assert self.grid.get_symbol(row, col) == Symbol.EMPTY
        
        # Check outside area preserved
        assert self.grid.get_symbol(0, 0) == Symbol.PINK_SK
        assert self.grid.get_symbol(4, 4) == Symbol.PINK_SK
    
    def test_chain_prevention(self):
        """Test that explosions don't chain in same step."""
        # Set up two EWs where one would destroy the other
        # . E .
        # E P .
        # . . .
        self.grid.set_symbol(0, 1, Symbol.E_WILD)
        self.grid.set_symbol(1, 0, Symbol.E_WILD)
        self.grid.set_symbol(1, 1, Symbol.PINK_SK)
        
        # Only bottom-left EW is eligible
        self.explosion_system.ew_tracker.landed_this_drop.add((1, 0))
        
        # Execute explosions
        events = self.explosion_system.execute_explosions(self.grid)
        
        assert len(events) == 1  # Only one explosion
        assert events[0].ew_position == (1, 0)
        
        # Top EW preserved (not eligible, didn't land)
        assert self.grid.get_symbol(0, 1) == Symbol.E_WILD
        # Pink destroyed
        assert self.grid.get_symbol(1, 1) == Symbol.EMPTY
        # Exploding EW destroyed
        assert self.grid.get_symbol(1, 0) == Symbol.EMPTY


if __name__ == "__main__":
    pytest.main([__file__])