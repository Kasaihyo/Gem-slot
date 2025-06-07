"""
Symbol system for Esqueleto Explosivo 3.

This module defines all symbols, their properties, and utility functions
for symbol type checking and manipulation.
"""

from enum import Enum, auto
from typing import Set, Optional


class Symbol(Enum):
    """Enumeration of all symbols in the game."""
    
    # Empty position
    EMPTY = auto()
    
    # High Pay Symbol
    LADY_SK = auto()  # Lady Skull (Red)
    
    # Low Pay Symbols
    PINK_SK = auto()   # Pink Skull (Magenta)
    GREEN_SK = auto()  # Green Skull (Green)
    BLUE_SK = auto()   # Blue Skull (Blue)
    ORANGE_SK = auto() # Orange Skull (Yellow)
    CYAN_SK = auto()   # Cyan Skull (Cyan)
    
    # Wild Symbols
    WILD = auto()      # Regular Wild (White)
    E_WILD = auto()    # Explosivo Wild (Bright Yellow)
    
    # Special Symbol
    SCATTER = auto()   # Scatter (Bright Magenta)


# Symbol display mappings for visualization
SYMBOL_DISPLAY = {
    Symbol.EMPTY: "   ",
    Symbol.LADY_SK: "LDY",
    Symbol.PINK_SK: "PNK",
    Symbol.GREEN_SK: "GRN",
    Symbol.BLUE_SK: "BLU",
    Symbol.ORANGE_SK: "ORG",
    Symbol.CYAN_SK: "CYN",
    Symbol.WILD: "WLD",
    Symbol.E_WILD: "EW ",
    Symbol.SCATTER: "SCR"
}

# Symbol to string mapping (matches config.py keys)
SYMBOL_TO_STRING = {
    Symbol.LADY_SK: "LADY_SK",
    Symbol.PINK_SK: "PINK_SK",
    Symbol.GREEN_SK: "GREEN_SK",
    Symbol.BLUE_SK: "BLUE_SK",
    Symbol.ORANGE_SK: "ORANGE_SK",
    Symbol.CYAN_SK: "CYAN_SK",
    Symbol.WILD: "WILD",
    Symbol.E_WILD: "E_WILD",
    Symbol.SCATTER: "SCATTER"
}

# String to symbol mapping (reverse of above)
STRING_TO_SYMBOL = {v: k for k, v in SYMBOL_TO_STRING.items()}

# Symbol categories
HIGH_PAY_SYMBOLS: Set[Symbol] = {Symbol.LADY_SK}
LOW_PAY_SYMBOLS: Set[Symbol] = {
    Symbol.PINK_SK, Symbol.GREEN_SK, Symbol.BLUE_SK,
    Symbol.ORANGE_SK, Symbol.CYAN_SK
}
PAYING_SYMBOLS: Set[Symbol] = HIGH_PAY_SYMBOLS | LOW_PAY_SYMBOLS
WILD_SYMBOLS: Set[Symbol] = {Symbol.WILD, Symbol.E_WILD}
SPECIAL_SYMBOLS: Set[Symbol] = {Symbol.SCATTER}
ALL_SYMBOLS: Set[Symbol] = PAYING_SYMBOLS | WILD_SYMBOLS | SPECIAL_SYMBOLS


def is_empty(symbol: Symbol) -> bool:
    """Check if a position is empty."""
    return symbol == Symbol.EMPTY


def is_high_pay(symbol: Symbol) -> bool:
    """Check if symbol is a high-pay symbol."""
    return symbol in HIGH_PAY_SYMBOLS


def is_low_pay(symbol: Symbol) -> bool:
    """Check if symbol is a low-pay symbol."""
    return symbol in LOW_PAY_SYMBOLS


def is_paying(symbol: Symbol) -> bool:
    """Check if symbol is a paying symbol (high or low pay)."""
    return symbol in PAYING_SYMBOLS


def is_wild(symbol: Symbol) -> bool:
    """Check if symbol is any type of wild."""
    return symbol in WILD_SYMBOLS


def is_regular_wild(symbol: Symbol) -> bool:
    """Check if symbol is a regular wild (not explosivo)."""
    return symbol == Symbol.WILD


def is_explosivo_wild(symbol: Symbol) -> bool:
    """Check if symbol is an explosivo wild."""
    return symbol == Symbol.E_WILD


def is_scatter(symbol: Symbol) -> bool:
    """Check if symbol is a scatter."""
    return symbol == Symbol.SCATTER


def is_special(symbol: Symbol) -> bool:
    """Check if symbol is a special symbol (scatter)."""
    return symbol in SPECIAL_SYMBOLS


def can_be_destroyed_by_explosion(symbol: Symbol) -> bool:
    """
    Check if symbol can be destroyed by explosivo wild explosion.
    Only low-pay symbols can be destroyed.
    """
    return is_low_pay(symbol)


def can_substitute(wild: Symbol, target: Symbol) -> bool:
    """
    Check if a wild symbol can substitute for a target symbol.
    Wilds can substitute for all paying symbols but not scatters.
    """
    if not is_wild(wild):
        return False
    return is_paying(target)


def get_display_string(symbol: Symbol) -> str:
    """Get the 3-character display string for a symbol."""
    return SYMBOL_DISPLAY.get(symbol, "???")


def get_config_string(symbol: Symbol) -> str:
    """Get the configuration string key for a symbol."""
    return SYMBOL_TO_STRING.get(symbol, "")


def from_config_string(config_str: str) -> Optional[Symbol]:
    """Convert a configuration string to a Symbol."""
    return STRING_TO_SYMBOL.get(config_str)


def symbols_match_for_cluster(symbol1: Symbol, symbol2: Symbol) -> bool:
    """
    Check if two symbols can form a cluster together.
    Paying symbols match with same type or wilds.
    Wilds match with any paying symbol or other wilds.
    Scatters don't match with anything.
    """
    # Empty positions don't match
    if is_empty(symbol1) or is_empty(symbol2):
        return False
    
    # Scatters don't participate in clusters
    if is_scatter(symbol1) or is_scatter(symbol2):
        return False
    
    # If both are wilds, they match
    if is_wild(symbol1) and is_wild(symbol2):
        return True
    
    # If one is wild and other is paying, they match
    if is_wild(symbol1) and is_paying(symbol2):
        return True
    if is_wild(symbol2) and is_paying(symbol1):
        return True
    
    # Two paying symbols match only if they're the same type
    if is_paying(symbol1) and is_paying(symbol2):
        return symbol1 == symbol2
    
    return False