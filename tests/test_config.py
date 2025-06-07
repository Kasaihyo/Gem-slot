"""Unit tests for configuration module."""

import pytest
import numpy as np
import json
import tempfile
import os
from simulator import config


class TestWeightConfiguration:
    """Test symbol weight configuration."""
    
    def test_weight_normalization(self):
        """Test that weights are properly normalized."""
        # Base game weights should sum to 1.0
        assert np.isclose(config.BG_WEIGHTS.sum(), 1.0)
        
        # Free spins weights should sum to 1.0
        assert np.isclose(config.FS_WEIGHTS.sum(), 1.0)
    
    def test_symbol_arrays_match_dicts(self):
        """Test that NumPy arrays match dictionaries."""
        # Base game
        assert len(config.BG_SYMBOL_NAMES) == len(config.SYMBOL_GENERATION_WEIGHTS_BG)
        for symbol in config.BG_SYMBOL_NAMES:
            assert symbol in config.SYMBOL_GENERATION_WEIGHTS_BG
        
        # Free spins
        assert len(config.FS_SYMBOL_NAMES) == len(config.SYMBOL_GENERATION_WEIGHTS_FS)
        for symbol in config.FS_SYMBOL_NAMES:
            assert symbol in config.SYMBOL_GENERATION_WEIGHTS_FS
    
    def test_free_spins_wild_enrichment(self):
        """Test that wilds are enriched in free spins."""
        bg_wild_weight = config.SYMBOL_GENERATION_WEIGHTS_BG["WILD"]
        bg_ew_weight = config.SYMBOL_GENERATION_WEIGHTS_BG["E_WILD"]
        fs_wild_weight = config.SYMBOL_GENERATION_WEIGHTS_FS["WILD"]
        fs_ew_weight = config.SYMBOL_GENERATION_WEIGHTS_FS["E_WILD"]
        
        # EW should be disabled in free spins
        assert fs_ew_weight == 0
        
        # Wild weight should be enriched with EW weight
        assert fs_wild_weight == bg_wild_weight + bg_ew_weight
    
    def test_weight_percentages(self):
        """Test that normalized weights match expected percentages."""
        # Get normalized weights
        bg_idx = {s: i for i, s in enumerate(config.BG_SYMBOL_NAMES)}
        
        # Check approximate percentages (within 0.5%)
        expected = {
            "LADY_SK": 0.025,   # ~2.5%
            "PINK_SK": 0.117,   # ~11.7%
            "GREEN_SK": 0.133,  # ~13.3%
            "BLUE_SK": 0.150,   # ~15.0%
            "ORANGE_SK": 0.167, # ~16.7%
            "CYAN_SK": 0.183,   # ~18.3%
            "WILD": 0.100,      # ~10.0%
            "E_WILD": 0.067,    # ~6.7%
            "SCATTER": 0.058    # ~5.8%
        }
        
        for symbol, expected_weight in expected.items():
            actual_weight = config.BG_WEIGHTS[bg_idx[symbol]]
            assert abs(actual_weight - expected_weight) < 0.005


class TestPaytableConfiguration:
    """Test paytable configuration."""
    
    def test_payout_retrieval(self):
        """Test get_payout function."""
        # Test valid payouts
        assert config.get_payout("LADY_SK", 5) == 1.0
        assert config.get_payout("LADY_SK", 15) == 150.0
        assert config.get_payout("PINK_SK", 8) == 1.7
        
        # Test cluster size < 5 returns 0
        assert config.get_payout("LADY_SK", 4) == 0.0
        assert config.get_payout("LADY_SK", 0) == 0.0
        
        # Test cluster size > 15 uses 15+ payout
        assert config.get_payout("LADY_SK", 20) == 150.0
        assert config.get_payout("LADY_SK", 100) == 150.0
    
    def test_all_symbols_have_payouts(self):
        """Test that all paying symbols have complete paytables."""
        for symbol in config.PAYING_SYMBOLS:
            for size in range(5, 16):
                payout = config.get_payout(symbol, size)
                assert payout > 0, f"Missing payout for {symbol} cluster size {size}"
    
    def test_payout_progression(self):
        """Test that payouts increase with cluster size."""
        for symbol in config.PAYING_SYMBOLS:
            payouts = [config.get_payout(symbol, size) for size in range(5, 16)]
            # Check that payouts are non-decreasing
            for i in range(1, len(payouts)):
                assert payouts[i] >= payouts[i-1], \
                    f"Payout regression for {symbol} at size {i+5}"


