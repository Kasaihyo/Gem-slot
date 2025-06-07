"""Unit tests for cluster detection system."""

import pytest
from simulator.core.grid import Grid
from simulator.core.symbol import Symbol
from simulator.core.clusters import ClusterDetector, Cluster


class TestClusterDetection:
    """Test basic cluster detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ClusterDetector()
    
    def test_simple_horizontal_cluster(self):
        """Test detection of simple horizontal cluster."""
        grid = Grid()
        
        # Create horizontal cluster of 5 pink symbols
        for col in range(5):
            grid.set_symbol(2, col, Symbol.PINK_SK)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 1
        assert clusters[0].symbol == Symbol.PINK_SK
        assert clusters[0].size == 5
        assert len(clusters[0].positions) == 5
    
    def test_simple_vertical_cluster(self):
        """Test detection of simple vertical cluster."""
        grid = Grid()
        
        # Create vertical cluster of 5 green symbols
        for row in range(5):
            grid.set_symbol(row, 2, Symbol.GREEN_SK)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 1
        assert clusters[0].symbol == Symbol.GREEN_SK
        assert clusters[0].size == 5
    
    def test_l_shaped_cluster(self):
        """Test detection of L-shaped cluster."""
        grid = Grid()
        
        # Create L-shaped cluster
        # B B B
        # B
        # B
        for col in range(3):
            grid.set_symbol(0, col, Symbol.BLUE_SK)
        for row in range(3):
            grid.set_symbol(row, 0, Symbol.BLUE_SK)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 1
        assert clusters[0].symbol == Symbol.BLUE_SK
        assert clusters[0].size == 5
    
    def test_cluster_too_small(self):
        """Test that clusters smaller than 5 are not detected."""
        grid = Grid()
        
        # Create cluster of only 4 symbols
        for col in range(4):
            grid.set_symbol(1, col, Symbol.ORANGE_SK)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 0
    
    def test_multiple_clusters(self):
        """Test detection of multiple separate clusters."""
        grid = Grid()
        
        # Create truly separate clusters with gap between them
        # First cluster: 5 horizontal pink at top
        for col in range(5):
            grid.set_symbol(0, col, Symbol.PINK_SK)
        
        # Gap row at row 1 (empty)
        
        # Second cluster: 5 horizontal green at row 2 
        for col in range(5):
            grid.set_symbol(2, col, Symbol.GREEN_SK)
        
        # Gap row at row 3 (empty)
        
        # Third cluster: 5 horizontal blue at bottom
        for col in range(5):
            grid.set_symbol(4, col, Symbol.BLUE_SK)
            
        clusters = self.detector.find_clusters(grid)
        
        # All three should be separate
        assert len(clusters) == 3
        
        # Check each cluster type exists
        symbols = {c.symbol for c in clusters}
        assert Symbol.PINK_SK in symbols
        assert Symbol.GREEN_SK in symbols  
        assert Symbol.BLUE_SK in symbols
        
        # All should be size 5
        for cluster in clusters:
            assert cluster.size == 5
    
    def test_wild_in_cluster(self):
        """Test wild participation in cluster."""
        grid = Grid()
        
        # Create cluster with wild: P W P P P
        grid.set_symbol(1, 0, Symbol.PINK_SK)
        grid.set_symbol(1, 1, Symbol.WILD)
        grid.set_symbol(1, 2, Symbol.PINK_SK)
        grid.set_symbol(1, 3, Symbol.PINK_SK)
        grid.set_symbol(1, 4, Symbol.PINK_SK)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 1
        assert clusters[0].symbol == Symbol.PINK_SK
        assert clusters[0].size == 5
        assert (1, 1) in clusters[0].positions  # Wild position included
    
    def test_explosivo_wild_in_cluster(self):
        """Test explosivo wild participation in cluster."""
        grid = Grid()
        
        # Create cluster with explosivo wild
        for row in range(4):
            grid.set_symbol(row, 2, Symbol.CYAN_SK)
        grid.set_symbol(4, 2, Symbol.E_WILD)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 1
        assert clusters[0].symbol == Symbol.CYAN_SK
        assert clusters[0].size == 5
        assert (4, 2) in clusters[0].positions
    
    def test_scatter_not_in_cluster(self):
        """Test that scatters don't participate in clusters."""
        grid = Grid()
        
        # Try to create cluster with scatter
        for col in range(4):
            grid.set_symbol(2, col, Symbol.LADY_SK)
        grid.set_symbol(2, 4, Symbol.SCATTER)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 0  # Only 4 symbols, scatter doesn't count
    
    def test_empty_positions_break_cluster(self):
        """Test that empty positions break clusters."""
        grid = Grid()
        
        # Create broken cluster: P P _ P P
        grid.set_symbol(1, 0, Symbol.PINK_SK)
        grid.set_symbol(1, 1, Symbol.PINK_SK)
        # Skip position (1, 2)
        grid.set_symbol(1, 3, Symbol.PINK_SK)
        grid.set_symbol(1, 4, Symbol.PINK_SK)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 0  # Gap breaks the cluster
    
    def test_diagonal_not_connected(self):
        """Test that diagonal connections don't count."""
        grid = Grid()
        
        # Create diagonal pattern
        for i in range(5):
            grid.set_symbol(i, i, Symbol.BLUE_SK)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 0  # Diagonals don't connect
    
    def test_cluster_size_capped_at_15(self):
        """Test that cluster size is capped at 15."""
        grid = Grid()
        
        # Fill entire grid with same symbol (25 positions)
        for row in range(5):
            for col in range(5):
                grid.set_symbol(row, col, Symbol.ORANGE_SK)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 1
        assert clusters[0].size == 15  # Capped at 15
        assert len(clusters[0].positions) == 25  # But all positions included


