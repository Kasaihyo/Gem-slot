"""Unit tests for symbol system."""

import pytest
from simulator.core.symbol import (
    Symbol, is_empty, is_high_pay, is_low_pay, is_paying, is_wild,
    is_regular_wild, is_explosivo_wild, is_scatter, is_special,
    can_be_destroyed_by_explosion, can_substitute, get_display_string,
    get_config_string, from_config_string, symbols_match_for_cluster,
    HIGH_PAY_SYMBOLS, LOW_PAY_SYMBOLS, PAYING_SYMBOLS, WILD_SYMBOLS,
    SPECIAL_SYMBOLS, ALL_SYMBOLS
)


class TestSymbolEnumeration:
    """Test Symbol enumeration and constants."""
    
    def test_all_symbols_defined(self):
        """Test that all 9 game symbols plus empty are defined."""
        expected_symbols = {
            Symbol.EMPTY, Symbol.LADY_SK, Symbol.PINK_SK, Symbol.GREEN_SK,
            Symbol.BLUE_SK, Symbol.ORANGE_SK, Symbol.CYAN_SK, Symbol.WILD,
            Symbol.E_WILD, Symbol.SCATTER
        }
        
        # Check all expected symbols exist
        for symbol in expected_symbols:
            assert isinstance(symbol, Symbol)
    
    def test_symbol_categories(self):
        """Test symbol category sets."""
        # High pay
        assert HIGH_PAY_SYMBOLS == {Symbol.LADY_SK}
        
        # Low pay
        assert LOW_PAY_SYMBOLS == {
            Symbol.PINK_SK, Symbol.GREEN_SK, Symbol.BLUE_SK,
            Symbol.ORANGE_SK, Symbol.CYAN_SK
        }
        
        # Paying symbols
        assert PAYING_SYMBOLS == HIGH_PAY_SYMBOLS | LOW_PAY_SYMBOLS
        assert len(PAYING_SYMBOLS) == 6
        
        # Wild symbols
        assert WILD_SYMBOLS == {Symbol.WILD, Symbol.E_WILD}
        
        # Special symbols
        assert SPECIAL_SYMBOLS == {Symbol.SCATTER}
        
        # All symbols (excluding empty)
        assert ALL_SYMBOLS == PAYING_SYMBOLS | WILD_SYMBOLS | SPECIAL_SYMBOLS
        assert len(ALL_SYMBOLS) == 9


class TestSymbolProperties:
    """Test symbol property checking functions."""
    
    def test_is_empty(self):
        """Test empty symbol detection."""
        assert is_empty(Symbol.EMPTY)
        assert not is_empty(Symbol.LADY_SK)
        assert not is_empty(Symbol.WILD)
    
    def test_is_high_pay(self):
        """Test high pay symbol detection."""
        assert is_high_pay(Symbol.LADY_SK)
        assert not is_high_pay(Symbol.PINK_SK)
        assert not is_high_pay(Symbol.WILD)
        assert not is_high_pay(Symbol.EMPTY)
    
    def test_is_low_pay(self):
        """Test low pay symbol detection."""
        assert is_low_pay(Symbol.PINK_SK)
        assert is_low_pay(Symbol.GREEN_SK)
        assert is_low_pay(Symbol.BLUE_SK)
        assert is_low_pay(Symbol.ORANGE_SK)
        assert is_low_pay(Symbol.CYAN_SK)
        assert not is_low_pay(Symbol.LADY_SK)
        assert not is_low_pay(Symbol.WILD)
    
    def test_is_paying(self):
        """Test paying symbol detection."""
        assert is_paying(Symbol.LADY_SK)
        assert is_paying(Symbol.PINK_SK)
        assert not is_paying(Symbol.WILD)
        assert not is_paying(Symbol.SCATTER)
        assert not is_paying(Symbol.EMPTY)
    
    def test_is_wild(self):
        """Test wild symbol detection."""
        assert is_wild(Symbol.WILD)
        assert is_wild(Symbol.E_WILD)
        assert not is_wild(Symbol.LADY_SK)
        assert not is_wild(Symbol.SCATTER)
    
    def test_wild_subtypes(self):
        """Test specific wild type detection."""
        assert is_regular_wild(Symbol.WILD)
        assert not is_regular_wild(Symbol.E_WILD)
        assert not is_regular_wild(Symbol.LADY_SK)
        
        assert is_explosivo_wild(Symbol.E_WILD)
        assert not is_explosivo_wild(Symbol.WILD)
        assert not is_explosivo_wild(Symbol.LADY_SK)
    
    def test_is_scatter(self):
        """Test scatter detection."""
        assert is_scatter(Symbol.SCATTER)
        assert not is_scatter(Symbol.WILD)
        assert not is_scatter(Symbol.LADY_SK)
    
    def test_is_special(self):
        """Test special symbol detection."""
        assert is_special(Symbol.SCATTER)
        assert not is_special(Symbol.WILD)
        assert not is_special(Symbol.LADY_SK)


