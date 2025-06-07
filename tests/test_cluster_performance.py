"""Performance comparison tests for cluster detection algorithms."""

import time
import pytest
from collections import deque
from simulator.core.grid import Grid, ROWS, COLS
from simulator.core.symbol import Symbol, is_empty, is_scatter, symbols_match_for_cluster
from simulator.core.clusters import ClusterDetector
from simulator.core.rng import SpinRNG


class BFSClusterDetector:
    """Basic BFS implementation for comparison."""
    
    def find_clusters_bfs(self, grid: Grid) -> list:
        """Find clusters using breadth-first search."""
        visited = [[False] * COLS for _ in range(ROWS)]
        clusters = []
        
        for row in range(ROWS):
            for col in range(COLS):
                if visited[row][col]:
                    continue
                    
                symbol = grid.get_symbol(row, col)
                if is_empty(symbol) or is_scatter(symbol):
                    visited[row][col] = True
                    continue
                
                # BFS from this position
                cluster_positions = []
                queue = deque([(row, col)])
                visited[row][col] = True
                
                while queue:
                    r, c = queue.popleft()
                    cluster_positions.append((r, c))
                    
                    # Check neighbors
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = r + dr, c + dc
                        
                        if (0 <= nr < ROWS and 0 <= nc < COLS and 
                            not visited[nr][nc]):
                            neighbor_symbol = grid.get_symbol(nr, nc)
                            
                            if symbols_match_for_cluster(symbol, neighbor_symbol):
                                visited[nr][nc] = True
                                queue.append((nr, nc))
                
                if len(cluster_positions) >= 5:
                    clusters.append(cluster_positions)
        
        return clusters


