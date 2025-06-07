# Task 04: Explosivo Wild (EW) Explosion Mechanics

**Priority:** High
**Status:** ✅ Done
**Started:** 2025-01-06
**Completed:** 2025-01-06
**Estimated Effort:** 2 days

## Description
Implement the Explosivo Wild explosion feature that destroys low-pay symbols in a 3x3 area. This mechanic is critical for gameplay as it creates cascading opportunities and contributes 5-8% to base game RTP.

## Technical Requirements
- EW explodes in 3x3 area centered on its position
- Only destroys low-pay symbols (PNK, GRN, BLU, ORG, CYN)
- Preserves: High-pay (LDY), Wilds (WLD), other EWs, Scatters (SCR)
- All EWs explode simultaneously in single step
- Multiplier increases ONCE regardless of number of explosions

## Subtasks

### 4.1 Explosion Eligibility Tracking
**Status:** ✅ Done
**Description:** Track which EWs are eligible to explode in current cascade
- Track EWs that "landed this drop" (new from symbol drop)
- Track EWs that were part of winning clusters (marked for explosion)
- Maintain explosion eligibility through removal/gravity
- Clear eligibility state between cascades
- Handle spawned EWs (NOT eligible in spawn cascade)

**Acceptance Criteria:**
- [x] "Landed this drop" EWs correctly identified
- [x] Winning cluster EWs marked for explosion even if removed
- [x] Spawned EWs marked as ineligible until next cascade
- [x] State properly reset between cascades
- [x] No EWs incorrectly marked for explosion

### 4.2 3x3 Explosion Area Calculation
**Status:** ✅ Done
**Description:** Calculate the 3x3 area affected by each EW explosion
- Calculate 3x3 grid centered on EW position
- Handle explosions near grid edges (partial 3x3 areas)
- Only include valid on-grid positions
- Support multiple explosion areas
- Consider overlapping explosion areas

**Acceptance Criteria:**
- [x] Correct 3x3 area for center positions
- [x] Proper clipping at grid boundaries
- [x] No off-grid positions included
- [x] Accurate position lists for each explosion
- [x] Efficient calculation without redundancy

### 4.3 Symbol Destruction Rules
**Status:** ✅ Done
**Description:** Implement rules for which symbols can be destroyed
- Identify low-pay symbols: PNK, GRN, BLU, ORG, CYN
- Preserve high-pay (LDY), wilds (WLD), other EWs, scatters (SCR)
- Apply destruction to grid positions
- Handle overlapping explosions (destroy only once)
- Track destroyed positions for gravity

**Acceptance Criteria:**
- [x] Only low-pay symbols destroyed
- [x] Special symbols always preserved
- [x] Each position destroyed maximum once
- [x] Destruction applied correctly to grid
- [x] No unintended symbol removal

### 4.4 Simultaneous Explosion Processing
**Status:** ✅ Done
**Description:** Process all eligible EW explosions in single atomic step
- Collect all eligible EWs before processing
- Calculate all explosion areas
- Apply all destructions simultaneously
- No chain reactions within same step
- Single multiplier increment regardless of count

**Acceptance Criteria:**
- [x] All eligible EWs processed together
- [x] No sequential processing
- [x] No chain reactions in same step
- [x] Multiplier incremented exactly once
- [x] Atomic operation (all or nothing)

### 4.5 EW Collection Tracking (Free Spins)
**Status:** ✅ Done
**Description:** Track EW collection for free spins feature
- Count EWs removed by winning clusters
- Count EWs that explode (including non-cluster explosions)
- Avoid double-counting (cluster + explosion = 1 collection)
- Maintain collection count through session
- Support collection state persistence

**Acceptance Criteria:**
- [x] Accurate EW collection count
- [x] No double-counting of same EW
- [x] Collections persist between spins
- [x] Non-cluster exploding EWs counted
- [x] State can be saved/restored

### 4.6 Edge Case Handling
**Status:** ✅ Done
**Description:** Handle complex explosion scenarios from PRD
- EW in winning cluster that would be destroyed by another EW
- Multiple EWs with overlapping explosion areas
- EW spawned in position about to be exploded
- EWs at grid corners/edges
- All positions destroyed scenario

**Acceptance Criteria:**
- [x] Cluster removal happens before explosion consideration
- [x] Overlapping areas handled correctly
- [x] Spawn-then-explode sequence correct
- [x] Edge explosions clip properly
- [x] Graceful handling of empty grid

### 4.7 Explosion Timing Integration
**Status:** ✅ Done
**Description:** Integrate explosions at correct point in cascade sequence
- Explosions occur AFTER win calculation
- But BEFORE gravity application
- Only if no winning clusters found
- Or after cluster processing complete
- Clear state management for timing

**Acceptance Criteria:**
- [x] Explosions at correct cascade step
- [x] Proper check for "no clusters" condition
- [x] State clearly indicates explosion phase
- [x] No premature explosions
- [x] Correct flow to gravity after explosions

## Dependencies
- Grid system (Task 01) for position management
- Symbol system for type identification
- Cluster detection (Task 02) for winning cluster EWs
- Game flow integration for timing

## Testing Requirements
- Unit tests for explosion area calculation
- Integration tests for simultaneous explosions
- Edge case tests from PRD examples
- Collection counting accuracy tests
- Timing sequence validation tests
- Visual debugging for explosion areas

## Example from PRD
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

After: PNK & CYN at (2,1) and (2,3) destroyed
       GRN, EW & BLU at (3,1), (3,2), (3,3) destroyed
       CYN & GRN at (4,1) and (4,2) destroyed
       WLD at (2,2), LDY at (3,4), and SCR at (4,3) survive
```

## Notes
- EW explosions contribute 5-8% to base RTP
- Critical timing: cluster removal → explosion → gravity
- No chain reactions within same cascade step
- Complex collection rules for free spins
- Performance less critical than cluster detection