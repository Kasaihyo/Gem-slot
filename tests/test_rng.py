"""Unit tests for RNG module."""

import pytest
import numpy as np
from simulator.core.rng import SpinRNG, create_worker_rng, verify_determinism


class TestSpinRNG:
    """Test SpinRNG wrapper functionality."""
    
    def test_deterministic_behavior(self):
        """Test that same seed produces same results."""
        seed = 12345
        rng1 = SpinRNG(seed)
        rng2 = SpinRNG(seed)
        
        # Generate some random numbers
        results1 = [rng1.random() for _ in range(100)]
        results2 = [rng2.random() for _ in range(100)]
        
        # Should be identical
        assert results1 == results2
    
    def test_random_range(self):
        """Test that random() returns values in [0, 1)."""
        rng = SpinRNG(42)
        
        for _ in range(1000):
            value = rng.random()
            assert 0.0 <= value < 1.0
    
    def test_randint_range(self):
        """Test that randint returns values in specified range."""
        rng = SpinRNG(42)
        
        # Test various ranges
        for _ in range(100):
            # [1, 10]
            value = rng.randint(1, 10)
            assert 1 <= value <= 10
            
            # [0, 0] - edge case
            value = rng.randint(0, 0)
            assert value == 0
            
            # [-5, 5]
            value = rng.randint(-5, 5)
            assert -5 <= value <= 5
    
    def test_choice(self):
        """Test choice method."""
        rng = SpinRNG(42)
        
        # Test with list
        choices = ['A', 'B', 'C', 'D', 'E']
        selected = set()
        for _ in range(100):
            choice = rng.choice(choices)
            assert choice in choices
            selected.add(choice)
        
        # Should have selected multiple different elements
        assert len(selected) > 1
        
        # Test with empty sequence
        with pytest.raises(IndexError):
            rng.choice([])
    
    def test_weighted_choice(self):
        """Test weighted choice method."""
        rng = SpinRNG(42)
        
        choices = ['A', 'B', 'C']
        weights = [1, 2, 7]  # C should be selected ~70% of the time
        
        counts = {'A': 0, 'B': 0, 'C': 0}
        iterations = 10000
        
        for _ in range(iterations):
            choice = rng.weighted_choice(choices, weights)
            counts[choice] += 1
        
        # Check approximate distribution
        assert abs(counts['A'] / iterations - 0.1) < 0.02
        assert abs(counts['B'] / iterations - 0.2) < 0.02
        assert abs(counts['C'] / iterations - 0.7) < 0.02
        
        # Test error cases
        with pytest.raises(ValueError):
            rng.weighted_choice(['A', 'B'], [1, 2, 3])  # Mismatched lengths
        
        with pytest.raises(ValueError):
            rng.weighted_choice([], [])  # Empty
        
        with pytest.raises(ValueError):
            rng.weighted_choice(['A'], [-1])  # Negative weight
        
        with pytest.raises(ValueError):
            rng.weighted_choice(['A'], [0])  # All zero weights
    
    def test_weighted_choice_numpy(self):
        """Test NumPy weighted choice method."""
        rng = SpinRNG(42)
        
        choices = np.array(['A', 'B', 'C'])
        weights = np.array([0.1, 0.2, 0.7])  # Must sum to 1.0
        
        counts = {'A': 0, 'B': 0, 'C': 0}
        iterations = 10000
        
        for _ in range(iterations):
            choice = rng.weighted_choice_numpy(choices, weights)
            counts[choice] += 1
        
        # Check approximate distribution
        assert abs(counts['A'] / iterations - 0.1) < 0.02
        assert abs(counts['B'] / iterations - 0.2) < 0.02
        assert abs(counts['C'] / iterations - 0.7) < 0.02
    
    def test_shuffle(self):
        """Test shuffle method."""
        rng = SpinRNG(42)
        
        # Test that shuffle modifies list
        original = [1, 2, 3, 4, 5]
        to_shuffle = original.copy()
        rng.shuffle(to_shuffle)
        
        # Should be different order (with high probability)
        assert to_shuffle != original
        # But same elements
        assert sorted(to_shuffle) == sorted(original)
        
        # Test determinism - use fresh RNGs
        rng1 = SpinRNG(42)
        rng2 = SpinRNG(42)
        list1 = [1, 2, 3, 4, 5]
        list2 = [1, 2, 3, 4, 5]
        
        rng1.shuffle(list1)
        rng2.shuffle(list2)
        
        assert list1 == list2
    
    def test_call_count(self):
        """Test that call count tracks RNG usage."""
        rng = SpinRNG(42)
        
        assert rng.get_call_count() == 0
        
        rng.random()
        assert rng.get_call_count() == 1
        
        rng.randint(1, 10)
        assert rng.get_call_count() == 2
        
        rng.choice([1, 2, 3])
        assert rng.get_call_count() == 3
    
    def test_state_management(self):
        """Test get_state and set_state methods."""
        rng = SpinRNG(42)
        
        # Generate some numbers
        initial = [rng.random() for _ in range(5)]
        
        # Save state
        state = rng.get_state()
        
        # Generate more numbers
        after_save = [rng.random() for _ in range(5)]
        
        # Restore state
        rng.set_state(state)
        
        # Should generate same numbers as after_save
        restored = [rng.random() for _ in range(5)]
        
        assert after_save == restored


