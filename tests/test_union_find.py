"""Unit tests for Union-Find data structure."""

import pytest
from simulator.core.union_find import UnionFind, GridUnionFind


class TestUnionFind:
    """Test basic Union-Find operations."""
    
    def test_initialization(self):
        """Test Union-Find initialization."""
        uf = UnionFind(10)
        
        assert uf.size == 10
        assert uf.num_sets() == 10
        
        # Each element should be its own parent
        for i in range(10):
            assert uf.find(i) == i
    
    def test_union_operations(self):
        """Test union operations."""
        uf = UnionFind(5)
        
        # Union 0 and 1
        assert uf.union(0, 1) == True
        assert uf.connected(0, 1) == True
        assert uf.num_sets() == 4
        
        # Union 2 and 3
        assert uf.union(2, 3) == True
        assert uf.connected(2, 3) == True
        assert uf.num_sets() == 3
        
        # Union already connected elements
        assert uf.union(0, 1) == False
        assert uf.num_sets() == 3
        
        # Union two sets
        assert uf.union(1, 2) == True
        assert uf.connected(0, 3) == True  # 0-1-2-3 all connected
        assert uf.num_sets() == 2
    
    def test_find_with_path_compression(self):
        """Test find operation with path compression."""
        uf = UnionFind(6)
        
        # Create a chain: 0 -> 1 -> 2 -> 3
        uf.union(0, 1)
        uf.union(1, 2)
        uf.union(2, 3)
        
        # Find should compress the path
        root = uf.find(0)
        
        # After path compression, 0 should point directly to root
        assert uf.parent[0] == root
    
    def test_get_sets(self):
        """Test getting all disjoint sets."""
        uf = UnionFind(6)
        
        # Create sets: {0,1,2}, {3,4}, {5}
        uf.union(0, 1)
        uf.union(1, 2)
        uf.union(3, 4)
        
        sets = uf.get_sets()
        
        # Should have 3 sets
        assert len(sets) == 3
        
        # Check set sizes
        set_sizes = sorted([len(s) for s in sets.values()])
        assert set_sizes == [1, 2, 3]
    
    def test_get_set_size(self):
        """Test getting size of a set."""
        uf = UnionFind(5)
        
        # Initially all sets have size 1
        assert uf.get_set_size(0) == 1
        
        # Union some elements
        uf.union(0, 1)
        uf.union(1, 2)
        
        # Check sizes
        assert uf.get_set_size(0) == 3
        assert uf.get_set_size(1) == 3
        assert uf.get_set_size(2) == 3
        assert uf.get_set_size(3) == 1
    
    def test_reset(self):
        """Test reset functionality."""
        uf = UnionFind(4)
        
        # Create some unions
        uf.union(0, 1)
        uf.union(2, 3)
        assert uf.num_sets() == 2
        
        # Reset
        uf.reset()
        
        # Should be back to initial state
        assert uf.num_sets() == 4
        for i in range(4):
            assert uf.find(i) == i
        assert not uf.connected(0, 1)
        assert not uf.connected(2, 3)
    
    def test_get_set_members(self):
        """Test getting members of a set."""
        uf = UnionFind(5)
        
        # Create set {0,1,2}
        uf.union(0, 1)
        uf.union(1, 2)
        
        members = uf.get_set_members(1)
        assert sorted(members) == [0, 1, 2]
        
        # Singleton set
        members = uf.get_set_members(3)
        assert members == [3]


class TestGridUnionFind:
    """Test grid-specific Union-Find operations."""
    
    def test_grid_initialization(self):
        """Test grid Union-Find initialization."""
        guf = GridUnionFind()
        
        assert guf.size == 25  # 5x5 grid
        assert guf.rows == 5
        assert guf.cols == 5
    
    def test_position_conversion(self):
        """Test position to index conversion."""
        guf = GridUnionFind()
        
        # Test conversions
        assert guf._pos_to_index(0, 0) == 0
        assert guf._pos_to_index(0, 4) == 4
        assert guf._pos_to_index(1, 0) == 5
        assert guf._pos_to_index(4, 4) == 24
        
        # Test reverse conversion
        assert guf._index_to_pos(0) == (0, 0)
        assert guf._index_to_pos(4) == (0, 4)
        assert guf._index_to_pos(5) == (1, 0)
        assert guf._index_to_pos(24) == (4, 4)
    
    def test_union_positions(self):
        """Test unioning grid positions."""
        guf = GridUnionFind()
        
        # Union adjacent positions
        assert guf.union_positions(0, 0, 0, 1) == True
        assert guf.union_positions(0, 1, 0, 2) == True
        
        # Check they're connected
        assert guf.connected(0, 2)  # indices 0 and 2
        
        # Check through position finding
        assert guf.find_position(0, 0) == guf.find_position(0, 2)
    
    def test_get_cluster_positions(self):
        """Test getting cluster positions."""
        guf = GridUnionFind()
        
        # Create a cluster
        guf.union_positions(1, 1, 1, 2)
        guf.union_positions(1, 2, 1, 3)
        guf.union_positions(1, 1, 2, 1)
        
        # Get cluster positions
        positions = guf.get_cluster_positions(1, 2)
        
        assert len(positions) == 4
        assert (1, 1) in positions
        assert (1, 2) in positions
        assert (1, 3) in positions
        assert (2, 1) in positions


class TestUnionFindPerformance:
    """Test Union-Find performance characteristics."""
    
    def test_large_scale_operations(self):
        """Test performance with many operations."""
        uf = UnionFind(1000)
        
        # Perform many unions
        for i in range(0, 1000, 2):
            uf.union(i, i + 1)
        
        # Should have 500 sets
        assert uf.num_sets() == 500
        
        # Union some of the pairs
        for i in range(0, 500, 4):
            uf.union(i, i + 2)
        
        # Find operations should still be fast
        for i in range(1000):
            _ = uf.find(i)
    
    def test_worst_case_path_compression(self):
        """Test path compression in worst case."""
        uf = UnionFind(100)
        
        # Create a long chain
        for i in range(99):
            uf.union(i, i + 1)
        
        # This should trigger path compression
        assert uf.find(0) == uf.find(99)
        
        # Now all finds should be O(1)
        for i in range(100):
            assert uf.find(i) == uf.find(0)


if __name__ == "__main__":
    pytest.main([__file__])