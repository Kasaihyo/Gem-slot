"""Unit tests for grid system."""

import pytest
from simulator.core.grid import Grid, ROWS, COLS, TOTAL_POSITIONS, create_test_grid
from simulator.core.symbol import Symbol
from simulator.core.rng import SpinRNG


class TestGridBasics:
    """Test basic grid functionality."""
    
    def test_grid_initialization(self):
        """Test grid initializes empty."""
        grid = Grid()
        
        # Check all positions are empty
        for row in range(ROWS):
            for col in range(COLS):
                assert grid.is_empty(row, col)
        
        # Check dimensions
        assert len(grid._symbols) == TOTAL_POSITIONS
        assert ROWS == 5
        assert COLS == 5
    
    def test_position_validation(self):
        """Test position boundary validation."""
        grid = Grid()
        
        # Valid positions
        grid.get_symbol(0, 0)  # Top-left
        grid.get_symbol(4, 4)  # Bottom-right
        
        # Invalid positions
        with pytest.raises(ValueError):
            grid.get_symbol(-1, 0)
        with pytest.raises(ValueError):
            grid.get_symbol(0, -1)
        with pytest.raises(ValueError):
            grid.get_symbol(5, 0)
        with pytest.raises(ValueError):
            grid.get_symbol(0, 5)
    
    def test_symbol_get_set(self):
        """Test getting and setting symbols."""
        grid = Grid()
        
        # Set and get
        grid.set_symbol(2, 3, Symbol.LADY_SK)
        assert grid.get_symbol(2, 3) == Symbol.LADY_SK
        assert not grid.is_empty(2, 3)
        
        # Other positions remain empty
        assert grid.is_empty(2, 2)
        assert grid.is_empty(2, 4)
    
    def test_grid_copy(self):
        """Test grid deep copy."""
        grid1 = Grid()
        grid1.set_symbol(1, 1, Symbol.WILD)
        grid1.set_symbol(2, 2, Symbol.PINK_SK)
        
        # Copy grid
        grid2 = grid1.copy()
        
        # Check copy has same content
        assert grid2.get_symbol(1, 1) == Symbol.WILD
        assert grid2.get_symbol(2, 2) == Symbol.PINK_SK
        
        # Modify original
        grid1.set_symbol(1, 1, Symbol.SCATTER)
        
        # Copy should be unchanged
        assert grid2.get_symbol(1, 1) == Symbol.WILD
    
    def test_grid_clear(self):
        """Test clearing the grid."""
        grid = Grid()
        grid.set_symbol(0, 0, Symbol.LADY_SK)
        grid.set_symbol(2, 2, Symbol.WILD)
        
        # Clear grid
        grid.clear()
        
        # All positions should be empty
        for row in range(ROWS):
            for col in range(COLS):
                assert grid.is_empty(row, col)


class TestGridQueries:
    """Test grid query operations."""
    
    def test_count_symbols(self):
        """Test symbol counting."""
        grid = Grid()
        
        # Empty grid
        counts = grid.count_symbols()
        assert counts.get(Symbol.EMPTY, 0) == 25
        
        # Add symbols
        grid.set_symbol(0, 0, Symbol.LADY_SK)
        grid.set_symbol(0, 1, Symbol.LADY_SK)
        grid.set_symbol(1, 0, Symbol.PINK_SK)
        
        counts = grid.count_symbols()
        assert counts.get(Symbol.LADY_SK, 0) == 2
        assert counts.get(Symbol.PINK_SK, 0) == 1
        assert counts.get(Symbol.EMPTY, 0) == 22
    
    def test_count_specific_symbol(self):
        """Test counting specific symbol."""
        grid = Grid()
        
        assert grid.count_symbol(Symbol.WILD) == 0
        
        grid.set_symbol(0, 0, Symbol.WILD)
        grid.set_symbol(2, 2, Symbol.WILD)
        
        assert grid.count_symbol(Symbol.WILD) == 2
        assert grid.count_symbol(Symbol.LADY_SK) == 0
    
    def test_find_all_positions(self):
        """Test finding all positions of a symbol."""
        grid = Grid()
        
        # Add scatters
        grid.set_symbol(0, 0, Symbol.SCATTER)
        grid.set_symbol(2, 3, Symbol.SCATTER)
        grid.set_symbol(4, 4, Symbol.SCATTER)
        
        positions = grid.find_all_positions(Symbol.SCATTER)
        assert len(positions) == 3
        assert (0, 0) in positions
        assert (2, 3) in positions
        assert (4, 4) in positions
        
        # No wilds
        assert grid.find_all_positions(Symbol.WILD) == []
    
    def test_get_column(self):
        """Test getting column symbols."""
        grid = Grid()
        
        # Fill column 2
        for row in range(ROWS):
            grid.set_symbol(row, 2, Symbol.PINK_SK)
        
        col_symbols = grid.get_column(2)
        assert len(col_symbols) == ROWS
        assert all(sym == Symbol.PINK_SK for sym in col_symbols)
        
        # Invalid column
        with pytest.raises(ValueError):
            grid.get_column(5)
    
    def test_get_row(self):
        """Test getting row symbols."""
        grid = Grid()
        
        # Fill row 1
        for col in range(COLS):
            grid.set_symbol(1, col, Symbol.GREEN_SK)
        
        row_symbols = grid.get_row(1)
        assert len(row_symbols) == COLS
        assert all(sym == Symbol.GREEN_SK for sym in row_symbols)
        
        # Invalid row
        with pytest.raises(ValueError):
            grid.get_row(5)


