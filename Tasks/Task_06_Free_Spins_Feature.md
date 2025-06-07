# Task 06: Free Spins Feature Implementation

**Priority:** High
**Status:** Not Started
**Estimated Effort:** 3 days

## Description
Implement the complete free spins feature including enhanced multiplier system, EW collection mechanics, base multiplier upgrades, and retrigger functionality. This feature contributes 30-35% of the base game RTP.

## Technical Requirements
- Persistent base multiplier with 6-step trails
- EW collection system (3 EWs = 1 upgrade)
- Base multiplier levels: 1x, 2x, 4x, 8x, 16x, 32x
- Trail progression: base → base×2 → base×4 → base×8 → base×16 → base×32
- Maximum multiplier: 1024x

## Subtasks

### 6.1 Free Spins State Management
**Status:** ⬜ Not Started
**Description:** Implement state tracking for free spins session
- Track number of spins remaining
- Track current base multiplier level
- Track EWs collected (0-2 carried between spins)
- Track total free spins win
- Support state save/restore for recovery
- Maintain free spins history for debugging

**Acceptance Criteria:**
- [ ] All state variables properly tracked
- [ ] State persists between spins
- [ ] State can be serialized/restored
- [ ] No state leakage between sessions
- [ ] Clear state initialization

### 6.2 Free Spins Triggering
**Status:** ⬜ Not Started
**Description:** Implement scatter-based triggering system
- Detect 3+ scatters in base game
- Award spins: 3 SCR=10, 4 SCR=12, 5+ SCR=12+(N-4)×2
- Defer entry until cascade complete
- Handle Feature Buy (75x bet for 10 spins)
- Initialize free spins state correctly

**Acceptance Criteria:**
- [ ] Correct spin count for scatter triggers
- [ ] Free spins entry properly deferred
- [ ] Feature Buy awards exactly 10 spins
- [ ] Initial state correctly set
- [ ] Scatters that trigger don't count for retrigger

### 6.3 Enhanced Multiplier System
**Status:** ⬜ Not Started
**Description:** Implement the persistent base multiplier with trails
- Base levels: 1x, 2x, 4x, 8x, 16x, 32x
- Each level has 6-step trail progression
- Trail resets to base at START of each spin
- Trail progresses with each cascade win
- Maximum multiplier: 1024x (32x base with full trail)

**Acceptance Criteria:**
- [ ] All base levels implemented
- [ ] Trail progression matches PRD table
- [ ] Trail resets at spin start
- [ ] Progression capped at 1024x
- [ ] No trail persistence between spins

### 6.4 EW Collection and Upgrades
**Status:** ⬜ Not Started
**Description:** Implement EW collection mechanics
- Count EWs removed by ANY means (clusters or explosions)
- Every 3 EWs = 1 upgrade
- Each upgrade: +1 base level AND +1 spin
- Upgrades apply at START of next spin
- Unused EWs carry over (e.g., 2 EWs wait for 1 more)

**Acceptance Criteria:**
- [ ] EWs collected from clusters counted
- [ ] EWs collected from explosions counted
- [ ] No double-counting same EW
- [ ] 3:1 collection ratio enforced
- [ ] Upgrades deferred to next spin start
- [ ] Remainder EWs carried over

### 6.5 Retrigger System
**Status:** ⬜ Not Started
**Description:** Implement scatter retriggers during free spins
- Different trigger requirements: 2 SCR=+3, 3 SCR=+5, 4 SCR=+7, 5+ SCR=+7+(N-4)×2
- Spins added immediately when detected
- No maximum retrigger limit
- Original trigger scatters don't count
- Track total spins for session

**Acceptance Criteria:**
- [ ] Correct spin awards for each scatter count
- [ ] Immediate spin addition
- [ ] No retrigger limit enforced
- [ ] Trigger scatters excluded from first check
- [ ] Total spin count accurate

### 6.6 Free Spins Symbol Weights
**Status:** ⬜ Not Started
**Description:** Implement enriched symbol distribution for free spins
- Use P_FS weights instead of P_BG
- Wild enriched by 1.5x
- EW enriched by 2x
- Ensure ~3-5 EWs collected per 10 spins average
- Same weights for initial and cascade drops

**Acceptance Criteria:**
- [ ] P_FS weights correctly applied
- [ ] Wild/EW enrichment ratios correct
- [ ] Average EW collection rate achieved
- [ ] No position-specific adjustments
- [ ] Weights used consistently

### 6.7 Multiplier Trail Examples
**Status:** ⬜ Not Started
**Description:** Implement specific trail progressions from PRD
- 1x base: 1x → 2x → 4x → 8x → 16x → 32x
- 2x base: 2x → 4x → 8x → 16x → 32x → 64x
- 4x base: 4x → 8x → 16x → 32x → 64x → 128x
- Continue pattern up to 32x base
- Cap at 1024x maximum

**Acceptance Criteria:**
- [ ] Each base level has correct trail
- [ ] Multiplier calculation accurate
- [ ] 1024x cap enforced
- [ ] No multiplier overflow
- [ ] Trail position tracked correctly

### 6.8 Free Spins Completion
**Status:** ⬜ Not Started
**Description:** Handle free spins session completion
- Process final spin completely
- Calculate total session win
- Return to base game state
- Clear free spins state
- Handle max win during free spins

**Acceptance Criteria:**
- [ ] Clean session termination
- [ ] Total win calculated correctly
- [ ] Base game state restored
- [ ] Free spins state cleared
- [ ] Max win handled properly

## Dependencies
- Base game cascade system (Task 05)
- EW explosion tracking (Task 04)
- Scatter detection system
- Multiplier management system
- State management framework

## Testing Requirements
- Unit tests for upgrade mechanics
- Integration tests for full sessions
- Statistical tests for EW collection rates
- Trail progression validation
- Retrigger functionality tests
- Max win scenarios during free spins
- State persistence tests

## Example Free Spins Session (from PRD)
```
Spin 1: Base 1x, collect 2 EWs
Spin 2: Base 1x, collect 1 EW (Total: 3 EWs)
        → Upgrade pending: Base increases to 2x, +1 spin
Spin 3: Base 2x (upgraded), Trail: 2x→4x→8x→16x→32x→64x
        Avalanche progression: 2x→4x→8x
        Collect 4 more EWs (Total: 7 EWs)
Spin 4: Base 2x, 1 more EW (Total: 8 EWs, 6 used, 2 remain)
        → Upgrade pending: Base to 4x, +1 spin
```

## Notes
- Free spins contribute 30-35% of base RTP
- Complex multiplier system requires careful implementation
- EW collection is key engagement mechanic
- State management critical for session integrity
- Consider visual representation of multiplier trails