class TestClusterPerformanceComparison:
    """Compare Union-Find vs BFS performance."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.uf_detector = ClusterDetector()
        self.bfs_detector = BFSClusterDetector()
        self.rng = SpinRNG(42)
    
    def create_random_grid(self) -> Grid:
        """Create a random grid for testing."""
        grid = Grid()
        grid.drop_new_symbols(self.rng, is_free_spins=False)
        return grid
    
    def create_cluster_heavy_grid(self) -> Grid:
        """Create a grid with many potential clusters."""
        grid = Grid()
        
        # Create a pattern that encourages clustering
        symbols = [Symbol.PINK_SK, Symbol.GREEN_SK, Symbol.BLUE_SK]
        
        for row in range(ROWS):
            for col in range(COLS):
                # Use modulo to create regions
                symbol_idx = (row // 2 + col // 2) % len(symbols)
                grid.set_symbol(row, col, symbols[symbol_idx])
        
        # Add some wilds to connect regions
        grid.set_symbol(1, 2, Symbol.WILD)
        grid.set_symbol(3, 2, Symbol.WILD)
        
        return grid
    
    def test_single_detection_performance(self):
        """Test performance of single cluster detection."""
        grid = self.create_cluster_heavy_grid()
        
        # Time Union-Find
        start = time.perf_counter()
        uf_clusters = self.uf_detector.find_clusters(grid)
        uf_time = time.perf_counter() - start
        
        # Time BFS
        start = time.perf_counter()
        bfs_clusters = self.bfs_detector.find_clusters_bfs(grid)
        bfs_time = time.perf_counter() - start
        
        print(f"\nSingle detection:")
        print(f"  Union-Find: {uf_time*1000:.3f} ms")
        print(f"  BFS: {bfs_time*1000:.3f} ms")
        print(f"  Speedup: {bfs_time/uf_time:.1f}x")
        
        # Union-Find should be faster
        assert uf_time < bfs_time
    
    def test_bulk_detection_performance(self):
        """Test performance with many grids."""
        # Generate test grids
        grids = [self.create_random_grid() for _ in range(100)]
        
        # Time Union-Find
        start = time.perf_counter()
        for grid in grids:
            _ = self.uf_detector.find_clusters(grid)
        uf_total = time.perf_counter() - start
        
        # Time BFS
        start = time.perf_counter()
        for grid in grids:
            _ = self.bfs_detector.find_clusters_bfs(grid)
        bfs_total = time.perf_counter() - start
        
        print(f"\nBulk detection (100 grids):")
        print(f"  Union-Find: {uf_total*1000:.1f} ms total, {uf_total/len(grids)*1000:.3f} ms avg")
        print(f"  BFS: {bfs_total*1000:.1f} ms total, {bfs_total/len(grids)*1000:.3f} ms avg")
        print(f"  Speedup: {bfs_total/uf_total:.1f}x")
        
        # Union-Find should show significant speedup
        assert uf_total < bfs_total
    
    def test_worst_case_grid_performance(self):
        """Test performance on worst-case grid (many small groups)."""
        grid = Grid()
        
        # Create checkerboard pattern (worst case for cluster detection)
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    grid.set_symbol(row, col, Symbol.PINK_SK)
                else:
                    grid.set_symbol(row, col, Symbol.GREEN_SK)
        
        iterations = 1000
        
        # Time Union-Find
        start = time.perf_counter()
        for _ in range(iterations):
            _ = self.uf_detector.find_clusters(grid)
        uf_total = time.perf_counter() - start
        
        # Time BFS
        start = time.perf_counter()
        for _ in range(iterations):
            _ = self.bfs_detector.find_clusters_bfs(grid)
        bfs_total = time.perf_counter() - start
        
        print(f"\nWorst case (1000 iterations):")
        print(f"  Union-Find: {uf_total*1000:.1f} ms total")
        print(f"  BFS: {bfs_total*1000:.1f} ms total")
        print(f"  Speedup: {bfs_total/uf_total:.1f}x")
        
        # Even in worst case, Union-Find should be competitive
        assert uf_total < bfs_total * 2  # Allow some margin
    
    def test_large_cluster_performance(self):
        """Test performance with large clusters."""
        grid = Grid()
        
        # Fill entire grid with same symbol
        for row in range(ROWS):
            for col in range(COLS):
                grid.set_symbol(row, col, Symbol.ORANGE_SK)
        
        iterations = 1000
        
        # Time Union-Find
        start = time.perf_counter()
        for _ in range(iterations):
            _ = self.uf_detector.find_clusters(grid)
        uf_total = time.perf_counter() - start
        
        # Time BFS  
        start = time.perf_counter()
        for _ in range(iterations):
            _ = self.bfs_detector.find_clusters_bfs(grid)
        bfs_total = time.perf_counter() - start
        
        print(f"\nLarge cluster (1000 iterations):")
        print(f"  Union-Find: {uf_total*1000:.1f} ms total")
        print(f"  BFS: {bfs_total*1000:.1f} ms total")
        print(f"  Speedup: {bfs_total/uf_total:.1f}x")
        
        # Union-Find should excel with large clusters
        assert uf_total < bfs_total
    
    @pytest.mark.benchmark
    def test_realistic_game_simulation(self):
        """Test performance in realistic game simulation."""
        # Simulate a game session
        total_uf_time = 0
        total_bfs_time = 0
        detection_count = 0
        
        for _ in range(50):  # 50 spins
            grid = self.create_random_grid()
            
            # Time Union-Find
            start = time.perf_counter()
            uf_clusters = self.uf_detector.find_clusters(grid)
            total_uf_time += time.perf_counter() - start
            
            # Time BFS
            start = time.perf_counter()
            bfs_clusters = self.bfs_detector.find_clusters_bfs(grid)
            total_bfs_time += time.perf_counter() - start
            
            detection_count += 1
            
            # Simulate cascades if clusters found
            if uf_clusters:
                for _ in range(3):  # Average 3 cascades
                    # Remove cluster positions
                    for cluster in uf_clusters:
                        for pos in cluster.positions:
                            grid.set_symbol(pos[0], pos[1], Symbol.EMPTY)
                    
                    # Apply gravity and refill
                    grid.apply_gravity()
                    grid.drop_new_symbols(self.rng, is_free_spins=False)
                    
                    # Detect again
                    start = time.perf_counter()
                    uf_clusters = self.uf_detector.find_clusters(grid)
                    total_uf_time += time.perf_counter() - start
                    
                    start = time.perf_counter()
                    bfs_clusters = self.bfs_detector.find_clusters_bfs(grid)
                    total_bfs_time += time.perf_counter() - start
                    
                    detection_count += 1
                    
                    if not uf_clusters:
                        break
        
        print(f"\nRealistic simulation ({detection_count} detections):")
        print(f"  Union-Find: {total_uf_time*1000:.1f} ms total")
        print(f"  BFS: {total_bfs_time*1000:.1f} ms total")
        print(f"  Speedup: {total_bfs_time/total_uf_time:.1f}x")
        print(f"  Avg per detection - UF: {total_uf_time/detection_count*1000:.3f} ms")
        print(f"  Avg per detection - BFS: {total_bfs_time/detection_count*1000:.3f} ms")
        
        # Should see significant speedup in realistic scenarios
        assert total_uf_time < total_bfs_time
        
        # Check if we're approaching the claimed 25x speedup
        speedup = total_bfs_time / total_uf_time
        print(f"\n  Achieved {speedup:.1f}x speedup (target: 25x)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])