class TestSymbolBehavior:
    """Test symbol behavior rules."""
    
    def test_explosion_destruction(self):
        """Test which symbols can be destroyed by explosions."""
        # Only low-pay symbols can be destroyed
        assert can_be_destroyed_by_explosion(Symbol.PINK_SK)
        assert can_be_destroyed_by_explosion(Symbol.GREEN_SK)
        assert can_be_destroyed_by_explosion(Symbol.BLUE_SK)
        assert can_be_destroyed_by_explosion(Symbol.ORANGE_SK)
        assert can_be_destroyed_by_explosion(Symbol.CYAN_SK)
        
        # High pay, wilds, and scatters cannot be destroyed
        assert not can_be_destroyed_by_explosion(Symbol.LADY_SK)
        assert not can_be_destroyed_by_explosion(Symbol.WILD)
        assert not can_be_destroyed_by_explosion(Symbol.E_WILD)
        assert not can_be_destroyed_by_explosion(Symbol.SCATTER)
        assert not can_be_destroyed_by_explosion(Symbol.EMPTY)
    
    def test_wild_substitution(self):
        """Test wild substitution rules."""
        # Wilds can substitute for paying symbols
        assert can_substitute(Symbol.WILD, Symbol.LADY_SK)
        assert can_substitute(Symbol.WILD, Symbol.PINK_SK)
        assert can_substitute(Symbol.E_WILD, Symbol.LADY_SK)
        assert can_substitute(Symbol.E_WILD, Symbol.PINK_SK)
        
        # Wilds cannot substitute for scatters
        assert not can_substitute(Symbol.WILD, Symbol.SCATTER)
        assert not can_substitute(Symbol.E_WILD, Symbol.SCATTER)
        
        # Wilds cannot substitute for other wilds (not needed)
        assert not can_substitute(Symbol.WILD, Symbol.WILD)
        assert not can_substitute(Symbol.WILD, Symbol.E_WILD)
        
        # Non-wilds cannot substitute
        assert not can_substitute(Symbol.LADY_SK, Symbol.PINK_SK)
        assert not can_substitute(Symbol.SCATTER, Symbol.LADY_SK)


class TestSymbolDisplay:
    """Test symbol display and string conversion."""
    
    def test_display_strings(self):
        """Test 3-character display strings."""
        assert get_display_string(Symbol.EMPTY) == "   "
        assert get_display_string(Symbol.LADY_SK) == "LDY"
        assert get_display_string(Symbol.PINK_SK) == "PNK"
        assert get_display_string(Symbol.GREEN_SK) == "GRN"
        assert get_display_string(Symbol.BLUE_SK) == "BLU"
        assert get_display_string(Symbol.ORANGE_SK) == "ORG"
        assert get_display_string(Symbol.CYAN_SK) == "CYN"
        assert get_display_string(Symbol.WILD) == "WLD"
        assert get_display_string(Symbol.E_WILD) == "EW "
        assert get_display_string(Symbol.SCATTER) == "SCR"
    
    def test_config_strings(self):
        """Test configuration string mapping."""
        assert get_config_string(Symbol.LADY_SK) == "LADY_SK"
        assert get_config_string(Symbol.PINK_SK) == "PINK_SK"
        assert get_config_string(Symbol.WILD) == "WILD"
        assert get_config_string(Symbol.E_WILD) == "E_WILD"
        assert get_config_string(Symbol.SCATTER) == "SCATTER"
        
        # Empty has no config string
        assert get_config_string(Symbol.EMPTY) == ""
    
    def test_string_to_symbol_conversion(self):
        """Test converting config strings back to symbols."""
        assert from_config_string("LADY_SK") == Symbol.LADY_SK
        assert from_config_string("PINK_SK") == Symbol.PINK_SK
        assert from_config_string("WILD") == Symbol.WILD
        assert from_config_string("E_WILD") == Symbol.E_WILD
        assert from_config_string("SCATTER") == Symbol.SCATTER
        
        # Invalid strings return None
        assert from_config_string("INVALID") is None
        assert from_config_string("") is None


class TestClusterMatching:
    """Test symbol cluster matching rules."""
    
    def test_empty_positions_dont_match(self):
        """Test that empty positions never match."""
        assert not symbols_match_for_cluster(Symbol.EMPTY, Symbol.EMPTY)
        assert not symbols_match_for_cluster(Symbol.EMPTY, Symbol.LADY_SK)
        assert not symbols_match_for_cluster(Symbol.WILD, Symbol.EMPTY)
    
    def test_scatters_dont_match(self):
        """Test that scatters don't participate in clusters."""
        assert not symbols_match_for_cluster(Symbol.SCATTER, Symbol.SCATTER)
        assert not symbols_match_for_cluster(Symbol.SCATTER, Symbol.LADY_SK)
        assert not symbols_match_for_cluster(Symbol.SCATTER, Symbol.WILD)
        assert not symbols_match_for_cluster(Symbol.WILD, Symbol.SCATTER)
    
    def test_wild_matching(self):
        """Test wild matching rules."""
        # Wilds match with each other
        assert symbols_match_for_cluster(Symbol.WILD, Symbol.WILD)
        assert symbols_match_for_cluster(Symbol.WILD, Symbol.E_WILD)
        assert symbols_match_for_cluster(Symbol.E_WILD, Symbol.E_WILD)
        
        # Wilds match with paying symbols
        assert symbols_match_for_cluster(Symbol.WILD, Symbol.LADY_SK)
        assert symbols_match_for_cluster(Symbol.WILD, Symbol.PINK_SK)
        assert symbols_match_for_cluster(Symbol.E_WILD, Symbol.LADY_SK)
        assert symbols_match_for_cluster(Symbol.LADY_SK, Symbol.WILD)
    
    def test_paying_symbol_matching(self):
        """Test paying symbol matching rules."""
        # Same symbols match
        assert symbols_match_for_cluster(Symbol.LADY_SK, Symbol.LADY_SK)
        assert symbols_match_for_cluster(Symbol.PINK_SK, Symbol.PINK_SK)
        
        # Different symbols don't match
        assert not symbols_match_for_cluster(Symbol.LADY_SK, Symbol.PINK_SK)
        assert not symbols_match_for_cluster(Symbol.PINK_SK, Symbol.GREEN_SK)


if __name__ == "__main__":
    pytest.main([__file__])