class TestWildClusters:
    """Test complex wild participation in clusters."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ClusterDetector()
    
    def test_wild_connects_different_symbols(self):
        """Test wild connecting different symbol types."""
        grid = Grid()
        
        # Create pattern:
        # P P W B B
        grid.set_symbol(1, 0, Symbol.PINK_SK)
        grid.set_symbol(1, 1, Symbol.PINK_SK)
        grid.set_symbol(1, 2, Symbol.WILD)
        grid.set_symbol(1, 3, Symbol.BLUE_SK)
        grid.set_symbol(1, 4, Symbol.BLUE_SK)
        
        # Add more symbols to make clusters valid
        grid.set_symbol(0, 1, Symbol.PINK_SK)
        grid.set_symbol(2, 1, Symbol.PINK_SK)
        grid.set_symbol(0, 3, Symbol.BLUE_SK)
        grid.set_symbol(2, 3, Symbol.BLUE_SK)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 2
        
        # Both clusters should include the wild
        for cluster in clusters:
            assert (1, 2) in cluster.positions
    
    def test_wild_in_multiple_clusters(self):
        """Test single wild participating in multiple clusters."""
        grid = Grid()
        
        # Create cross pattern with wild in center
        #   P
        #   P
        # G W B
        #   B
        #   B
        
        # Vertical pink cluster
        for row in range(3):
            grid.set_symbol(row, 2, Symbol.PINK_SK)
        
        # Horizontal with wild
        grid.set_symbol(2, 1, Symbol.GREEN_SK)
        grid.set_symbol(2, 2, Symbol.WILD)  # Overwrites pink
        grid.set_symbol(2, 3, Symbol.BLUE_SK)
        
        # Vertical blue cluster (need 5 total for valid cluster)
        for row in range(3, 5):
            grid.set_symbol(row, 3, Symbol.BLUE_SK)
        # Add more blues to make 5
        grid.set_symbol(1, 3, Symbol.BLUE_SK)  
        grid.set_symbol(0, 3, Symbol.BLUE_SK)
        
        # Add more greens to make valid cluster
        grid.set_symbol(1, 1, Symbol.GREEN_SK)
        grid.set_symbol(3, 1, Symbol.GREEN_SK)
        grid.set_symbol(2, 0, Symbol.GREEN_SK)
        
        clusters = self.detector.find_clusters(grid)
        
        # Should find green and blue clusters (pink broken by wild)
        assert len(clusters) == 2
        
        # Wild should be in both clusters
        wild_count = 0
        for cluster in clusters:
            if (2, 2) in cluster.positions:
                wild_count += 1
        
        assert wild_count == 2  # Wild in both clusters
    
    def test_pure_wild_cluster_invalid(self):
        """Test that pure wild clusters are not valid."""
        grid = Grid()
        
        # Create cluster of only wilds
        positions = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2)]
        for row, col in positions:
            grid.set_symbol(row, col, Symbol.WILD)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 0  # Pure wild cluster not valid
    
    def test_wild_chain(self):
        """Test chain of wilds connecting paying symbols."""
        grid = Grid()
        
        # Create pattern: P W W W P
        grid.set_symbol(1, 0, Symbol.PINK_SK)
        grid.set_symbol(1, 1, Symbol.WILD)
        grid.set_symbol(1, 2, Symbol.E_WILD)
        grid.set_symbol(1, 3, Symbol.WILD)
        grid.set_symbol(1, 4, Symbol.PINK_SK)
        
        clusters = self.detector.find_clusters(grid)
        
        assert len(clusters) == 1
        assert clusters[0].symbol == Symbol.PINK_SK
        assert clusters[0].size == 5


class TestPRDExamples:
    """Test specific examples from the PRD."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ClusterDetector()
    
    def test_prd_8_pink_cluster_example(self):
        """Test the 8 pink cluster example from PRD."""
        grid = Grid()
        
        # Set up the exact grid from PRD
        # Row 0
        grid.set_symbol(0, 0, Symbol.LADY_SK)
        grid.set_symbol(0, 1, Symbol.PINK_SK)
        grid.set_symbol(0, 2, Symbol.GREEN_SK)
        grid.set_symbol(0, 3, Symbol.BLUE_SK)
        grid.set_symbol(0, 4, Symbol.ORANGE_SK)
        
        # Row 1
        grid.set_symbol(1, 0, Symbol.CYAN_SK)
        grid.set_symbol(1, 1, Symbol.WILD)
        grid.set_symbol(1, 2, Symbol.PINK_SK)
        grid.set_symbol(1, 3, Symbol.PINK_SK)
        grid.set_symbol(1, 4, Symbol.GREEN_SK)
        
        # Row 2
        grid.set_symbol(2, 0, Symbol.BLUE_SK)
        grid.set_symbol(2, 1, Symbol.PINK_SK)
        grid.set_symbol(2, 2, Symbol.PINK_SK)
        grid.set_symbol(2, 3, Symbol.PINK_SK)
        grid.set_symbol(2, 4, Symbol.LADY_SK)
        
        # Row 3
        grid.set_symbol(3, 0, Symbol.ORANGE_SK)
        grid.set_symbol(3, 1, Symbol.PINK_SK)
        grid.set_symbol(3, 2, Symbol.E_WILD)
        grid.set_symbol(3, 3, Symbol.PINK_SK)
        grid.set_symbol(3, 4, Symbol.BLUE_SK)
        
        # Row 4
        grid.set_symbol(4, 0, Symbol.SCATTER)
        grid.set_symbol(4, 1, Symbol.CYAN_SK)
        grid.set_symbol(4, 2, Symbol.GREEN_SK)
        grid.set_symbol(4, 3, Symbol.SCATTER)
        grid.set_symbol(4, 4, Symbol.ORANGE_SK)
        
        clusters = self.detector.find_clusters(grid)
        
        # Should find the pink cluster
        assert len(clusters) >= 1
        
        pink_cluster = next((c for c in clusters if c.symbol == Symbol.PINK_SK), None)
        assert pink_cluster is not None
        
        # The actual cluster from the grid analysis
        # Pink at: (0,1), (1,2), (1,3), (2,1), (2,2), (2,3), (3,1), (3,3)
        # Wild at: (1,1) connects to pinks at (0,1) and (2,1)
        # EW at: (3,2) connects to pinks at (2,2), (3,1), (3,3)
        # Total: 8 pink + 1 wild + 1 EW = 10 positions
        
        assert len(pink_cluster.positions) == 10
        
        # Check both wilds are included
        assert (1, 1) in pink_cluster.positions  # Regular wild
        assert (3, 2) in pink_cluster.positions  # Explosivo wild


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ClusterDetector()
    
    def test_empty_grid(self):
        """Test cluster detection on empty grid."""
        grid = Grid()
        clusters = self.detector.find_clusters(grid)
        assert len(clusters) == 0
    
    def test_grid_full_of_scatters(self):
        """Test grid full of scatters."""
        grid = Grid()
        
        for row in range(5):
            for col in range(5):
                grid.set_symbol(row, col, Symbol.SCATTER)
        
        clusters = self.detector.find_clusters(grid)
        assert len(clusters) == 0
    
    def test_alternating_pattern(self):
        """Test alternating symbol pattern."""
        grid = Grid()
        
        # Create checkerboard pattern
        for row in range(5):
            for col in range(5):
                if (row + col) % 2 == 0:
                    grid.set_symbol(row, col, Symbol.PINK_SK)
                else:
                    grid.set_symbol(row, col, Symbol.BLUE_SK)
        
        clusters = self.detector.find_clusters(grid)
        assert len(clusters) == 0  # No clusters possible
    
    def test_complex_multi_cluster(self):
        """Test complex scenario with multiple overlapping clusters."""
        grid = Grid()
        
        # Create complex pattern with multiple clusters
        # Fill grid strategically
        pattern = [
            [Symbol.PINK_SK, Symbol.PINK_SK, Symbol.WILD, Symbol.BLUE_SK, Symbol.BLUE_SK],
            [Symbol.PINK_SK, Symbol.PINK_SK, Symbol.WILD, Symbol.BLUE_SK, Symbol.BLUE_SK],
            [Symbol.WILD, Symbol.WILD, Symbol.WILD, Symbol.WILD, Symbol.WILD],
            [Symbol.GREEN_SK, Symbol.GREEN_SK, Symbol.WILD, Symbol.CYAN_SK, Symbol.CYAN_SK],
            [Symbol.GREEN_SK, Symbol.GREEN_SK, Symbol.WILD, Symbol.CYAN_SK, Symbol.CYAN_SK]
        ]
        
        for row in range(5):
            for col in range(5):
                grid.set_symbol(row, col, pattern[row][col])
        
        clusters = self.detector.find_clusters(grid)
        
        # Should find 4 clusters (pink, blue, green, cyan)
        assert len(clusters) == 4
        
        # Each cluster should include the central wilds
        for cluster in clusters:
            # Central wild should be in all clusters
            assert (2, 2) in cluster.positions


