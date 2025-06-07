"""
Unit tests for the wild spawning system.
"""

import unittest
from simulator.core.wild_spawning import WildSpawningSystem, WildSpawn
from simulator.core.grid import Grid
from simulator.core.clusters import Cluster
from simulator.core.symbol import Symbol
from simulator.core.rng import SpinRNG


class TestWildSpawning(unittest.TestCase):
    """Test cases for wild spawning mechanics."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.system = WildSpawningSystem()
        self.grid = Grid()
        self.rng = SpinRNG(seed=42)  # Fixed seed for deterministic tests
    
    def test_wild_type_selection(self):
        """Test that wild type selection follows 50/50 probability."""
        # Create a simple cluster
        cluster = Cluster(
            symbol=Symbol.PINK_SK,
            positions=[(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)],
            size=5
        )
        
        # Run many spawn attempts to check distribution
        wild_count = 0
        explosivo_count = 0
        iterations = 1000
        
        for i in range(iterations):
            rng = SpinRNG(seed=i)  # Different seed each time
            spawn = self.system._create_spawn_attempt(0, cluster, rng)
            
            if spawn.wild_type == Symbol.WILD:
                wild_count += 1
            else:
                explosivo_count += 1
        
        # Check that distribution is roughly 50/50 (with some tolerance)
        wild_ratio = wild_count / iterations
        self.assertGreater(wild_ratio, 0.45)
        self.assertLess(wild_ratio, 0.55)
    
    def test_empty_position_selection(self):
        """Test that wilds only spawn in empty positions within footprint."""
        # Create a grid with some occupied positions
        self.grid.set_symbol(0, 0, Symbol.PINK_SK)
        self.grid.set_symbol(0, 1, Symbol.PINK_SK)
        # (1,0), (1,1), (2,0) are empty
        
        cluster = Cluster(
            symbol=Symbol.PINK_SK,
            positions=[(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)],
            size=5
        )
        
        # Spawn wild for this cluster
        spawns = self.system.spawn_wilds_for_clusters(self.grid, [cluster], self.rng)
        
        self.assertEqual(len(spawns), 1)
        spawn = spawns[0]
        
        # Check spawn was successful
        self.assertTrue(spawn.success)
        
        # Check position is one of the empty ones in footprint
        self.assertIn(spawn.spawned_position, [(1, 0), (1, 1), (2, 0)])
        
        # Check wild was placed on grid
        row, col = spawn.spawned_position
        self.assertIn(self.grid.get_symbol(row, col), [Symbol.WILD, Symbol.E_WILD])
    
    def test_no_spawn_when_footprint_full(self):
        """Test that spawn fails when entire footprint is occupied."""
        # Fill entire cluster footprint
        positions = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]
        for row, col in positions:
            self.grid.set_symbol(row, col, Symbol.PINK_SK)
        
        cluster = Cluster(
            symbol=Symbol.PINK_SK,
            positions=positions,
            size=5
        )
        
        # Try to spawn wild
        spawns = self.system.spawn_wilds_for_clusters(self.grid, [cluster], self.rng)
        
        self.assertEqual(len(spawns), 1)
        spawn = spawns[0]
        
        # Check spawn failed
        self.assertFalse(spawn.success)
        self.assertIsNone(spawn.spawned_position)
    
    def test_multiple_cluster_collision_handling(self):
        """Test collision handling when multiple clusters spawn simultaneously."""
        # Create two clusters with overlapping footprints
        cluster1 = Cluster(
            symbol=Symbol.PINK_SK,
            positions=[(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)],
            size=5
        )
        
        cluster2 = Cluster(
            symbol=Symbol.BLUE_SK,
            positions=[(1, 1), (1, 2), (2, 1), (2, 2), (3, 1)],
            size=5
        )
        
        # Clear grid (all positions empty)
        self.grid.clear()
        
        # Spawn wilds for both clusters
        spawns = self.system.spawn_wilds_for_clusters(
            self.grid, 
            [cluster1, cluster2], 
            self.rng
        )
        
        self.assertEqual(len(spawns), 2)
        
        # Both should succeed
        self.assertTrue(spawns[0].success)
        self.assertTrue(spawns[1].success)
        
        # Positions should be different
        self.assertNotEqual(spawns[0].spawned_position, spawns[1].spawned_position)
        
        # Each position should be in respective footprint
        self.assertIn(spawns[0].spawned_position, cluster1.positions)
        self.assertIn(spawns[1].spawned_position, cluster2.positions)
    
    def test_deterministic_spawn_order(self):
        """Test that spawn order is deterministic with same RNG seed."""
        clusters = [
            Cluster(Symbol.PINK_SK, [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)], 5),
            Cluster(Symbol.BLUE_SK, [(2, 2), (2, 3), (3, 2), (3, 3), (4, 2)], 5),
            Cluster(Symbol.GREEN_SK, [(0, 3), (0, 4), (1, 3), (1, 4), (2, 4)], 5)
        ]
        
        # Run spawning twice with same seed
        rng1 = SpinRNG(seed=123)
        grid1 = Grid()
        spawns1 = self.system.spawn_wilds_for_clusters(grid1, clusters, rng1)
        
        rng2 = SpinRNG(seed=123)
        grid2 = Grid()
        spawns2 = self.system.spawn_wilds_for_clusters(grid2, clusters, rng2)
        
        # Results should be identical
        self.assertEqual(len(spawns1), len(spawns2))
        for s1, s2 in zip(spawns1, spawns2):
            self.assertEqual(s1.wild_type, s2.wild_type)
            self.assertEqual(s1.spawned_position, s2.spawned_position)
            self.assertEqual(s1.success, s2.success)
    
    def test_spawn_statistics(self):
        """Test spawn statistics calculation."""
        # Create mix of successful and failed spawns
        spawns = [
            WildSpawn(0, Symbol.WILD, [(0, 0)], (0, 0), True),
            WildSpawn(1, Symbol.E_WILD, [(1, 0)], (1, 0), True),
            WildSpawn(2, Symbol.WILD, [(2, 0)], None, False),
            WildSpawn(3, Symbol.E_WILD, [(3, 0)], (3, 0), True),
        ]
        
        stats = self.system.get_spawn_statistics(spawns)
        
        self.assertEqual(stats['total_attempts'], 4)
        self.assertEqual(stats['successful_spawns'], 3)
        self.assertEqual(stats['failed_spawns'], 1)
        self.assertEqual(stats['wild_spawns'], 1)
        self.assertEqual(stats['explosivo_wild_spawns'], 2)
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        # Valid configuration
        self.assertTrue(self.system.validate_spawn_configuration())
        
        # Test invalid configurations
        system = WildSpawningSystem()
        
        # Invalid: probabilities don't sum to 1
        system.WILD_PROBABILITY = 0.6
        system.EXPLOSIVO_WILD_PROBABILITY = 0.5
        self.assertFalse(system.validate_spawn_configuration())
        
        # Invalid: negative probability
        system.WILD_PROBABILITY = -0.1
        system.EXPLOSIVO_WILD_PROBABILITY = 1.1
        self.assertFalse(system.validate_spawn_configuration())
    
    def test_edge_positions(self):
        """Test spawning at grid edge positions."""
        # Cluster at top-left corner
        cluster = Cluster(
            symbol=Symbol.PINK_SK,
            positions=[(0, 0), (0, 1), (1, 0), (1, 1), (0, 2)],
            size=5
        )
        
        self.grid.clear()
        spawns = self.system.spawn_wilds_for_clusters(self.grid, [cluster], self.rng)
        
        self.assertEqual(len(spawns), 1)
        self.assertTrue(spawns[0].success)
        self.assertIn(spawns[0].spawned_position, cluster.positions)
    
    def test_uniform_position_distribution(self):
        """Test that position selection is uniformly random."""
        # Create cluster with 5 positions, all empty
        cluster = Cluster(
            symbol=Symbol.PINK_SK,
            positions=[(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)],
            size=5
        )
        
        # Count how many times each position is selected
        position_counts = {pos: 0 for pos in cluster.positions}
        iterations = 1000
        
        for i in range(iterations):
            grid = Grid()  # Fresh empty grid
            rng = SpinRNG(seed=i)
            spawns = self.system.spawn_wilds_for_clusters(grid, [cluster], rng)
            
            if spawns[0].success:
                position_counts[spawns[0].spawned_position] += 1
        
        # Each position should be selected roughly 1/5 of the time
        expected_count = iterations / len(cluster.positions)
        for pos, count in position_counts.items():
            # Allow 20% deviation from expected
            self.assertGreater(count, expected_count * 0.8)
            self.assertLess(count, expected_count * 1.2)


if __name__ == '__main__':
    unittest.main()