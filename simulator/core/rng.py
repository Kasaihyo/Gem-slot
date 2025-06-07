"""
Random Number Generator wrapper for deterministic game behavior.

This module provides the SpinRNG class which wraps Python's random.Random
to ensure controlled, deterministic randomness throughout the simulation.
"""

import random
from typing import TypeVar, List, Optional, Sequence
import numpy as np

T = TypeVar('T')


class SpinRNG:
    """
    Deterministic random number generator wrapper.
    
    This class provides a controlled interface to randomness, ensuring:
    - Deterministic behavior with same seed
    - No access to unwrapped RNG
    - Limited interface (only needed methods exposed)
    - Future-proof for RNG engine swapping
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the RNG with an optional seed.
        
        Args:
            seed: Random seed for deterministic behavior. If None, uses system random.
        """
        self._rng = random.Random(seed)
        self._seed = seed
        self._call_count = 0  # Track RNG usage for debugging
    
    def random(self) -> float:
        """
        Generate a random float in [0.0, 1.0).
        
        Returns:
            Random float between 0.0 (inclusive) and 1.0 (exclusive)
        """
        self._call_count += 1
        return self._rng.random()
    
    def randint(self, a: int, b: int) -> int:
        """
        Generate a random integer in [a, b] (inclusive).
        
        Args:
            a: Lower bound (inclusive)
            b: Upper bound (inclusive)
            
        Returns:
            Random integer between a and b (both inclusive)
        """
        self._call_count += 1
        return self._rng.randint(a, b)
    
    def choice(self, seq: Sequence[T]) -> T:
        """
        Choose a random element from a non-empty sequence.
        
        Args:
            seq: Non-empty sequence to choose from
            
        Returns:
            Random element from the sequence
            
        Raises:
            IndexError: If sequence is empty
        """
        if not seq:
            raise IndexError("Cannot choose from an empty sequence")
        self._call_count += 1
        return self._rng.choice(seq)
    
    def weighted_choice(self, choices: List[T], weights: List[float]) -> T:
        """
        Choose a random element with weighted probabilities.
        
        Args:
            choices: List of choices
            weights: List of weights (same length as choices)
            
        Returns:
            Random element chosen according to weights
            
        Raises:
            ValueError: If lengths don't match or weights are invalid
        """
        if len(choices) != len(weights):
            raise ValueError("Choices and weights must have same length")
        if not choices:
            raise ValueError("Cannot choose from empty choices")
        if any(w < 0 for w in weights):
            raise ValueError("Weights must be non-negative")
        if sum(weights) <= 0:
            raise ValueError("At least one weight must be positive")
        
        self._call_count += 1
        # Use cumulative distribution for efficiency
        cumsum = []
        total = 0
        for w in weights:
            total += w
            cumsum.append(total)
        
        r = self.random() * total
        for i, threshold in enumerate(cumsum):
            if r <= threshold:
                return choices[i]
        
        # Fallback (should never reach here)
        return choices[-1]
    
    def weighted_choice_numpy(self, choices: np.ndarray, weights: np.ndarray) -> str:
        """
        Optimized weighted choice using NumPy arrays.
        
        Args:
            choices: NumPy array of choices
            weights: NumPy array of normalized weights (must sum to 1.0)
            
        Returns:
            Random element chosen according to weights
        """
        self._call_count += 1
        # np.random.choice doesn't use our RNG, so we implement manually
        r = self.random()
        cumsum = np.cumsum(weights)
        idx = np.searchsorted(cumsum, r)
        return choices[idx]
    
    def shuffle(self, seq: List[T]) -> None:
        """
        Shuffle a list in-place.
        
        Args:
            seq: List to shuffle (modified in-place)
        """
        self._call_count += 1
        self._rng.shuffle(seq)
    
    def get_seed(self) -> Optional[int]:
        """Get the seed used to initialize this RNG."""
        return self._seed
    
    def get_call_count(self) -> int:
        """Get the number of RNG calls made (for debugging)."""
        return self._call_count
    
    def get_state(self) -> tuple:
        """
        Get the internal state of the RNG.
        
        Returns:
            Internal RNG state (can be restored with set_state)
        """
        return self._rng.getstate()
    
    def set_state(self, state: tuple) -> None:
        """
        Restore the internal state of the RNG.
        
        Args:
            state: State tuple from get_state()
        """
        self._rng.setstate(state)


def create_worker_rng(base_seed: int, worker_id: int) -> SpinRNG:
    """
    Create a deterministic RNG for a parallel worker.
    
    This ensures each worker has a unique, deterministic seed that:
    - Doesn't correlate with other workers
    - Is reproducible with same base_seed and worker_id
    - Supports distributed simulation
    
    Args:
        base_seed: Base seed for the simulation run
        worker_id: Unique identifier for this worker
        
    Returns:
        SpinRNG instance with deterministic seed
    """
    # Simple deterministic formula that avoids correlation
    # Using prime multiplier to reduce patterns
    worker_seed = base_seed + (worker_id * 1000003)
    return SpinRNG(worker_seed)


def verify_determinism(seed: int, operations: int = 1000) -> List[float]:
    """
    Helper function to verify RNG determinism.
    
    Args:
        seed: Seed to test
        operations: Number of random operations to perform
        
    Returns:
        List of generated random values
    """
    rng = SpinRNG(seed)
    results = []
    
    for _ in range(operations):
        results.append(rng.random())
    
    return results