class TestClusterPerformance:
    """Test cluster detection performance."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ClusterDetector()
    
    def test_worst_case_performance(self):
        """Test performance in worst case scenario."""
        grid = Grid()
        
        # Worst case: many small non-connecting groups
        # This forces algorithm to check many possibilities
        for row in range(5):
            for col in range(5):
                # Create a complex pattern
                symbol_idx = (row * 5 + col) % 6
                symbols = [Symbol.PINK_SK, Symbol.GREEN_SK, Symbol.BLUE_SK,
                          Symbol.ORANGE_SK, Symbol.CYAN_SK, Symbol.LADY_SK]
                grid.set_symbol(row, col, symbols[symbol_idx])
        
        # Should still complete quickly
        import time
        start = time.time()
        clusters = self.detector.find_clusters(grid)
        elapsed = time.time() - start
        
        # Should complete in under 1ms
        assert elapsed < 0.001
        
    def test_reuse_performance(self):
        """Test that detector can be reused efficiently."""
        grid = Grid()
        
        # Fill with some pattern
        for row in range(5):
            for col in range(5):
                if row == 2:
                    grid.set_symbol(row, col, Symbol.PINK_SK)
        
        # Run detection multiple times
        import time
        start = time.time()
        for _ in range(1000):
            clusters = self.detector.find_clusters(grid)
        elapsed = time.time() - start
        
        # Should average less than 0.1ms per detection
        assert elapsed / 1000 < 0.0001


if __name__ == "__main__":
    pytest.main([__file__])