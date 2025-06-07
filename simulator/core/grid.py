"""
Core grid implementation for Esqueleto Explosivo 3.

This module provides the fundamental 5x5 grid system including the grid
data structure, gravity mechanics, and symbol dropping functionality.
"""

from typing import List, Tuple, Optional, Dict, Set
import copy
from simulator.core.symbol import (
    Symbol, is_empty, get_display_string, from_config_string,
    get_config_string
)
from simulator.core.rng import SpinRNG
from simulator import config
import numpy as np


# Grid dimensions
ROWS = 5
COLS = 5
TOTAL_POSITIONS = ROWS * COLS


class Grid:
    """
    5x5 game grid implementation.
    
    The grid uses row-major ordering with positions indexed as:
    - Row 0-4 (top to bottom)
    - Column 0-4 (left to right)
    """
    
    def __init__(self):
        """Initialize an empty 5x5 grid."""
        # Using a flat list for better performance
        # Position (row, col) maps to index: row * COLS + col
        self._symbols: List[Symbol] = [Symbol.EMPTY] * TOTAL_POSITIONS
        self._cached_symbol_counts: Optional[Dict[Symbol, int]] = None
    
    def _invalidate_cache(self):
        """Invalidate cached computations when grid changes."""
        self._cached_symbol_counts = None
    
    def _pos_to_index(self, row: int, col: int) -> int:
        """Convert (row, col) position to flat index."""
        return row * COLS + col
    
    def _index_to_pos(self, index: int) -> Tuple[int, int]:
        """Convert flat index to (row, col) position."""
        return divmod(index, COLS)
    
    def _validate_position(self, row: int, col: int) -> None:
        """Validate that position is within grid bounds."""
        if not (0 <= row < ROWS and 0 <= col < COLS):
            raise ValueError(f"Position ({row}, {col}) out of bounds")
    
    def get_symbol(self, row: int, col: int) -> Symbol:
        """Get symbol at specified position."""
        self._validate_position(row, col)
        return self._symbols[self._pos_to_index(row, col)]
    
    def set_symbol(self, row: int, col: int, symbol: Symbol) -> None:
        """Set symbol at specified position."""
        self._validate_position(row, col)
        self._symbols[self._pos_to_index(row, col)] = symbol
        self._invalidate_cache()
    
    def is_empty(self, row: int, col: int) -> bool:
        """Check if position is empty."""
        return is_empty(self.get_symbol(row, col))
    
    def clear(self) -> None:
        """Clear the entire grid."""
        self._symbols = [Symbol.EMPTY] * TOTAL_POSITIONS
        self._invalidate_cache()
    
    def copy(self) -> 'Grid':
        """Create a deep copy of the grid."""
        new_grid = Grid()
        new_grid._symbols = self._symbols.copy()
        return new_grid
    
    def get_all_positions(self) -> List[Tuple[int, int]]:
        """Get all valid grid positions."""
        return [(row, col) for row in range(ROWS) for col in range(COLS)]
    
    def count_symbols(self) -> Dict[Symbol, int]:
        """Count occurrences of each symbol type."""
        if self._cached_symbol_counts is None:
            counts = {}
            for symbol in self._symbols:
                counts[symbol] = counts.get(symbol, 0) + 1
            self._cached_symbol_counts = counts
        return self._cached_symbol_counts.copy()
    
    def count_symbol(self, symbol: Symbol) -> int:
        """Count occurrences of a specific symbol."""
        return self.count_symbols().get(symbol, 0)
    
    def find_all_positions(self, symbol: Symbol) -> List[Tuple[int, int]]:
        """Find all positions containing a specific symbol."""
        positions = []
        for idx, sym in enumerate(self._symbols):
            if sym == symbol:
                positions.append(self._index_to_pos(idx))
        return positions
    
    def get_column(self, col: int) -> List[Symbol]:
        """Get all symbols in a column (top to bottom)."""
        if not 0 <= col < COLS:
            raise ValueError(f"Column {col} out of bounds")
        return [self._symbols[row * COLS + col] for row in range(ROWS)]
    
    def get_row(self, row: int) -> List[Symbol]:
        """Get all symbols in a row (left to right)."""
        if not 0 <= row < ROWS:
            raise ValueError(f"Row {row} out of bounds")
        start_idx = row * COLS
        return self._symbols[start_idx:start_idx + COLS]
    
    def apply_gravity(self) -> bool:
        """
        Apply gravity to make symbols fall down.
        
        Returns:
            True if any symbols moved, False otherwise
        """
        moved = False
        
        # Process each column independently
        for col in range(COLS):
            # Extract non-empty symbols from top to bottom (preserve order)
            symbols = []
            symbol_positions = []  # Track original positions
            
            for row in range(ROWS):
                symbol = self.get_symbol(row, col)
                if not is_empty(symbol):
                    symbols.append(symbol)
                    symbol_positions.append(row)
            
            # If no symbols or column is full, skip
            if not symbols or len(symbols) == ROWS:
                continue
            
            # Calculate where symbols should be after gravity
            expected_positions = list(range(ROWS - len(symbols), ROWS))
            
            # Check if any symbol needs to move
            if symbol_positions == expected_positions:
                continue  # Already in correct positions
            
            # Clear the column and place symbols at bottom
            for row in range(ROWS):
                self._symbols[self._pos_to_index(row, col)] = Symbol.EMPTY
            
            # Place symbols from bottom
            for i, symbol in enumerate(symbols):
                self._symbols[self._pos_to_index(expected_positions[i], col)] = symbol
            
            self._invalidate_cache()
            moved = True
        
        return moved
    
    def _count_empty_in_column(self, col: int) -> int:
        """Count empty positions in a column."""
        count = 0
        for row in range(ROWS):
            if is_empty(self.get_symbol(row, col)):
                count += 1
        return count
    
    def drop_new_symbols(self, rng: SpinRNG, is_free_spins: bool = False) -> int:
        """
        Drop new symbols into empty positions.
        
        Args:
            rng: Random number generator
            is_free_spins: Whether to use free spins weights
            
        Returns:
            Number of symbols dropped
        """
        # Choose appropriate weights
        if is_free_spins:
            symbol_names = config.FS_SYMBOL_NAMES
            weights = config.FS_WEIGHTS
        else:
            symbol_names = config.BG_SYMBOL_NAMES
            weights = config.BG_WEIGHTS
        
        dropped = 0
        
        # Fill empty positions from top to bottom in each column
        for col in range(COLS):
            for row in range(ROWS):
                if is_empty(self.get_symbol(row, col)):
                    # Generate new symbol using weighted choice
                    config_str = rng.weighted_choice_numpy(symbol_names, weights)
                    symbol = from_config_string(config_str)
                    if symbol:
                        self.set_symbol(row, col, symbol)
                        dropped += 1
        
        return dropped
    
    def remove_positions(self, positions: List[Tuple[int, int]]) -> None:
        """Remove symbols at specified positions (set to empty)."""
        for row, col in positions:
            self.set_symbol(row, col, Symbol.EMPTY)
    
    def to_string(self, show_coordinates: bool = True) -> str:
        """
        Convert grid to ASCII string representation.
        
        Args:
            show_coordinates: Whether to show row/column labels
            
        Returns:
            ASCII representation of the grid
        """
        lines = []
        
        # Top border
        lines.append("┌─────" + "┬─────" * (COLS - 1) + "┐")
        
        # Grid content
        for row in range(ROWS):
            row_symbols = []
            for col in range(COLS):
                symbol = self.get_symbol(row, col)
                row_symbols.append(f" {get_display_string(symbol)} ")
            
            line = "│" + "│".join(row_symbols) + "│"
            if show_coordinates:
                line += f"  Row {row}"
            lines.append(line)
            
            # Horizontal separator (except after last row)
            if row < ROWS - 1:
                lines.append("├─────" + "┼─────" * (COLS - 1) + "┤")
        
        # Bottom border
        lines.append("└─────" + "┴─────" * (COLS - 1) + "┘")
        
        # Column labels
        if show_coordinates:
            col_labels = "  "
            for col in range(COLS):
                col_labels += f"Col{col}  "
            lines.append(col_labels)
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        """String representation of the grid."""
        return self.to_string()
    
    def __repr__(self) -> str:
        """Developer representation of the grid."""
        symbol_counts = self.count_symbols()
        non_empty = sum(count for sym, count in symbol_counts.items() 
                       if sym != Symbol.EMPTY)
        return f"<Grid: {non_empty}/25 symbols>"
    
    def validate(self) -> bool:
        """
        Validate grid integrity.
        
        Returns:
            True if grid is valid, False otherwise
        """
        # Check grid has correct size
        if len(self._symbols) != TOTAL_POSITIONS:
            return False
        
        # Check all positions contain valid symbols
        for symbol in self._symbols:
            if not isinstance(symbol, Symbol):
                return False
        
        return True
    
    def to_state(self) -> List[str]:
        """
        Serialize grid state to list of symbol strings.
        
        Returns:
            List of symbol configuration strings
        """
        return [get_config_string(sym) if sym != Symbol.EMPTY else "" 
                for sym in self._symbols]
    
    def from_state(self, state: List[str]) -> None:
        """
        Restore grid from serialized state.
        
        Args:
            state: List of symbol configuration strings
        """
        if len(state) != TOTAL_POSITIONS:
            raise ValueError(f"Invalid state size: {len(state)}")
        
        self._symbols = []
        for config_str in state:
            if config_str:
                symbol = from_config_string(config_str)
                if symbol is None:
                    raise ValueError(f"Invalid symbol string: {config_str}")
                self._symbols.append(symbol)
            else:
                self._symbols.append(Symbol.EMPTY)
        
        self._invalidate_cache()


def create_test_grid() -> Grid:
    """Create a test grid with some symbols for testing."""
    grid = Grid()
    
    # Add some test symbols
    grid.set_symbol(0, 0, Symbol.LADY_SK)
    grid.set_symbol(0, 1, Symbol.PINK_SK)
    grid.set_symbol(1, 1, Symbol.WILD)
    grid.set_symbol(2, 2, Symbol.E_WILD)
    grid.set_symbol(4, 0, Symbol.SCATTER)
    grid.set_symbol(4, 4, Symbol.SCATTER)
    
    return grid