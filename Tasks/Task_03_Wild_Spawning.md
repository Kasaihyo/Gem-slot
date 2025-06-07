# Task 03: Wild Spawning System

**Priority:** High
**Status:** ✅ Done
**Started:** 2025-01-06
**Completed:** 2025-01-06
**Estimated Effort:** 1.5 days

## Description
Implement the guaranteed wild spawning mechanic that triggers after each winning cluster. This system is crucial for game flow as it ensures continued action and contributes 10-15% to overall RTP according to the PRD.

## Technical Requirements
- 100% spawn chance per winning cluster (guaranteed)
- 50% chance for regular Wild (WLD), 50% for Explosivo Wild (EW)
- Spawns in random empty position within cluster's original footprint
- Spawned EWs do NOT explode in the cascade they spawn
- Must handle collision when multiple clusters spawn simultaneously

## Subtasks

### 3.1 Cluster Footprint Tracking
**Description:** Track the original positions of winning clusters before removal
- Store cluster footprint (all positions) before symbols are removed
- Maintain footprint data through the removal process
- Support multiple cluster footprints simultaneously
- Ensure footprints are based on original positions, not post-removal

**Acceptance Criteria:**
- Each cluster's original positions preserved
- Footprint data available after symbol removal
- Multiple footprints tracked independently
- No modification of footprint during processing
- Efficient storage for position lists

### 3.2 Wild Type Selection Logic
**Description:** Implement the 50/50 probability split for wild type selection
- Use SpinRNG for random selection
- Exactly 50% probability for WLD vs EW
- Independent roll for each cluster
- Configurable probabilities (PRD mentions "tunable")
- Maintain deterministic behavior with seeded RNG

**Acceptance Criteria:**
- Equal probability for WLD and EW (50% each)
- Each cluster gets independent random roll
- Probabilities sum to exactly 1.0
- Configuration supports future tuning
- Deterministic with same RNG seed

### 3.3 Empty Position Selection
**Description:** Select random empty position within cluster footprint for spawning
- Identify all empty positions within cluster footprint
- Use RNG to select one random empty position
- Handle case where no empty positions exist
- Only consider positions that were part of the original cluster
- Ensure uniform random distribution

**Acceptance Criteria:**
- Only empty positions within footprint considered
- Uniform random selection from available positions
- Graceful handling when no positions available
- No selection outside cluster footprint
- Deterministic with same RNG seed

### 3.4 Collision Handling System
**Description:** Handle multiple clusters attempting to spawn in same position
- Process all clusters in consistent order
- First wild takes contested position
- Subsequent wilds re-roll within their footprint
- If entire footprint occupied, forfeit spawn
- No expansion beyond original footprint

**Acceptance Criteria:**
- Collision detection works correctly
- First-come-first-served resolution
- Re-roll stays within original footprint
- Forfeit spawn if no positions available
- No search area expansion
- Deterministic resolution order

### 3.5 Edge Case Handling
**Description:** Handle special cases for wild spawning
- Clusters entirely off-grid (theoretical edge case)
- Overlapping cluster footprints
- Cluster footprint with no empty spaces after removal
- Very small clusters (exactly 5 symbols)
- Clusters at grid boundaries

**Acceptance Criteria:**
- Off-grid positions excluded from selection
- Overlapping footprints handled independently
- Graceful forfeit when no space available
- Small clusters work correctly
- Boundary positions handled properly

### 3.6 Spawn Timing Integration
**Description:** Integrate spawning at correct point in game flow
- Spawning occurs AFTER cluster removal
- But BEFORE gravity is applied
- Spawned wilds participate in gravity
- Spawned EWs marked as "not landed this drop"
- Clear state tracking for spawn timing

**Acceptance Criteria:**
- Spawning happens at exactly the right moment
- Spawned wilds fall with gravity
- EW explosion eligibility tracked correctly
- No premature explosion of spawned EWs
- State clearly indicates spawn status

### 3.7 Multi-Cluster Spawn Coordination
**Description:** Coordinate spawning when multiple clusters win simultaneously
- All clusters attempt spawn in same phase
- Process in consistent order (not size/position based)
- Track successful spawns vs forfeits
- Maintain independence between clusters
- Log/track spawn results for debugging

**Acceptance Criteria:**
- All clusters get spawn opportunity
- Processing order is consistent
- Success/forfeit tracked per cluster
- No interference between spawns
- Clear logging of spawn outcomes

## Dependencies
- Cluster detection system (Task 02) must provide footprint data
- Grid system (Task 01) for position management
- RNG system (SpinRNG) for random selections
- Symbol system for wild type definitions

## Testing Requirements
- Unit tests for position selection algorithm
- Integration tests for multi-cluster scenarios
- Collision handling test cases
- Edge case coverage (no empty positions, off-grid)
- Statistical tests for 50/50 distribution
- Regression tests for deterministic behavior

## Example Scenario (from PRD)
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
```

## Notes
- This mechanic adds 10-15% to overall RTP - critical for game math
- Must maintain strict spawn timing to prevent premature EW explosions
- Performance important but less critical than cluster detection
- Consider visual debugging for spawn position selection
- Keep spawn logic separate from wild behavior logic