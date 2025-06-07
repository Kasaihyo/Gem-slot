"""
Configuration module for Esqueleto Explosivo 3 Simulator.

This module contains all game mathematics, weights, and configuration values.
Uses a dual-storage approach: Python dictionaries for primary storage and
NumPy arrays for high-performance operations.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime


# Symbol definitions
SYMBOLS = {
    "LADY_SK": "LDY",    # Lady Skull - High Pay
    "PINK_SK": "PNK",    # Pink Skull - Low Pay
    "GREEN_SK": "GRN",   # Green Skull - Low Pay
    "BLUE_SK": "BLU",    # Blue Skull - Low Pay
    "ORANGE_SK": "ORG",  # Orange Skull - Low Pay
    "CYAN_SK": "CYN",    # Cyan Skull - Low Pay
    "WILD": "WLD",       # Wild - Substitutes for all paying symbols
    "E_WILD": "EW",      # Explosivo Wild - Special Wild with explosion
    "SCATTER": "SCR"     # Scatter - Triggers free spins
}

# Symbol categories
HIGH_PAY_SYMBOLS = ["LADY_SK"]
LOW_PAY_SYMBOLS = ["PINK_SK", "GREEN_SK", "BLUE_SK", "ORANGE_SK", "CYAN_SK"]
PAYING_SYMBOLS = HIGH_PAY_SYMBOLS + LOW_PAY_SYMBOLS
WILD_SYMBOLS = ["WILD", "E_WILD"]
SPECIAL_SYMBOLS = ["SCATTER"]
ALL_SYMBOLS = PAYING_SYMBOLS + WILD_SYMBOLS + SPECIAL_SYMBOLS

# Base Game Symbol Generation Weights (normalized at runtime)
# These are the primary weights from the PRD
SYMBOL_GENERATION_WEIGHTS_BG = {
    "LADY_SK": 3,     # ~2.5%
    "PINK_SK": 14,    # ~11.7%
    "GREEN_SK": 16,   # ~13.3%
    "BLUE_SK": 18,    # ~15.0%
    "ORANGE_SK": 20,  # ~16.7%
    "CYAN_SK": 22,    # ~18.3%
    "WILD": 12,       # ~10.0%
    "E_WILD": 8,      # ~6.7%
    "SCATTER": 7      # ~5.8%
}

# Free Spins Symbol Generation Weights (enriched wilds)
# EW spawning is disabled in free spins, so redistribute that weight
SYMBOL_GENERATION_WEIGHTS_FS = {
    "LADY_SK": 3,     # Same as base
    "PINK_SK": 14,    # Same as base
    "GREEN_SK": 16,   # Same as base
    "BLUE_SK": 18,    # Same as base
    "ORANGE_SK": 20,  # Same as base
    "CYAN_SK": 22,    # Same as base
    "WILD": 20,       # Enriched (12 + 8 from EW)
    "E_WILD": 0,      # Disabled in free spins
    "SCATTER": 7      # Same as base
}

# Performance optimization: NumPy arrays for weighted random selection
# These are generated from the dictionaries above
def _normalize_weights(weights_dict: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
    """Convert weight dictionary to normalized NumPy arrays."""
    symbols = list(weights_dict.keys())
    weights = np.array([weights_dict[s] for s in symbols], dtype=np.float64)
    weights = weights / weights.sum()  # Normalize to sum to 1.0
    return np.array(symbols), weights

# Generate NumPy arrays from dictionaries
BG_SYMBOL_NAMES, BG_WEIGHTS = _normalize_weights(SYMBOL_GENERATION_WEIGHTS_BG)
FS_SYMBOL_NAMES, FS_WEIGHTS = _normalize_weights(SYMBOL_GENERATION_WEIGHTS_FS)

# Paytable Configuration
# Key: (symbol, cluster_size), Value: payout multiplier
PAYTABLE = {
    # Lady Skull (High Pay)
    ("LADY_SK", 5): 1.0,
    ("LADY_SK", 6): 1.5,
    ("LADY_SK", 7): 2.5,
    ("LADY_SK", 8): 5.0,
    ("LADY_SK", 9): 5.0,
    ("LADY_SK", 10): 7.5,
    ("LADY_SK", 11): 7.5,
    ("LADY_SK", 12): 25.0,
    ("LADY_SK", 13): 25.0,
    ("LADY_SK", 14): 25.0,
    ("LADY_SK", 15): 150.0,  # 15+ pays 150x
    
    # Pink Skull
    ("PINK_SK", 5): 0.5,
    ("PINK_SK", 6): 0.7,
    ("PINK_SK", 7): 1.0,
    ("PINK_SK", 8): 1.7,
    ("PINK_SK", 9): 1.7,
    ("PINK_SK", 10): 2.5,
    ("PINK_SK", 11): 2.5,
    ("PINK_SK", 12): 7.5,
    ("PINK_SK", 13): 7.5,
    ("PINK_SK", 14): 7.5,
    ("PINK_SK", 15): 50.0,
    
    # Green Skull
    ("GREEN_SK", 5): 0.4,
    ("GREEN_SK", 6): 0.7,
    ("GREEN_SK", 7): 0.8,
    ("GREEN_SK", 8): 1.4,
    ("GREEN_SK", 9): 1.4,
    ("GREEN_SK", 10): 2.0,
    ("GREEN_SK", 11): 2.0,
    ("GREEN_SK", 12): 6.0,
    ("GREEN_SK", 13): 6.0,
    ("GREEN_SK", 14): 6.0,
    ("GREEN_SK", 15): 40.0,
    
    # Blue Skull
    ("BLUE_SK", 5): 0.3,
    ("BLUE_SK", 6): 0.5,
    ("BLUE_SK", 7): 0.6,
    ("BLUE_SK", 8): 1.0,
    ("BLUE_SK", 9): 1.0,
    ("BLUE_SK", 10): 1.5,
    ("BLUE_SK", 11): 1.5,
    ("BLUE_SK", 12): 5.0,
    ("BLUE_SK", 13): 5.0,
    ("BLUE_SK", 14): 5.0,
    ("BLUE_SK", 15): 30.0,
    
    # Orange Skull
    ("ORANGE_SK", 5): 0.3,
    ("ORANGE_SK", 6): 0.4,
    ("ORANGE_SK", 7): 0.5,
    ("ORANGE_SK", 8): 0.8,
    ("ORANGE_SK", 9): 0.8,
    ("ORANGE_SK", 10): 1.2,
    ("ORANGE_SK", 11): 1.2,
    ("ORANGE_SK", 12): 4.0,
    ("ORANGE_SK", 13): 4.0,
    ("ORANGE_SK", 14): 4.0,
    ("ORANGE_SK", 15): 25.0,
    
    # Cyan Skull
    ("CYAN_SK", 5): 0.2,
    ("CYAN_SK", 6): 0.3,
    ("CYAN_SK", 7): 0.4,
    ("CYAN_SK", 8): 0.6,
    ("CYAN_SK", 9): 0.6,
    ("CYAN_SK", 10): 1.0,
    ("CYAN_SK", 11): 1.0,
    ("CYAN_SK", 12): 3.0,
    ("CYAN_SK", 13): 3.0,
    ("CYAN_SK", 14): 3.0,
    ("CYAN_SK", 15): 20.0
}

def get_payout(symbol: str, cluster_size: int) -> float:
    """Get payout for a symbol and cluster size."""
    if cluster_size < 5:
        return 0.0
    if cluster_size >= 15:
        cluster_size = 15
    return PAYTABLE.get((symbol, cluster_size), 0.0)

# Game Configuration
GRID_SIZE = 5
MIN_CLUSTER_SIZE = 5
MAX_MULTIPLIER_BASE = 32
MAX_MULTIPLIER_FS = 1024
MAX_WIN_CAP = 7500  # Max win is 7500x bet

# Bet Configuration
MIN_BET = 0.10
MAX_BET = 100.00
BET_PLUS_MULTIPLIERS = [1.5, 2.0, 3.0]  # Bet+ options
FEATURE_BUY_COST = 75  # 75x bet for feature buy

# Free Spins Configuration
SCATTER_COUNTS_TO_SPINS = {
    3: 10,
    4: 15,
    5: 20,
    6: 25  # 6+ scatters
}
EW_COLLECTION_THRESHOLD = 3  # Collect 3 EWs for multiplier upgrade + 1 spin

# Avalanche Multiplier Progression
BASE_GAME_MULTIPLIERS = [1, 2, 4, 8, 16, 32]
# Free spins multipliers are dynamic based on base level

# RTP Targets
RTP_BASE_GAME = 0.9422  # 94.22%
RTP_FEATURE_BUY = 0.9440  # 94.40%

# Performance Settings
USE_NUMPY_OPTIMIZATION = True
BATCH_SIZE = 1000  # For batch operations

# Wild Spawning Configuration
WILD_SPAWN_CHANCE_AFTER_WIN = 1.0  # 100% chance
WILD_TYPE_DISTRIBUTION = {
    "WILD": 0.5,     # 50% regular wild
    "E_WILD": 0.5    # 50% explosivo wild
}

# Explosion Configuration
EXPLOSION_RADIUS = 1  # 3x3 area (center +/- 1)
EXPLOSION_AFFECTS_ONLY_LP = True  # Only destroys low-pay symbols

def validate_config() -> None:
    """Validate configuration integrity at runtime."""
    # Check weight sums
    bg_sum = sum(SYMBOL_GENERATION_WEIGHTS_BG.values())
    fs_sum = sum(SYMBOL_GENERATION_WEIGHTS_FS.values())
    
    if bg_sum <= 0 or fs_sum <= 0:
        raise ValueError("Weight sums must be positive")
    
    # Check for negative weights
    for symbol, weight in SYMBOL_GENERATION_WEIGHTS_BG.items():
        if weight < 0:
            raise ValueError(f"Negative weight for {symbol} in base game")
    
    for symbol, weight in SYMBOL_GENERATION_WEIGHTS_FS.items():
        if weight < 0:
            raise ValueError(f"Negative weight for {symbol} in free spins")
    
    # Check symbol sets match
    bg_symbols = set(SYMBOL_GENERATION_WEIGHTS_BG.keys())
    fs_symbols = set(SYMBOL_GENERATION_WEIGHTS_FS.keys())
    
    if bg_symbols != fs_symbols:
        raise ValueError("Base game and free spins symbol sets must match")
    
    # Check arrays align with dictionaries
    if len(BG_SYMBOL_NAMES) != len(SYMBOL_GENERATION_WEIGHTS_BG):
        raise ValueError("BG arrays don't match dictionary size")
    
    if len(FS_SYMBOL_NAMES) != len(SYMBOL_GENERATION_WEIGHTS_FS):
        raise ValueError("FS arrays don't match dictionary size")
    
    # Check normalized weights sum to 1.0
    if not np.isclose(BG_WEIGHTS.sum(), 1.0):
        raise ValueError("BG weights don't sum to 1.0")
    
    if not np.isclose(FS_WEIGHTS.sum(), 1.0):
        raise ValueError("FS weights don't sum to 1.0")
    
    # Check all symbols in paytable are valid
    for symbol, _ in PAYTABLE.keys():
        if symbol not in PAYING_SYMBOLS:
            raise ValueError(f"Invalid symbol in paytable: {symbol}")

def save_weights(filename: str) -> None:
    """Save current weights to JSON file."""
    data = {
        "timestamp": datetime.now().isoformat(),
        "base_game": SYMBOL_GENERATION_WEIGHTS_BG,
        "free_spins": SYMBOL_GENERATION_WEIGHTS_FS,
        "version": "1.0"
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_weights(filename: str) -> None:
    """Load weights from JSON file and regenerate arrays."""
    global SYMBOL_GENERATION_WEIGHTS_BG, SYMBOL_GENERATION_WEIGHTS_FS
    global BG_SYMBOL_NAMES, BG_WEIGHTS, FS_SYMBOL_NAMES, FS_WEIGHTS
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    SYMBOL_GENERATION_WEIGHTS_BG = data["base_game"]
    SYMBOL_GENERATION_WEIGHTS_FS = data["free_spins"]
    
    # Regenerate arrays
    BG_SYMBOL_NAMES, BG_WEIGHTS = _normalize_weights(SYMBOL_GENERATION_WEIGHTS_BG)
    FS_SYMBOL_NAMES, FS_WEIGHTS = _normalize_weights(SYMBOL_GENERATION_WEIGHTS_FS)
    
    # Validate after loading
    validate_config()

# Run validation at import time
validate_config()