class TestParallelDeterminism:
    """Test parallel RNG determinism."""
    
    def test_worker_seeds_unique(self):
        """Test that worker seeds are unique."""
        base_seed = 12345
        
        # Create RNGs for multiple workers
        workers = []
        for worker_id in range(10):
            rng = create_worker_rng(base_seed, worker_id)
            workers.append(rng)
        
        # Generate some random numbers from each
        results = []
        for rng in workers:
            worker_results = [rng.random() for _ in range(100)]
            results.append(worker_results)
        
        # Check that each worker produces different results
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                assert results[i] != results[j], f"Workers {i} and {j} produced same results"
    
    def test_worker_determinism(self):
        """Test that same worker_id produces same results."""
        base_seed = 12345
        worker_id = 3
        
        # Create two RNGs with same parameters
        rng1 = create_worker_rng(base_seed, worker_id)
        rng2 = create_worker_rng(base_seed, worker_id)
        
        # Should produce identical results
        results1 = [rng1.random() for _ in range(100)]
        results2 = [rng2.random() for _ in range(100)]
        
        assert results1 == results2
    
    def test_no_correlation_between_workers(self):
        """Test that there's no obvious correlation between workers."""
        base_seed = 12345
        
        # Generate first values from multiple workers
        first_values = []
        for worker_id in range(100):
            rng = create_worker_rng(base_seed, worker_id)
            first_values.append(rng.random())
        
        # Check that values are well-distributed
        # Simple test: values should span most of [0, 1)
        assert min(first_values) < 0.1
        assert max(first_values) > 0.9
        
        # Check no obvious patterns (consecutive differences)
        diffs = [abs(first_values[i] - first_values[i-1]) for i in range(1, len(first_values))]
        avg_diff = sum(diffs) / len(diffs)
        
        # Average difference should be around 0.33 for uniform distribution
        assert 0.2 < avg_diff < 0.5


class TestVerifyDeterminism:
    """Test determinism verification helper."""
    
    def test_verify_determinism_helper(self):
        """Test the verify_determinism helper function."""
        seed = 12345
        
        # Run twice with same seed
        results1 = verify_determinism(seed, 1000)
        results2 = verify_determinism(seed, 1000)
        
        # Should be identical
        assert results1 == results2
        
        # Run with different seed
        results3 = verify_determinism(seed + 1, 1000)
        
        # Should be different
        assert results1 != results3
        
        # Check all values in valid range
        for value in results1:
            assert 0.0 <= value < 1.0


if __name__ == "__main__":
    pytest.main([__file__])