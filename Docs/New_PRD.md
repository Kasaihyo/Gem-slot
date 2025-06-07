# Esqueleto Explosivo 3 - Product Requirements Document

**Version:** 1.1  
**Date:** 2024-12-06  
**Status:** Complete  
**Based on:** Math Specification Revision 4

## Executive Summary

Esqueleto Explosivo 3 is a high-volatility 5x5 grid slot game featuring cluster pays mechanics, cascading avalanches, explosive wilds, and progressive multipliers. Set in a vibrant Day of the Dead celebration, the game offers players the potential for massive wins up to 7,500x their bet through escalating multipliers and an engaging free spins feature.

## Core Game Mechanics

### 1. Grid Structure & Display

The game uses a **5x5 grid** (25 positions) with symbols displayed using colored abbreviations:

```
Example Initial Grid:
┌─────┬─────┬─────┬─────┬─────┐
│ LDY │ PNK │ GRN │ BLU │ ORG │  Row 0
├─────┼─────┼─────┼─────┼─────┤
│ CYN │ WLD │ PNK │ PNK │ GRN │  Row 1
├─────┼─────┼─────┼─────┼─────┤
│ BLU │ PNK │ PNK │ PNK │ LDY │  Row 2
├─────┼─────┼─────┼─────┼─────┤
│ ORG │ PNK │ EW  │ PNK │ BLU │  Row 3
├─────┼─────┼─────┼─────┼─────┤
│ SCR │ CYN │ GRN │ SCR │ ORG │  Row 4
└─────┴─────┴─────┴─────┴─────┘
  Col0  Col1  Col2  Col3  Col4
```

**Symbol Legend:**
- **LDY** (Lady Skull) - High Pay symbol - Red color - Elegant decorated skull
- **PNK** (Pink Skull) - Low Pay symbol - Magenta color  
- **GRN** (Green Skull) - Low Pay symbol - Green color
- **BLU** (Blue Skull) - Low Pay symbol - Blue color
- **ORG** (Orange Skull) - Low Pay symbol - Yellow color
- **CYN** (Cyan Skull) - Low Pay symbol - Cyan color
- **WLD** (Wild) - Substitutes for all paying symbols - White color - Skull with sunglasses
- **EW** (Explosivo Wild) - Special Wild with explosion feature - Bright Yellow - Distinct explosive visual
- **SCR** (Scatter) - Triggers free spins - Bright Magenta - Silver Robot Skull

### 2. Cluster Pays System