class TestGravitySystem:
    """Test gravity mechanics."""
    
    def test_simple_gravity(self):
        """Test basic gravity with single symbol."""
        grid = Grid()
        
        # Place symbol in air
        grid.set_symbol(1, 2, Symbol.LADY_SK)
        
        # Apply gravity
        moved = grid.apply_gravity()
        assert moved
        
        # Symbol should fall to bottom
        assert grid.is_empty(1, 2)
        assert grid.get_symbol(4, 2) == Symbol.LADY_SK
    
    def test_multiple_symbols_gravity(self):
        """Test gravity with multiple symbols in column."""
        grid = Grid()
        
        # Create floating symbols
        grid.set_symbol(0, 1, Symbol.PINK_SK)
        grid.set_symbol(2, 1, Symbol.GREEN_SK)
        
        # Apply gravity
        moved = grid.apply_gravity()
        assert moved
        
        # Check final positions (order preserved)
        assert grid.get_symbol(3, 1) == Symbol.PINK_SK  # Was at row 0
        assert grid.get_symbol(4, 1) == Symbol.GREEN_SK  # Was at row 2
        assert grid.is_empty(0, 1)
        assert grid.is_empty(2, 1)
    
    def test_no_gravity_needed(self):
        """Test when no gravity is needed."""
        grid = Grid()
        
        # Fill bottom row
        for col in range(COLS):
            grid.set_symbol(4, col, Symbol.WILD)
        
        # Apply gravity
        moved = grid.apply_gravity()
        
        
        assert not moved  # Nothing should move
        
        # Check positions unchanged
        for col in range(COLS):
            assert grid.get_symbol(4, col) == Symbol.WILD
    
    def test_complex_gravity(self):
        """Test complex gravity scenario."""
        grid = Grid()
        
        # Setup:
        # Column 0: symbols at rows 0, 2, 3
        grid.set_symbol(0, 0, Symbol.LADY_SK)
        grid.set_symbol(2, 0, Symbol.PINK_SK)
        grid.set_symbol(3, 0, Symbol.GREEN_SK)
        
        # Apply gravity
        grid.apply_gravity()
        
        # Should compact to bottom
        assert grid.get_symbol(2, 0) == Symbol.LADY_SK
        assert grid.get_symbol(3, 0) == Symbol.PINK_SK
        assert grid.get_symbol(4, 0) == Symbol.GREEN_SK
        assert grid.is_empty(0, 0)
        assert grid.is_empty(1, 0)


class TestSymbolDropping:
    """Test symbol dropping mechanism."""
    
    def test_drop_fills_empty(self):
        """Test dropping fills all empty positions."""
        grid = Grid()
        rng = SpinRNG(42)
        
        # Create some empty positions
        grid.set_symbol(4, 0, Symbol.LADY_SK)
        grid.set_symbol(4, 1, Symbol.PINK_SK)
        
        # Drop new symbols
        dropped = grid.drop_new_symbols(rng, is_free_spins=False)
        
        # Should fill 23 positions
        assert dropped == 23
        
        # No empty positions remain
        for row in range(ROWS):
            for col in range(COLS):
                assert not grid.is_empty(row, col)
    
    def test_drop_deterministic(self):
        """Test symbol dropping is deterministic."""
        grid1 = Grid()
        grid2 = Grid()
        
        rng1 = SpinRNG(12345)
        rng2 = SpinRNG(12345)
        
        # Drop in both grids
        grid1.drop_new_symbols(rng1, is_free_spins=False)
        grid2.drop_new_symbols(rng2, is_free_spins=False)
        
        # Should be identical
        for row in range(ROWS):
            for col in range(COLS):
                assert grid1.get_symbol(row, col) == grid2.get_symbol(row, col)
    
    def test_free_spins_weights(self):
        """Test free spins use different weights."""
        grid = Grid()
        rng = SpinRNG(42)
        
        # Drop with free spins weights
        grid.drop_new_symbols(rng, is_free_spins=True)
        
        # Should have no explosivo wilds in free spins
        assert grid.count_symbol(Symbol.E_WILD) == 0
        
        # Should have more regular wilds than base game
        # (Can't test exact distribution in unit test, that's for integration tests)


