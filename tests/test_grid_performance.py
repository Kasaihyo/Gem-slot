"""Performance benchmarks for grid operations."""

import time
import pytest
from simulator.core.grid import Grid, ROWS, COLS
from simulator.core.symbol import Symbol
from simulator.core.rng import SpinRNG


class TestGridPerformance:
    """Performance benchmarks for grid operations."""
    
    def test_grid_creation_performance(self):
        """Benchmark grid creation."""
        iterations = 10000
        
        start_time = time.time()
        for _ in range(iterations):
            grid = Grid()
        end_time = time.time()
        
        elapsed = end_time - start_time
        per_grid = elapsed / iterations * 1000  # Convert to milliseconds
        
        print(f"\nGrid creation: {per_grid:.3f} ms per grid")
        assert per_grid < 0.1  # Should be less than 0.1ms per grid
    
    def test_symbol_access_performance(self):
        """Benchmark symbol get/set operations."""
        grid = Grid()
        iterations = 100000
        
        # Test set performance
        start_time = time.time()
        for i in range(iterations):
            row, col = divmod(i % 25, COLS)
            grid.set_symbol(row, col, Symbol.LADY_SK)
        end_time = time.time()
        
        set_elapsed = end_time - start_time
        per_set = set_elapsed / iterations * 1_000_000  # Convert to microseconds
        
        # Test get performance
        start_time = time.time()
        for i in range(iterations):
            row, col = divmod(i % 25, COLS)
            _ = grid.get_symbol(row, col)
        end_time = time.time()
        
        get_elapsed = end_time - start_time
        per_get = get_elapsed / iterations * 1_000_000  # Convert to microseconds
        
        print(f"\nSymbol set: {per_set:.3f} μs per operation")
        print(f"Symbol get: {per_get:.3f} μs per operation")
        
        assert per_set < 5  # Should be less than 5 microseconds
        assert per_get < 2  # Should be less than 2 microseconds
    
    def test_gravity_performance(self):
        """Benchmark gravity operations."""
        iterations = 1000
        
        # Create grids with symbols that need gravity
        grids = []
        for _ in range(iterations):
            grid = Grid()
            # Place symbols in middle rows
            for col in range(COLS):
                grid.set_symbol(2, col, Symbol.PINK_SK)
            grids.append(grid)
        
        # Benchmark gravity
        start_time = time.time()
        for grid in grids:
            grid.apply_gravity()
        end_time = time.time()
        
        elapsed = end_time - start_time
        per_gravity = elapsed / iterations * 1000  # Convert to milliseconds
        
        print(f"\nGravity application: {per_gravity:.3f} ms per operation")
        assert per_gravity < 1  # Should be less than 1ms
    
    def test_symbol_drop_performance(self):
        """Benchmark symbol dropping."""
        iterations = 1000
        rng = SpinRNG(42)
        
        # Create empty grids
        grids = []
        for _ in range(iterations):
            grids.append(Grid())
        
        # Benchmark dropping
        start_time = time.time()
        for grid in grids:
            grid.drop_new_symbols(rng, is_free_spins=False)
        end_time = time.time()
        
        elapsed = end_time - start_time
        per_drop = elapsed / iterations * 1000  # Convert to milliseconds
        
        print(f"\nSymbol dropping (25 positions): {per_drop:.3f} ms per operation")
        assert per_drop < 2  # Should be less than 2ms
    
    def test_full_cascade_simulation(self):
        """Benchmark a full cascade sequence."""
        iterations = 100
        rng = SpinRNG(42)
        
        total_time = 0
        
        for _ in range(iterations):
            grid = Grid()
            
            start_time = time.time()
            
            # Initial drop
            grid.drop_new_symbols(rng, is_free_spins=False)
            
            # Simulate removing a cluster
            positions_to_remove = [(2, 2), (2, 3), (3, 2), (3, 3), (4, 2)]
            grid.remove_positions(positions_to_remove)
            
            # Apply gravity
            grid.apply_gravity()
            
            # Drop new symbols
            grid.drop_new_symbols(rng, is_free_spins=False)
            
            end_time = time.time()
            total_time += end_time - start_time
        
        per_cascade = total_time / iterations * 1000  # Convert to milliseconds
        
        print(f"\nFull cascade sequence: {per_cascade:.3f} ms per cascade")
        assert per_cascade < 5  # Should be less than 5ms
    
    def test_state_serialization_performance(self):
        """Benchmark state serialization/deserialization."""
        grid = Grid()
        grid.drop_new_symbols(SpinRNG(42), is_free_spins=False)
        iterations = 10000
        
        # Benchmark serialization
        start_time = time.time()
        for _ in range(iterations):
            state = grid.to_state()
        end_time = time.time()
        
        serialize_time = (end_time - start_time) / iterations * 1000
        
        # Benchmark deserialization
        state = grid.to_state()
        start_time = time.time()
        for _ in range(iterations):
            new_grid = Grid()
            new_grid.from_state(state)
        end_time = time.time()
        
        deserialize_time = (end_time - start_time) / iterations * 1000
        
        print(f"\nState serialization: {serialize_time:.3f} ms per operation")
        print(f"State deserialization: {deserialize_time:.3f} ms per operation")
        
        assert serialize_time < 0.5  # Should be less than 0.5ms
        assert deserialize_time < 1  # Should be less than 1ms


if __name__ == "__main__":
    # Run with pytest -v -s to see performance output
    pytest.main([__file__, "-v", "-s"])