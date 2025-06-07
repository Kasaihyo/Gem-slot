# Task 07: Configuration and RNG System

**Priority:** Critical (Foundation)
**Status:** ✅ Done
**Estimated Effort:** 2 days
**Completed:** 2025-01-06

## Description
Implement the configuration management system and deterministic RNG wrapper as described in the technical architecture. This includes dual-storage weight management, SpinRNG wrapper, and runtime validation.

## Technical Requirements
- Dual-storage approach: Python dicts (primary) + NumPy arrays (performance)
- SpinRNG wrapper for controlled randomness
- JSON-based weight persistence
- Runtime validation with fail-fast pattern
- Support for parallel determinism

## Subtasks

### 7.1 Symbol Weight Configuration
**Status:** ✅ Done
**Description:** Implement the dual-storage weight management system
- Define SYMBOL_GENERATION_WEIGHTS_BG dictionary
- Define SYMBOL_GENERATION_WEIGHTS_FS dictionary
- Create NumPy arrays (BG_SYMBOL_NAMES, BG_WEIGHTS, etc.)
- Implement dict-to-array conversion
- Support runtime weight updates with array regeneration

**Acceptance Criteria:**
- [ ] Base game weights match PRD specifications
- [ ] Free spins weights show correct enrichment
- [ ] NumPy arrays generated from dictionaries
- [ ] Arrays regenerate when dicts update
- [ ] Weights sum to 1.0 when normalized

### 7.2 SpinRNG Wrapper Implementation
**Status:** ✅ Done
**Description:** Create the RNG wrapper for deterministic behavior
- Implement SpinRNG class wrapping random.Random
- Limited interface (only expose needed methods)
- Support seed initialization
- Implement random(), randint(), choice() methods
- Prevent untracked randomness

**Acceptance Criteria:**
- [ ] SpinRNG provides controlled interface
- [ ] Deterministic with same seed
- [ ] No access to unwrapped RNG
- [ ] All randomness channeled through wrapper
- [ ] Future-proof for RNG engine swap

### 7.3 Parallel Determinism Support
**Status:** ✅ Done
**Description:** Implement deterministic parallel execution support
- Worker seed generation: base_seed + worker_id
- No inter-worker correlation
- Reproducible results across workers
- Support for distributed simulation
- Clear seed management strategy

**Acceptance Criteria:**
- [ ] Each worker has unique deterministic seed
- [ ] No correlation between worker results
- [ ] Results reproducible with same base seed
- [ ] Scalable to many workers
- [ ] Clear documentation of seeding strategy

### 7.4 Configuration Validation System
**Status:** ✅ Done
**Description:** Implement runtime validation with fail-fast pattern
- Create validate_config() function
- Check weight sums are positive
- Verify symbol sets match between BG/FS
- Ensure arrays align with dictionaries
- Run validation at import time

**Acceptance Criteria:**
- [ ] All invariants checked at startup
- [ ] Clear error messages for violations
- [ ] Fail-fast prevents subtle bugs
- [ ] Validation runs automatically
- [ ] Performance impact minimal

### 7.5 JSON Weight Persistence
**Status:** ✅ Done
**Description:** Implement save/load functionality for weights
- Create save_weights() function
- Include timestamp in saved data
- Save both BG and FS weights
- Implement load_weights() function
- Support version control and A/B testing

**Acceptance Criteria:**
- [ ] Weights saved to JSON format
- [ ] Timestamp included for tracking
- [ ] Both weight sets persisted
- [ ] Loading restores exact state
- [ ] File format supports versioning

### 7.6 Paytable Configuration
**Status:** ✅ Done
**Description:** Implement paytable data structure from PRD
- Define payout values for all symbols
- Support cluster sizes 5 through 15+
- Match exact values from PRD table
- Efficient lookup structure
- Support for future modifications

**Acceptance Criteria:**
- [ ] All payout values match PRD exactly
- [ ] Efficient lookup by symbol and size
- [ ] 15+ clusters handled correctly
- [ ] No hardcoded values in game logic
- [ ] Easy to modify for balancing

### 7.7 Bet Configuration and Modifiers
**Status:** ✅ Done
**Description:** Implement bet-related configuration
- Base bet range: €0.10 to €100.00
- Bet+ multipliers: 1.5x, 2x, 3x
- Feature Buy cost: 75x
- Scatter probability modifications
- RTP targets for each mode

**Acceptance Criteria:**
- [ ] Bet range enforced correctly
- [ ] Bet+ modifiers applied properly
- [ ] Feature Buy cost calculated
- [ ] Probability modifications work
- [ ] RTP targets documented

### 7.8 Configuration Hot Reload (Future-Ready)
**Status:** ✅ Done
**Description:** Prepare architecture for future hot reload capability
- Separate configuration from code logic
- Clear configuration access patterns
- No cached values in game logic
- Support for configuration observers
- Document hot reload integration points

**Acceptance Criteria:**
- [ ] Configuration cleanly separated
- [ ] No hardcoded config values
- [ ] Access patterns support updates
- [ ] Observer pattern considered
- [ ] Integration points documented

## Dependencies
- Must be completed before any game logic
- Foundation for all other systems
- Required by symbol generation
- Required by weight-based features

## Testing Requirements
- Unit tests for weight normalization
- Validation test coverage
- RNG determinism tests
- Parallel seed generation tests
- Configuration save/load tests
- Performance benchmarks for array operations

## Configuration Structure (from Technical Doc)
```python
# Primary storage: Python dictionaries
SYMBOL_GENERATION_WEIGHTS_BG = {
    "LADY": 0.025,    # ~2.5%
    "PINK": 0.117,    # ~11.7%
    # ... etc
}

# Secondary storage: NumPy arrays for performance
BG_SYMBOL_NAMES = np.array([...])
BG_WEIGHTS = np.array([...])
```

## Notes
- This is THE foundation - must be implemented first
- Performance critical for millions of simulations
- Determinism is non-negotiable requirement
- Clean architecture enables future enhancements
- Consider configuration UI for future iterations