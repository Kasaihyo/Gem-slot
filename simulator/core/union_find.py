"""
Union-Find (Disjoint Set Union) data structure for efficient cluster detection.

This module provides an optimized Union-Find implementation specifically
designed for the 5x5 grid cluster detection in Esqueleto Explosivo 3.
"""

from typing import List, Set, Dict


class UnionFind:
    """
    Union-Find data structure with path compression and union by rank.
    
    Optimized for cluster detection in a 5x5 grid (25 positions).
    Provides near O(1) amortized time complexity for operations.
    """
    
    def __init__(self, size: int = 25):
        """
        Initialize Union-Find structure.
        
        Args:
            size: Number of elements (default 25 for 5x5 grid)
        """
        self.size = size
        self.parent = list(range(size))  # Each element is its own parent initially
        self.rank = [0] * size  # Rank for union by rank optimization
        self._num_sets = size  # Track number of disjoint sets
    
    def find(self, x: int) -> int:
        """
        Find the root of the set containing element x.
        
        Uses path compression to flatten the tree structure,
        ensuring near O(1) amortized complexity.
        
        Args:
            x: Element to find the root of
            
        Returns:
            Root element of the set containing x
        """
        if self.parent[x] != x:
            # Path compression: make all nodes point directly to root
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int) -> bool:
        """
        Unite the sets containing elements x and y.
        
        Uses union by rank to keep trees balanced.
        
        Args:
            x: First element
            y: Second element
            
        Returns:
            True if sets were merged, False if already in same set
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False  # Already in same set
        
        # Union by rank: attach smaller tree under larger tree
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            # Same rank: attach y to x and increment x's rank
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        
        self._num_sets -= 1
        return True
    
    def connected(self, x: int, y: int) -> bool:
        """
        Check if two elements are in the same set.
        
        Args:
            x: First element
            y: Second element
            
        Returns:
            True if elements are in the same set
        """
        return self.find(x) == self.find(y)
    
    def reset(self) -> None:
        """
        Reset the Union-Find structure to initial state.
        
        Efficient reset for reuse without reallocation.
        """
        for i in range(self.size):
            self.parent[i] = i
            self.rank[i] = 0
        self._num_sets = self.size
    
    def get_sets(self) -> Dict[int, List[int]]:
        """
        Get all disjoint sets as a dictionary.
        
        Returns:
            Dictionary mapping root elements to lists of elements in each set
        """
        sets: Dict[int, List[int]] = {}
        
        for i in range(self.size):
            root = self.find(i)
            if root not in sets:
                sets[root] = []
            sets[root].append(i)
        
        return sets
    
    def get_set_size(self, x: int) -> int:
        """
        Get the size of the set containing element x.
        
        Args:
            x: Element to check
            
        Returns:
            Size of the set containing x
        """
        root = self.find(x)
        count = 0
        for i in range(self.size):
            if self.find(i) == root:
                count += 1
        return count
    
    def num_sets(self) -> int:
        """
        Get the current number of disjoint sets.
        
        Returns:
            Number of disjoint sets
        """
        return self._num_sets
    
    def get_set_members(self, x: int) -> List[int]:
        """
        Get all members of the set containing element x.
        
        Args:
            x: Element whose set to retrieve
            
        Returns:
            List of all elements in the same set as x
        """
        root = self.find(x)
        members = []
        for i in range(self.size):
            if self.find(i) == root:
                members.append(i)
        return members


class GridUnionFind(UnionFind):
    """
    Specialized Union-Find for 5x5 grid operations.
    
    Provides grid-specific helper methods for cluster detection.
    """
    
    def __init__(self):
        """Initialize for 5x5 grid (25 positions)."""
        super().__init__(25)
        self.rows = 5
        self.cols = 5
    
    def _pos_to_index(self, row: int, col: int) -> int:
        """Convert grid position to linear index."""
        return row * self.cols + col
    
    def _index_to_pos(self, index: int) -> tuple[int, int]:
        """Convert linear index to grid position."""
        return divmod(index, self.cols)
    
    def union_positions(self, row1: int, col1: int, row2: int, col2: int) -> bool:
        """
        Unite two grid positions.
        
        Args:
            row1, col1: First position
            row2, col2: Second position
            
        Returns:
            True if positions were merged
        """
        idx1 = self._pos_to_index(row1, col1)
        idx2 = self._pos_to_index(row2, col2)
        return self.union(idx1, idx2)
    
    def find_position(self, row: int, col: int) -> int:
        """Find root of grid position."""
        return self.find(self._pos_to_index(row, col))
    
    def get_cluster_positions(self, row: int, col: int) -> List[tuple[int, int]]:
        """
        Get all positions in the same cluster as the given position.
        
        Args:
            row, col: Position to check
            
        Returns:
            List of (row, col) tuples in the same cluster
        """
        index = self._pos_to_index(row, col)
        members = self.get_set_members(index)
        return [self._index_to_pos(idx) for idx in members]