class TestGridVisualization:
    """Test grid visualization and display."""
    
    def test_ascii_display(self):
        """Test ASCII grid representation."""
        grid = Grid()
        grid.set_symbol(0, 0, Symbol.LADY_SK)
        grid.set_symbol(1, 1, Symbol.WILD)
        grid.set_symbol(2, 2, Symbol.E_WILD)
        grid.set_symbol(3, 3, Symbol.SCATTER)
        grid.set_symbol(4, 4, Symbol.PINK_SK)
        
        display = grid.to_string(show_coordinates=True)
        
        # Check key elements appear
        assert "LDY" in display
        assert "WLD" in display
        assert "EW " in display
        assert "SCR" in display
        assert "PNK" in display
        assert "Row 0" in display
        assert "Col0" in display
    
    def test_grid_repr(self):
        """Test grid representation."""
        grid = Grid()
        
        # Empty grid
        assert "0/25 symbols" in repr(grid)
        
        # Add some symbols
        grid.set_symbol(0, 0, Symbol.LADY_SK)
        grid.set_symbol(1, 1, Symbol.WILD)
        
        assert "2/25 symbols" in repr(grid)


class TestGridSerialization:
    """Test grid state serialization."""
    
    def test_state_serialization(self):
        """Test converting grid to/from state."""
        grid = Grid()
        
        # Setup grid
        grid.set_symbol(0, 0, Symbol.LADY_SK)
        grid.set_symbol(1, 1, Symbol.WILD)
        grid.set_symbol(2, 2, Symbol.E_WILD)
        grid.set_symbol(3, 3, Symbol.SCATTER)
        
        # Serialize
        state = grid.to_state()
        assert len(state) == TOTAL_POSITIONS
        assert state[0] == "LADY_SK"  # Position (0,0)
        assert state[6] == "WILD"      # Position (1,1)
        assert state[12] == "E_WILD"   # Position (2,2)
        assert state[18] == "SCATTER"  # Position (3,3)
        assert state[1] == ""          # Empty position
        
        # Deserialize to new grid
        new_grid = Grid()
        new_grid.from_state(state)
        
        # Check restoration
        assert new_grid.get_symbol(0, 0) == Symbol.LADY_SK
        assert new_grid.get_symbol(1, 1) == Symbol.WILD
        assert new_grid.get_symbol(2, 2) == Symbol.E_WILD
        assert new_grid.get_symbol(3, 3) == Symbol.SCATTER
        assert new_grid.is_empty(0, 1)
    
    def test_invalid_state(self):
        """Test error handling for invalid states."""
        grid = Grid()
        
        # Wrong size
        with pytest.raises(ValueError):
            grid.from_state(["LADY_SK"] * 10)
        
        # Invalid symbol
        with pytest.raises(ValueError):
            grid.from_state(["INVALID_SYMBOL"] + [""] * 24)


class TestGridUtilities:
    """Test utility functions and helpers."""
    
    def test_create_test_grid(self):
        """Test the test grid creation helper."""
        grid = create_test_grid()
        
        # Check expected symbols
        assert grid.get_symbol(0, 0) == Symbol.LADY_SK
        assert grid.get_symbol(0, 1) == Symbol.PINK_SK
        assert grid.get_symbol(1, 1) == Symbol.WILD
        assert grid.get_symbol(2, 2) == Symbol.E_WILD
        assert grid.get_symbol(4, 0) == Symbol.SCATTER
        assert grid.get_symbol(4, 4) == Symbol.SCATTER
    
    def test_remove_positions(self):
        """Test removing symbols at positions."""
        grid = Grid()
        
        # Add symbols
        grid.set_symbol(0, 0, Symbol.LADY_SK)
        grid.set_symbol(1, 1, Symbol.WILD)
        grid.set_symbol(2, 2, Symbol.PINK_SK)
        
        # Remove some
        grid.remove_positions([(0, 0), (2, 2)])
        
        # Check removed
        assert grid.is_empty(0, 0)
        assert grid.is_empty(2, 2)
        assert grid.get_symbol(1, 1) == Symbol.WILD  # Not removed
    
    def test_grid_validation(self):
        """Test grid validation."""
        grid = Grid()
        
        # Valid grid
        assert grid.validate()
        
        # Add symbols - still valid
        grid.set_symbol(0, 0, Symbol.LADY_SK)
        assert grid.validate()


if __name__ == "__main__":
    pytest.main([__file__])