class TestConfigurationValidation:
    """Test configuration validation."""
    
    def test_validate_config_passes(self):
        """Test that current config passes validation."""
        # Should not raise any exceptions
        config.validate_config()
    
    def test_validate_config_catches_errors(self):
        """Test that validation catches configuration errors."""
        # Save original values
        original_bg = config.SYMBOL_GENERATION_WEIGHTS_BG.copy()
        
        # Test negative weights
        config.SYMBOL_GENERATION_WEIGHTS_BG["LADY_SK"] = -1
        with pytest.raises(ValueError):
            config.validate_config()
        
        # Restore
        config.SYMBOL_GENERATION_WEIGHTS_BG.update(original_bg)
        config.validate_config()  # Should pass again


class TestWeightPersistence:
    """Test weight save/load functionality."""
    
    def test_save_and_load_weights(self):
        """Test saving and loading weights to/from JSON."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Save weights
            config.save_weights(temp_path)
            
            # Verify file exists and is valid JSON
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            # Check structure
            assert "timestamp" in data
            assert "base_game" in data
            assert "free_spins" in data
            assert "version" in data
            
            # Modify weights
            original_bg = config.SYMBOL_GENERATION_WEIGHTS_BG.copy()
            config.SYMBOL_GENERATION_WEIGHTS_BG["LADY_SK"] = 10
            
            # Load weights (should restore original)
            config.load_weights(temp_path)
            
            # Verify restoration
            assert config.SYMBOL_GENERATION_WEIGHTS_BG["LADY_SK"] == original_bg["LADY_SK"]
            
            # Verify arrays were regenerated
            assert np.isclose(config.BG_WEIGHTS.sum(), 1.0)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestGameConfiguration:
    """Test game configuration values."""
    
    def test_grid_configuration(self):
        """Test grid-related configuration."""
        assert config.GRID_SIZE == 5
        assert config.MIN_CLUSTER_SIZE == 5
    
    def test_multiplier_configuration(self):
        """Test multiplier configuration."""
        assert config.MAX_MULTIPLIER_BASE == 32
        assert config.MAX_MULTIPLIER_FS == 1024
        assert config.BASE_GAME_MULTIPLIERS == [1, 2, 4, 8, 16, 32]
    
    def test_bet_configuration(self):
        """Test bet-related configuration."""
        assert config.MIN_BET == 0.10
        assert config.MAX_BET == 100.00
        assert config.FEATURE_BUY_COST == 75
        assert config.BET_PLUS_MULTIPLIERS == [1.5, 2.0, 3.0]
    
    def test_rtp_targets(self):
        """Test RTP configuration."""
        assert config.RTP_BASE_GAME == 0.9422
        assert config.RTP_FEATURE_BUY == 0.9440
    
    def test_wild_spawn_configuration(self):
        """Test wild spawning configuration."""
        assert config.WILD_SPAWN_CHANCE_AFTER_WIN == 1.0
        assert sum(config.WILD_TYPE_DISTRIBUTION.values()) == 1.0
        assert config.WILD_TYPE_DISTRIBUTION["WILD"] == 0.5
        assert config.WILD_TYPE_DISTRIBUTION["E_WILD"] == 0.5


if __name__ == "__main__":
    pytest.main([__file__])