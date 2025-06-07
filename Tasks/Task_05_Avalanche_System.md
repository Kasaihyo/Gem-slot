# Task 05: Avalanche System and Game Flow

**Priority:** Critical
**Status:** ✅ Done
**Started:** 2025-01-06
**Completed:** 2025-01-06
**Estimated Effort:** 2 days

## Description
Implement the complete avalanche cascade system that orchestrates the game flow from initial spin through all cascading wins. This is the core game loop that coordinates all other mechanics in the correct sequence.

## Technical Requirements
- Implement the 5-step game flow from PRD section 11
- Manage state transitions between cascade steps
- Track multiplier progression (1x → 2x → 4x → 8x → 16x → 32x)
- Handle cascade termination conditions
- Coordinate all subsystems in correct order

## Subtasks

### 5.1 Game Flow State Machine
**Status:** ⬜ Not Started
**Description:** Implement the main game flow state machine
- Define states: REEL_DROP, CHECK_SCATTERS, CHECK_CLUSTERS, CHECK_EXPLOSIONS, SEQUENCE_COMPLETE
- Implement state transition logic
- Ensure single path through states (no loops within states)
- Track current state and cascade count
- Support state inspection for debugging

**Acceptance Criteria:**
- [ ] All 5 game flow states defined
- [ ] Transitions follow PRD flow diagram
- [ ] No invalid state transitions possible
- [ ] Current state always known
- [ ] State history trackable for debugging

### 5.2 Initial Reel Drop
**Status:** ⬜ Not Started
**Description:** Implement initial spin and subsequent cascade drops
- Fill all empty positions with new symbols
- Use appropriate weights (P_BG or P_FS)
- Handle special modifiers (Bet+ options)
- Track whether this is initial drop or cascade drop
- Support "The Enrico Show" (force 1 EW on initial drop)

**Acceptance Criteria:**
- [ ] All 25 positions filled on initial spin
- [ ] Empty positions filled on cascade drops
- [ ] Correct weight distribution applied
- [ ] Bet+ modifiers working correctly
- [ ] Drop type (initial/cascade) tracked

### 5.3 Scatter Detection and Tracking
**Status:** ⬜ Not Started
**Description:** Implement scatter counting and free spins triggering
- Count all visible scatters after each drop
- Track if 3+ scatters present (free spins triggered)
- Continue cascade even if free spins triggered
- Enter free spins only after cascade complete
- Handle multiple scatter triggers in same spin

**Acceptance Criteria:**
- [ ] Accurate scatter counting
- [ ] Free spins trigger at 3+ scatters
- [ ] Cascade continues after trigger
- [ ] Free spins entry deferred properly
- [ ] Multiple triggers count as one

### 5.4 Cascade Loop Orchestration
**Status:** ⬜ Not Started
**Description:** Implement the main cascade loop logic
- Check for winning clusters
- Process wins and remove symbols
- Spawn wilds for each cluster
- Apply gravity
- Process EW explosions when appropriate
- Increment multiplier after wins/explosions
- Loop back to reel drop

**Acceptance Criteria:**
- [ ] Correct sequence of operations
- [ ] All subsystems called in order
- [ ] Multiplier incremented at right times
- [ ] Loop continues while wins occur
- [ ] Clean termination when no wins

### 5.5 Multiplier Management
**Status:** ⬜ Not Started
**Description:** Implement the progressive multiplier system
- Start at 1x for each new spin
- Progress: 1x → 2x → 4x → 8x → 16x → 32x
- Increment after each winning cascade
- Increment after EW explosions
- Reset to 1x on new spin
- Different progression for free spins

**Acceptance Criteria:**
- [ ] Correct multiplier progression
- [ ] Increment timing matches PRD
- [ ] Reset on new spin (base game)
- [ ] No increment beyond 32x (base game)
- [ ] State clearly tracked

### 5.6 Win Accumulation and Max Win
**Status:** ⬜ Not Started
**Description:** Track total win and implement max win cap
- Accumulate all wins during cascade sequence
- Apply current multiplier to each win
- Check for 7,500x max win cap
- Immediately end round if max win reached
- Cancel all pending features at max win

**Acceptance Criteria:**
- [ ] Accurate win accumulation
- [ ] Multipliers applied correctly
- [ ] Max win check after each win
- [ ] Immediate termination at 7,500x
- [ ] All features cancelled at max win

### 5.7 Cascade Termination Logic
**Status:** ⬜ Not Started
**Description:** Implement cascade termination conditions
- End when no clusters found AND no EWs to explode
- Enter free spins if triggered (after cascade end)
- Reset multiplier to 1x (base game)
- Clear cascade-specific state
- Prepare for next spin

**Acceptance Criteria:**
- [ ] Cascade ends at correct conditions
- [ ] Free spins entry handled properly
- [ ] Multiplier reset in base game
- [ ] All cascade state cleared
- [ ] Ready for next spin

### 5.8 Integration Testing Framework
**Status:** ⬜ Not Started
**Description:** Create comprehensive integration tests
- Test complete cascade sequences
- Verify state transitions
- Test multiplier progression
- Test max win behavior
- Test free spins triggering
- Create replay system for debugging

**Acceptance Criteria:**
- [ ] Full cascade sequences tested
- [ ] Edge cases covered
- [ ] Deterministic replay capability
- [ ] Performance benchmarks included
- [ ] Visual debugging tools

## Dependencies
- All core systems must be complete:
  - Grid system (Task 01)
  - Cluster detection (Task 02)
  - Wild spawning (Task 03)
  - EW explosions (Task 04)
- RNG system for deterministic behavior
- Configuration system for game parameters

## Testing Requirements
- Integration tests for complete game flows
- State machine validation tests
- Multiplier progression tests
- Max win cap tests
- Free spins trigger tests
- Performance tests for cascade sequences
- Replay system for debugging complex cascades

## Game Flow Sequence (from PRD)
1. **REEL DROP** → Fill empty positions
2. **CHECK SCATTERS** → Count and mark FS trigger
3. **CHECK CLUSTERS** → Process wins, spawn wilds
4. **CHECK EXPLOSIONS** → Process EW explosions
5. **SEQUENCE COMPLETE** → Enter FS or end spin

## Notes
- This is the core game loop - must be rock solid
- Performance critical for millions of simulations
- State management crucial for debugging
- Must maintain deterministic behavior
- Consider detailed logging for cascade replay