"""
Integration tests for wild spawning system.

This demonstrates how wild spawning integrates with cluster detection
and grid mechanics in the game flow.
"""

import unittest
from simulator.core.wild_spawning import WildSpawningSystem
from simulator.core.grid import Grid
from simulator.core.clusters import ClusterDetector
from simulator.core.symbol import Symbol
from simulator.core.rng import SpinRNG


class TestWildSpawningIntegration(unittest.TestCase):
    """Integration tests for wild spawning with other game systems."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wild_system = WildSpawningSystem()
        self.cluster_detector = ClusterDetector()
        self.rng = SpinRNG(seed=42)
    
    def test_full_game_flow_integration(self):
        """Test wild spawning in a complete game flow scenario."""
        # Step 1: Create a grid with winning clusters
        grid = Grid()
        
        # Create a Pink cluster (5 symbols)
        grid.set_symbol(0, 0, Symbol.PINK_SK)
        grid.set_symbol(0, 1, Symbol.PINK_SK)
        grid.set_symbol(1, 0, Symbol.PINK_SK)
        grid.set_symbol(1, 1, Symbol.PINK_SK)
        grid.set_symbol(2, 0, Symbol.PINK_SK)
        
        # Create a Blue cluster (5 symbols)
        grid.set_symbol(2, 3, Symbol.BLUE_SK)
        grid.set_symbol(2, 4, Symbol.BLUE_SK)
        grid.set_symbol(3, 3, Symbol.BLUE_SK)
        grid.set_symbol(3, 4, Symbol.BLUE_SK)
        grid.set_symbol(4, 3, Symbol.BLUE_SK)
        
        # Add some other symbols
        grid.set_symbol(0, 3, Symbol.GREEN_SK)
        grid.set_symbol(1, 3, Symbol.ORANGE_SK)
        grid.set_symbol(4, 0, Symbol.SCATTER)
        
        print("\nInitial Grid:")
        print(grid.to_string())
        
        # Step 2: Detect winning clusters
        clusters = self.cluster_detector.find_clusters(grid)
        self.assertEqual(len(clusters), 2)
        
        print(f"\nFound {len(clusters)} winning clusters:")
        for cluster in clusters:
            print(f"  - {cluster}")
        
        # Step 3: Store cluster footprints before removal
        cluster_footprints = [cluster.positions.copy() for cluster in clusters]
        
        # Step 4: Remove winning symbols
        winning_positions = self.cluster_detector.get_winning_positions(clusters)
        grid.remove_positions(winning_positions)
        
        print("\nGrid after removing winning clusters:")
        print(grid.to_string())
        
        # Step 5: Spawn wilds (BEFORE gravity)
        spawn_results = self.wild_system.spawn_wilds_for_clusters(grid, clusters, self.rng)
        
        print("\nWild spawning results:")
        for spawn in spawn_results:
            if spawn.success:
                print(f"  - Spawned {spawn.wild_type.name} at {spawn.spawned_position}")
            else:
                print(f"  - Failed to spawn for cluster {spawn.cluster_id}")
        
        # Verify spawns
        self.assertEqual(len(spawn_results), 2)
        for spawn in spawn_results:
            self.assertTrue(spawn.success)
        
        print("\nGrid after wild spawning:")
        print(grid.to_string())
        
        # Step 6: Apply gravity (spawned wilds should fall)
        moved = grid.apply_gravity()
        self.assertTrue(moved)
        
        print("\nGrid after gravity:")
        print(grid.to_string())
        
        # Verify wild positions after gravity
        wild_count = grid.count_symbol(Symbol.WILD)
        ew_count = grid.count_symbol(Symbol.E_WILD)
        total_wilds = wild_count + ew_count
        self.assertEqual(total_wilds, 2)  # One wild per cluster
    
    def test_wild_with_existing_wild_cluster(self):
        """Test wild spawning when cluster already contains a wild."""
        grid = Grid()
        
        # Create a cluster with a wild in it
        grid.set_symbol(0, 0, Symbol.PINK_SK)
        grid.set_symbol(0, 1, Symbol.WILD)  # Wild in cluster
        grid.set_symbol(1, 0, Symbol.PINK_SK)
        grid.set_symbol(1, 1, Symbol.PINK_SK)
        grid.set_symbol(2, 0, Symbol.PINK_SK)
        
        # Detect cluster (should include the wild)
        clusters = self.cluster_detector.find_clusters(grid)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0].size, 5)
        
        # Remove winning positions
        winning_positions = self.cluster_detector.get_winning_positions(clusters)
        grid.remove_positions(winning_positions)
        
        # Spawn new wild
        spawn_results = self.wild_system.spawn_wilds_for_clusters(grid, clusters, self.rng)
        
        self.assertEqual(len(spawn_results), 1)
        self.assertTrue(spawn_results[0].success)
        
        # Should have exactly one wild on grid
        total_wilds = grid.count_symbol(Symbol.WILD) + grid.count_symbol(Symbol.E_WILD)
        self.assertEqual(total_wilds, 1)
    
    def test_spawned_ew_marking(self):
        """Test that spawned EWs can be properly marked for non-explosion."""
        grid = Grid()
        
        # Create a simple cluster
        positions = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]
        for row, col in positions:
            grid.set_symbol(row, col, Symbol.PINK_SK)
        
        # Detect and remove cluster
        clusters = self.cluster_detector.find_clusters(grid)
        winning_positions = self.cluster_detector.get_winning_positions(clusters)
        grid.remove_positions(winning_positions)
        
        # Force spawn an EW by using a specific seed
        rng = SpinRNG(seed=2)  # This seed produces an EW
        spawn_results = self.wild_system.spawn_wilds_for_clusters(grid, clusters, rng)
        
        # Check if we got an EW
        ew_spawns = [s for s in spawn_results if s.wild_type == Symbol.E_WILD and s.success]
        
        if ew_spawns:
            # This demonstrates where game state tracking would mark the EW
            # as "spawned this cascade" to prevent immediate explosion
            spawned_ew_positions = [s.spawned_position for s in ew_spawns]
            print(f"\nEWs spawned at {spawned_ew_positions} should be marked as non-exploding")
            
            # In actual game implementation, these positions would be tracked
            # in game state to prevent explosion until next cascade
    
    def test_edge_case_overlapping_clusters(self):
        """Test wild spawning with overlapping cluster footprints."""
        grid = Grid()
        
        # Create overlapping clusters using a wild
        # Pink cluster
        grid.set_symbol(0, 0, Symbol.PINK_SK)
        grid.set_symbol(0, 1, Symbol.PINK_SK)
        grid.set_symbol(1, 0, Symbol.PINK_SK)
        grid.set_symbol(1, 1, Symbol.WILD)  # Shared position
        grid.set_symbol(2, 1, Symbol.PINK_SK)
        
        # Blue cluster (shares the wild)
        grid.set_symbol(1, 1, Symbol.WILD)  # Same wild
        grid.set_symbol(1, 2, Symbol.BLUE_SK)
        grid.set_symbol(2, 1, Symbol.BLUE_SK)  # Overlaps with pink
        grid.set_symbol(2, 2, Symbol.BLUE_SK)
        grid.set_symbol(3, 2, Symbol.BLUE_SK)
        
        # Detect clusters
        clusters = self.cluster_detector.find_clusters(grid)
        # Should find 2 clusters, both including the wild
        
        # Remove winning positions
        winning_positions = self.cluster_detector.get_winning_positions(clusters)
        grid.remove_positions(winning_positions)
        
        # Spawn wilds
        spawn_results = self.wild_system.spawn_wilds_for_clusters(grid, clusters, self.rng)
        
        # Each cluster should attempt to spawn
        self.assertEqual(len(spawn_results), len(clusters))
        
        # Count successful spawns
        successful_spawns = sum(1 for s in spawn_results if s.success)
        print(f"\nSuccessfully spawned {successful_spawns} wilds from {len(clusters)} clusters")


class TestWildSpawningStatistics(unittest.TestCase):
    """Test statistical properties of wild spawning over many iterations."""
    
    def test_50_50_distribution_over_many_games(self):
        """Verify 50/50 wild type distribution holds over many games."""
        wild_count = 0
        ew_count = 0
        total_spawns = 0
        
        # Simulate many cluster spawns
        for seed in range(1000):
            grid = Grid()
            wild_system = WildSpawningSystem()
            rng = SpinRNG(seed=seed)
            
            # Create a simple cluster
            cluster = ClusterDetector()
            positions = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]
            for row, col in positions:
                grid.set_symbol(row, col, Symbol.PINK_SK)
            
            clusters = cluster.find_clusters(grid)
            grid.remove_positions(positions)
            
            spawns = wild_system.spawn_wilds_for_clusters(grid, clusters, rng)
            
            for spawn in spawns:
                if spawn.success:
                    total_spawns += 1
                    if spawn.wild_type == Symbol.WILD:
                        wild_count += 1
                    else:
                        ew_count += 1
        
        # Check distribution
        wild_ratio = wild_count / total_spawns
        ew_ratio = ew_count / total_spawns
        
        print(f"\nWild spawn distribution over {total_spawns} spawns:")
        print(f"  Regular Wild: {wild_count} ({wild_ratio:.1%})")
        print(f"  Explosivo Wild: {ew_count} ({ew_ratio:.1%})")
        
        # Should be close to 50/50
        self.assertAlmostEqual(wild_ratio, 0.5, delta=0.02)
        self.assertAlmostEqual(ew_ratio, 0.5, delta=0.02)


if __name__ == '__main__':
    unittest.main()