Wins occur when **5 or more identical symbols** connect horizontally and/or vertically (diagonal connections don't count). Wilds substitute for all paying symbols. 

**Key Specifications:**
- Minimum cluster size: 5 symbols
- Maximum tracked cluster size: 15+ symbols (all clusters ≥15 pay the same)
- Connections: Horizontal and vertical only

**Wild Assignment Rules:**
- A single wild CAN participate in multiple clusters simultaneously
- Each cluster independently includes any connected wilds
- Example: One wild could connect to both a Pink cluster and a Blue cluster
- All valid clusters are paid independently
- Cluster detection uses Union-Find algorithm for performance

**Example - Finding a Winning Cluster:**
```
Initial State:
┌─────┬─────┬─────┬─────┬─────┐
│ LDY │ PNK │ GRN │ BLU │ ORG │
├─────┼─────┼─────┼─────┼─────┤
│ CYN │ WLD │ PNK │ PNK │ GRN │  
├─────┼─────┼─────┼─────┼─────┤
│ BLU │ PNK │ PNK │ PNK │ LDY │
├─────┼─────┼─────┼─────┼─────┤
│ ORG │ PNK │ EW  │ PNK │ BLU │
├─────┼─────┼─────┼─────┼─────┤
│ SCR │ CYN │ GRN │ SCR │ ORG │
└─────┴─────┴─────┴─────┴─────┘

Cluster Found: 8 Pink Skulls (including Wild at (1,1))
Positions: (0,1), (1,1), (1,2), (1,3), (2,1), (2,2), (2,3), (3,1), (3,3)
Payout: 1.7x bet × current multiplier
```

### 3. Paytable

| Symbol | 5 | 6 | 7 | 8-9 | 10-11 | 12-14 | 15+ |
|--------|---|---|---|-----|-------|-------|-----|
| Lady Skull (HP) | 1.0x | 1.5x | 2.5x | 5.0x | 7.5x | 25.0x | 150.0x |
| Pink Skull | 0.5x | 0.7x | 1.0x | 1.7x | 2.5x | 7.5x | 50.0x |
| Green Skull | 0.4x | 0.7x | 0.8x | 1.4x | 2.0x | 6.0x | 40.0x |
| Blue Skull | 0.3x | 0.5x | 0.6x | 1.0x | 1.5x | 5.0x | 30.0x |
| Orange Skull | 0.3x | 0.4x | 0.5x | 0.8x | 1.2x | 4.0x | 25.0x |
| Cyan Skull | 0.2x | 0.3x | 0.4x | 0.6x | 1.0x | 3.0x | 20.0x |

### 4. Avalanche Mechanic

After each win, an avalanche sequence occurs:

**Example Avalanche Sequence:**
```
Step 1: Win Detected (8 Pink cluster)
┌─────┬─────┬─────┬─────┬─────┐
│ LDY │[PNK]│ GRN │ BLU │ ORG │
├─────┼─────┼─────┼─────┼─────┤
│ CYN │[WLD]│[PNK]│[PNK]│ GRN │
├─────┼─────┼─────┼─────┼─────┤
│ BLU │[PNK]│[PNK]│[PNK]│ LDY │
├─────┼─────┼─────┼─────┼─────┤
│ ORG │[PNK]│ SCR │[PNK]│ BLU │
├─────┼─────┼─────┼─────┼─────┤
│ SCR │ CYN │ GRN │ SCR │ ORG │
└─────┴─────┴─────┴─────┴─────┘
[Brackets indicate winning cluster]

Step 2: Remove Winners & Wild Spawn (guaranteed)
Wild spawned at (2,2) in empty cluster position
┌─────┬─────┬─────┬─────┬─────┐
│ LDY │     │ GRN │ BLU │ ORG │
├─────┼─────┼─────┼─────┼─────┤
│ CYN │     │     │     │ GRN │
├─────┼─────┼─────┼─────┼─────┤
│ BLU │     │ WLD │     │ LDY │  ← New Wild spawned
├─────┼─────┼─────┼─────┼─────┤
│ ORG │     │ SCR │     │ BLU │
├─────┼─────┼─────┼─────┼─────┤
│ SCR │ CYN │ GRN │ SCR │ ORG │
└─────┴─────┴─────┴─────┴─────┘

Step 3: Gravity (symbols fall down)
┌─────┬─────┬─────┬─────┬─────┐
│ LDY │     │     │     │ ORG │
├─────┼─────┼─────┼─────┼─────┤
│ CYN │     │ GRN │     │ GRN │ ← Green fall
├─────┼─────┼─────┼─────┼─────┤
│ BLU │     │ WLD │     │ LDY │  
├─────┼─────┼─────┼─────┼─────┤
│ ORG │     │ SCR │ BLU │ BLU │ ← Blue fall
├─────┼─────┼─────┼─────┼─────┤
│ SCR │ CYN │ GRN │ SCR │ ORG │
└─────┴─────┴─────┴─────┴─────┘

Step 4: New symbols drop from above
┌─────┬─────┬─────┬─────┬─────┐
│ LDY │ PNK │ CYN │ PNK │ ORG │
├─────┼─────┼─────┼─────┼─────┤
│ CYN │ CYN │ GRN │ PNK │ GRN │
├─────┼─────┼─────┼─────┼─────┤
│ BLU │ PNK │ WLD │ CYN │ LDY │  
├─────┼─────┼─────┼─────┼─────┤
│ ORG │ PNK │ SCR │ BLU │ BLU │
├─────┼─────┼─────┼─────┼─────┤
│ SCR │ CYN │ GRN │ SCR │ ORG │
└─────┴─────┴─────┴─────┴─────┘
```

### 5. Explosivo Wild Feature

Explosivo Wilds explode after wins are calculated. This includes:
- EWs that **landed** (dropped from above) in the current cascade
- EWs that were part of **winning clusters** (removed but still explode)

**Explosion Timing Edge Cases:**
- If an EW is part of a winning cluster AND would be destroyed by another EW's explosion, the cluster removal happens first (EW is marked for explosion)
- EWs are immune to explosion damage - only LP symbols can be destroyed
- All marked EWs explode truly simultaneously in single step
- Multiplier increases ONCE per explosion step, regardless of how many EWs explode
- No chain reactions: EWs exposed by explosions wait until next cascade
- Overlapping 3x3 areas: Each position destroyed only once
- Collection: EWs in clusters that also explode are collected ONCE only

**Example EW Explosion:**
```
Before Explosion (EW at position 3,2):
┌─────┬─────┬─────┬─────┬─────┐
│ PNK │ BLU │ CYN │ GRN │ LDY │
├─────┼─────┼─────┼─────┼─────┤
│ LDY │ ORG │ GRN │ BLU │ ORG │
├─────┼─────┼─────┼─────┼─────┤
│ CYN │ PNK │ WLD │ CYN │ GRN │
├─────┼─────┼─────┼─────┼─────┤
│ BLU │ GRN │ EW  │ BLU │ LDY │  ← EW will explode
├─────┼─────┼─────┼─────┼─────┤
│ SCR │ CYN │ GRN │ SCR │ ORG │
└─────┴─────┴─────┴─────┴─────┘

3x3 Explosion Area (destroys only LP symbols):
┌─────┬─────┬─────┬─────┬─────┐
│ PNK │ BLU │ CYN │ GRN │ LDY │
├─────┼─────┼─────┼─────┼─────┤
│ LDY │ ORG │ GRN │ BLU │ ORG │
├─────┼─────┼─────┼─────┼─────┤
│ CYN │ [  ]│ WLD │ [  ]│ GRN │  ← PNK & CYN destroyed
├─────┼─────┼─────┼─────┼─────┤
│ BLU │ [  ]│ [  ]│ [  ]│ LDY │  ← GRN, EW & BLU destroyed
├─────┼─────┼─────┼─────┼─────┤
│ SCR │ [  ]│ [  ]│ SCR │ ORG │  ← CYN & GRN destroyed
└─────┴─────┴─────┴─────┴─────┘

Note: WLD at (2,2), LDY at (3,4), and SCR at (4,3) survive
(Only LP symbols are destroyed)
```

### 6. Multiplier System

**Base Game Multiplier Progression:**
- Starts at 1x each spin
- Increases with each winning avalanche: 1x → 2x → 4x → 8x → 16x → 32x
- Resets on new spin

**Example Multiplier Progression:**
```
Spin Start: Multiplier = 1x
Avalanche 1: 8-cluster Pink win = 1.7x × 1x = 1.7x bet
Avalanche 2: Multiplier increases to 2x
             6-cluster Blue win = 0.5x × 2x = 1.0x bet  
Avalanche 3: Multiplier increases to 4x
             5-cluster Green win = 0.4x × 4x = 1.6x bet
Total Win: 1.7 + 1.0 + 1.6 = 4.3x bet
```

### 7. Free Spins Feature

**Triggering:**
- Base Game: 3+ Scatters anywhere
  - 3 SCR = 10 spins
  - 4 SCR = 12 spins
  - 5+ SCR = 12 + (N-4)×2 spins

**Retriggers (During Free Spins):**
- 2 SCR = +3 spins
- 3 SCR = +5 spins
- 4 SCR = +7 spins
- 5+ SCR = +7 + (N-4)×2 spins

**Enhanced Multiplier System:**
The FS uses a persistent base multiplier with 6-step trails:

| Base Level | Trail Progression |
|------------|-------------------|
| 1x | 1x → 2x → 4x → 8x → 16x → 32x |
| 2x | 2x → 4x → 8x → 16x → 32x → 64x |
| 4x | 4x → 8x → 16x → 32x → 64x → 128x |
| ... | ... |
| 32x | 32x → 64x → 128x → 256x → 512x → 1024x |

**EW Collection & Upgrades:**
- EWs are collected when removed by ANY means (winning clusters OR explosions)
- This includes EWs that explode without being part of a cluster
- Every 3 EWs collected = 1 upgrade
- Each upgrade grants:
  - +1 base multiplier level (max 32x)
  - +1 additional free spin
- Upgrades apply at the START of the next spin
- Unused EWs carry over between spins (e.g., 2 collected EWs wait for 1 more)

**Multiplier Trail Behavior:**
- Trail resets to base level at the START of each free spin
- Current trail position does NOT persist between spins
- If base multiplier upgrades mid-spin, the upgrade takes effect at the START of the next spin
- Within a spin, trail progression follows: base → base×2 → base×4 → base×8 → base×16 → base×32
- Maximum multiplier: 1024x (base 32x with full trail progression)
- No wrapping - multiplier caps at 1024x for remainder of spin

**Free Spins Retrigger Rules:**
- Scatters that trigger FS do NOT count toward immediate retrigger
- Retrigger spins added immediately when detected
- No maximum retriggers or total spin limit

```
Example Free Spins Session:
Spin 1: Base 1x, collect 2 EWs
Spin 2: Base 1x, collect 1 EW (Total: 3 EWs)
        → Upgrade pending: Base increases to 2x, +1 spin
Spin 3: Base 2x (upgraded), Trail: 2x→4x→8x→16x→32x→64x
        Avalanche progression: 2x→4x→8x
        Collect 4 more EWs (Total: 7 EWs)
Spin 4: Base 2x, 1 more EW (Total: 8 EWs, 6 used, 2 remain)
        → Upgrade pending: Base to 4x, +1 spin
```

### 8. Wild Spawning Mechanic

After each winning cluster, a wild is **guaranteed to spawn** (100% chance):
- 50% chance: Standard Wild (WLD)
- 50% chance: Explosivo Wild (EW)
- Spawns in random empty position within cluster footprint

**Detailed Wild Spawning Process:**

1. **Trigger**: After symbols in winning clusters are marked for removal
2. **Probability Check**: 100% chance per cluster (guaranteed spawn)
3. **Position Selection**: Random empty position within cluster's original footprint
4. **Wild Type Selection**: 50% WLD, 50% EW

**Important Notes:**
- Spawned wilds appear AFTER cluster symbols are removed
- Spawned EWs do NOT explode in the same cascade they are spawned
- Spawned EWs follow the "landed this drop" rule - they only explode in step 4 of the cascade where they land
- Gravity completes first before new symbols (including spawned wilds) drop
- The 50/50 probability split is tunable: P(SpawnW) + P(SpawnEW) = 1

**Multiple Cluster Resolution:**
- All clusters spawn wilds simultaneously during the same phase
- Wild spawning order is not based on cluster size or position
- Overlapping footprints: Each cluster independently selects from its own footprint
- If footprints overlap, the same position could be selected by multiple clusters (collision handling applies)

**Collision Handling:**
When multiple clusters trigger wild spawning simultaneously:
- Each cluster attempts a guaranteed wild spawn (100% chance)
- If multiple wilds target same position:
  - First wild takes the position
  - Subsequent wilds re-roll for different empty positions within their cluster footprint
  - If entire footprint becomes occupied, that cluster forfeits its wild spawn
  - No search area expansion beyond original cluster footprint
- Edge clusters: Only valid on-grid positions considered
- If cluster is entirely off-grid, spawn is forfeited

**Example Multi-Cluster Wild Spawn:**
```
Two winning clusters detected:
Cluster A (Blue): positions (0,0), (0,1), (1,0), (1,1), (2,0)
Cluster B (Green): positions (2,3), (2,4), (3,3), (3,4), (4,3)

Wild Spawning (guaranteed for each cluster):
- Cluster A: 50/50 roll → Spawn WLD
- Cluster B: 50/50 roll → Spawn EW

Position Selection:
- Cluster A chooses (1,1) for WLD
- Cluster B chooses (3,4) for EW
- No collision, both wilds placed successfully

If both had chosen (1,1):
- Cluster A places WLD at (1,1)
- Cluster B re-rolls and places EW at different position like (2,4)
```

### 9. Special Features

**Bet+ Options (Base Game Only):**
- **Bonus Boost (1.5x bet)**: ~2x FS trigger chance
- **The Enrico Show (2x bet)**: Guarantees 1 EW on initial drop
- **Bonus Boost Plus (3x bet)**: ~5x FS trigger chance

**Feature Buy:**
- Cost: 75x base bet
- Awards: 10 Free Spins immediately
- Target RTP: 94.40%
- Initial grid: Standard P_BG generation (no special rules)
- Bet+ options: Disabled during all free spins (natural or purchased)
- Expected return: ~71x average (94.40% of 75x cost)
- Return distribution: Heavily skewed (many small wins, rare huge wins)

### 10. Symbol Distribution & Weights

The game uses separate symbol distributions for Base Game and Free Spins, defined as:
- **P_BG(Symbol)**: Base Game probability for each symbol
- **P_FS(Symbol)**: Free Spins probability for each symbol

**Base Game Weights (example):**
```python
BG_WEIGHTS = {
    "LADY_SK": 3,      # P_BG(HP) ≈ 2.5%
    "PINK_SK": 14,     # P_BG(LP1) ≈ 11.7%
    "GREEN_SK": 16,    # P_BG(LP2) ≈ 13.3%
    "BLUE_SK": 18,     # P_BG(LP3) ≈ 15.0%
    "ORANGE_SK": 20,   # P_BG(LP4) ≈ 16.7%
    "CYAN_SK": 22,     # P_BG(LP5) ≈ 18.3%
    "WILD": 12,        # P_BG(W) ≈ 10.0%
    "E_WILD": 8,       # P_BG(EW) ≈ 6.7%
    "SCATTER": 7       # P_BG(S) ≈ 5.8%
}
```

**Symbol Weight Application:**
- Weights are relative and normalized at runtime: P(symbol) = weight/sum(all weights)
- Same normalized distribution for BOTH initial drops AND cascade refills
- Same distribution (P_BG or P_FS) used throughout entire spin sequence
- No position-specific weight adjustments
- Pure random generation - no consecutive symbol restrictions
- No near-miss prevention or minimum spacing requirements

**Free Spins Weights (example):**
```python
FS_WEIGHTS = {
    "LADY_SK": 4,      # P_FS(HP) ≈ 3.1%
    "PINK_SK": 12,     # P_FS(LP1) ≈ 9.2%
    "GREEN_SK": 14,    # P_FS(LP2) ≈ 10.8%
    "BLUE_SK": 16,     # P_FS(LP3) ≈ 12.3%
    "ORANGE_SK": 18,   # P_FS(LP4) ≈ 13.8%
    "CYAN_SK": 20,     # P_FS(LP5) ≈ 15.4%
    "WILD": 18,        # P_FS(W) ≈ 13.8% (1.5x enrichment)
    "E_WILD": 16,      # P_FS(EW) ≈ 12.3% (2x enrichment)
    "SCATTER": 12      # P_FS(S) ≈ 9.2%
}
```
- EW enrichment ensures ~3-5 EWs collected per 10 spins average
- Wild enrichment increases cluster frequency and size

**Bet+ Modifications:**
- Bonus Boost: Increases P_BG(S) by ~2x (other weights scale down proportionally)
- Bonus Boost Plus: Increases P_BG(S) by ~5x (other weights scale down proportionally)
- The Enrico Show: Forces exactly 1 EW at random position on initial drop only (overrides normal generation for that position)

### 11. Game Flow Summary

**Complete Spin Sequence:**

1. **REEL DROP** (Initial or After Avalanche)
   - Populate empty positions with new symbols

2. **CHECK FOR SCATTERS**
   - Count total Scatters visible on grid
   - If 3+ Scatters present anywhere:
     - Mark Free Spins as triggered (will enter after complete avalanche sequence)
   - Continue to step 3 regardless

3. **CHECK FOR WINNING CLUSTERS**
   - If clusters found (5+ connected symbols, including Wilds/EWs):
     - Calculate win value (paytable × current multiplier)
     - Mark winning symbols for removal
     - For EACH winning cluster:
       - Spawn Wild (100% chance):
         - 50% chance: Regular Wild (WLD)
         - 50% chance: Explosivo Wild (EW)
         - Position: Random empty spot in cluster footprint
     - Remove winning symbols (including regular Wilds in clusters)
     - **NOTE: EWs in winning clusters are removed but WILL STILL EXPLODE**
     - Process any EW explosions (see step 4)
     - Apply gravity (symbols fall)
     - Increase multiplier (1x→2x→4x→8x→16x→32x)
     - Return to step 1 (new symbols drop)
   - If no clusters found:
     - Continue to step 4

4. **CHECK FOR EXPLOSIVO WILDS TO EXPLODE**
   - If any EWs present (landed this drop OR from winning clusters):
     - Each EW explodes in 3x3 area
     - Destroy ONLY low-pay symbols in explosion area
     - Preserve: High-pay (LDY), Wilds, other EWs, Scatters
     - Apply gravity (symbols fall)
     - Increase multiplier
     - Return to step 1 (new symbols drop)
   - If no EWs to explode:
     - End avalanche sequence

5. **AVALANCHE SEQUENCE COMPLETE**
   - If Scatters triggered Free Spins → Enter Free Spins
   - Otherwise → End spin, reset multiplier to 1x

### 12. Technical Specifications

**Performance Optimizations:**
- Union-Find algorithm for cluster detection (25x faster than BFS)
- Bit-packed grid storage option (16x memory reduction)
- NumPy arrays for efficient weight calculations
- Optimized symbol generation using cumulative distributions

**RTP Targets:**
- Base Game: 94.22%
- Feature Buy: 94.40%
- Max Win: 7,500x base bet

**Volatility:** High (confirmed through simulation variance analysis)

**Bet Range:**
- Minimum: €0.10
- Maximum: €100.00
- Configurable bet levels based on operator requirements

**Max Win Behavior:**
- When total win in a spin sequence reaches 7,500x, the round ends immediately
- All pending avalanches and features are cancelled
- The 7,500x win is awarded to the player

### 13. Audio/Visual Specifications

**Theme:** Festive Day of the Dead (Día de Muertos) celebration in a Mexican street setting

**Visual Design:**
- Vibrant nighttime street scene background
- Decorations: colorful flowers, paper lanterns, candles
- Animated skeleton characters playing instruments around the reels
- Explosion effects for EW feature - visually satisfying and clear
- Smooth avalanche animations showing symbols falling

**Audio Design:**
- Background music: Upbeat, festive Mexican-style soundtrack
- Sound effects needed:
  - Spin initiation
  - Symbol drops during avalanche
  - Cluster win celebration (scaled by size)
  - Wild spawn appearance
  - EW explosion (dramatic effect)
  - Multiplier increase
  - Scatter landing
  - Free Spins trigger fanfare
  - Big win celebrations
- Optional: Character voice-overs or musical stings for major events

### 14. Platform & Technical Requirements

**Platform:** HTML5 (JavaScript)

**Device Compatibility:**
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- iOS devices (iPhone, iPad)
- Android devices (phones, tablets)

**Orientation Support:**
- Portrait mode (mobile)
- Landscape mode (mobile and desktop)

**Performance Requirements:**
- 60 FPS animation target
- Sub-100ms response time for user actions
- Efficient memory usage for extended play sessions

### 15. Success Metrics

**Core KPIs:**
- Base Game RTP: 94.22% (±0.1%)
- Feature Buy RTP: 94.40% (±0.1%)
- Hit Frequency: Target 25-30% (any spin producing at least one win)
- Feature Trigger Frequency: 
  - Base: 1 in 150-200 spins
  - With 2x Boost: 1 in 75-100 spins
  - With 5x Boost: 1 in 30-40 spins
- Average Free Spins win multiplier: 50-70x
- Max win achievement: 7,500x

**Volatility Specifications:**
- Volatility Index: 9.0-9.5 (on 10-point scale)
- 95th percentile win: ~100-150x bet
- 99th percentile win: ~500-800x bet

**RTP Contribution Breakdown (estimated):**
- Base game regular wins: ~60-65%
  - EW explosions contribute: ~5-8% of base RTP
  - Wild spawning adds: ~10-15% to overall RTP
- Base game scatter-triggered free spins: ~30-35%
- Feature buy: 94.40% total RTP (includes 75x cost)
- Feature trigger formula: Base probability × Boost Factor (2x or 5x)

**Player Engagement Metrics:**
- Average session duration
- Bet level distribution
- Feature Buy usage rate
- Bet+ option adoption rates

### 16. Edge Cases & Limits

**Maximum Symbol Constraints:**
- No hard limit on number of wilds (W or EW) on grid
- Theoretically all 25 positions could be wilds (extremely improbable)
- No artificial restrictions on symbol placement

**Scatter Behavior:**
- Scatters do NOT participate in cluster wins
- Scatters cannot be removed by winning clusters
- Scatters are immune to EW explosions
- New scatters CAN drop during avalanche after 3+ already triggered
- No positional restrictions on scatter drops
- No maximum scatter count per spin (RTP protected by probability weights)
- Multiple scatter triggers in same spin only count once

**Max Win Cap Behavior:**
- When any win reaches 7,500x during avalanche: round ends IMMEDIATELY
- All pending avalanches cancelled
- All pending features cancelled
- If Free Spins were triggered but not entered: cancelled
- The 7,500x is awarded as final win

**Additional Edge Cases:**
- If all positions become empty (theoretical): new symbols drop using standard P_BG/P_FS weights
- Spawned wilds landing on falling symbols: gravity completes first
- Multiple EWs in winning cluster: all removed but all still explode
- EW spawned in position about to be exploded: spawning happens first, then explosion
- Spawned EW landing and forming cluster: removed as part of cluster but still explodes in step 4 (follows "landed this drop" rule)

### 17. Out of Scope

The following features are explicitly NOT included in this version:
- Progressive jackpots
- Gamble/Double-up features
- Tournament functionality
- Social/multiplayer features
- Complex narrative elements beyond theme
- Mini-games

This PRD provides a complete specification for implementing Esqueleto Explosivo 3, with detailed mechanics, visual examples, and mathematical models to ensure accurate game behavior and target RTP achievement.