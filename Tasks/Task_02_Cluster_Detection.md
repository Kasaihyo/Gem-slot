# Task 02: Cluster Detection System

**Priority:** Critical
**Status:** Not Started
**Estimated Effort:** 2 days

## Description
Implement the cluster pays winning system that detects groups of 5 or more connected symbols. This is the core winning mechanic of the game and must handle complex scenarios including wild substitutions and multiple simultaneous clusters.

## Technical Requirements
- Minimum cluster size: 5 symbols
- Maximum tracked size: 15+ (all clusters ≥15 pay the same)
- Connections: Horizontal and vertical only (NO diagonals)
- Must use Union-Find algorithm for performance (25x faster than BFS per technical doc)
- Single wild can participate in multiple clusters simultaneously

## Subtasks

### 2.1 Union-Find Algorithm Implementation
**Description:** Implement the Union-Find (Disjoint Set) data structure for efficient cluster detection
- Create UnionFind class with path compression optimization
- Implement find() with path compression
- Implement union() with rank optimization
- Support for 25 positions (5x5 grid)
- Reset/clear functionality for reuse between checks

**Acceptance Criteria:**
- Find operation has near O(1) amortized complexity
- Union operation properly merges sets
- Path compression reduces tree height
- Can handle all 25 grid positions
- Reusable without memory allocation

### 2.2 Cluster Detection Core Logic
**Description:** Implement the main cluster detection algorithm using Union-Find
- Create findClusters() method in grid.py or separate clusters.py
- Iterate through grid positions and union adjacent matching symbols
- Handle symbol matching rules (same symbol or wild substitution)
- Group connected components by their root
- Return list of clusters with positions and symbol type

**Acceptance Criteria:**
- Detects all valid clusters of 5+ symbols
- Correctly handles horizontal/vertical connections only
- No diagonal connections counted
- Returns cluster data: positions, size, symbol type
- Performance meets requirements for millions of runs

### 2.3 Wild Substitution Logic
**Description:** Implement complex wild participation rules
- Wild (WLD) and Explosivo Wild (EW) substitute for all paying symbols
- Single wild can be part of multiple different clusters
- Wild connects clusters of different symbols if adjacent to both
- Each cluster independently "claims" any connected wilds
- Wilds do NOT form clusters by themselves

**Acceptance Criteria:**
- Wild at position (2,2) can be in both Pink cluster and Blue cluster if adjacent to both
- All valid clusters found independently
- No double-counting of wins
- Wilds included in cluster size count
- Pure wild clusters (only wilds) are NOT valid

### 2.4 Cluster Validation and Filtering
**Description:** Validate and filter detected clusters according to game rules
- Filter out clusters smaller than 5 symbols
- Ensure scatters (SCR) never participate in clusters
- Cap cluster size reporting at 15+ for payout purposes
- Validate that each cluster has at least one non-wild symbol
- Sort clusters by value or size for consistent processing order

**Acceptance Criteria:**
- Only clusters of 5+ symbols returned
- Scatter symbols never included in clusters
- Cluster size capped at 15 for payout calculation
- No pure-wild clusters in results
- Consistent ordering for deterministic behavior

### 2.5 Multi-Cluster Handling
**Description:** Handle scenarios with multiple simultaneous winning clusters
- Process all clusters independently
- Track which positions belong to which clusters
- Handle overlapping clusters (shared wild positions)
- Prepare cluster data for payout calculation
- Support cluster footprint tracking for wild spawning

**Acceptance Criteria:**
- All valid clusters detected in single pass
- Shared positions tracked correctly
- Each cluster has independent position list
- Cluster footprints available for wild spawning
- No interference between cluster processing

### 2.6 Performance Optimization
**Description:** Optimize cluster detection for high-frequency use
- Minimize memory allocations
- Use efficient data structures
- Consider caching adjacent position calculations
- Profile and optimize the hot path
- Ensure Union-Find optimizations are working

**Acceptance Criteria:**
- Cluster detection completes in <1ms for typical grid
- No heap allocations in inner loops
- Union-Find achieves expected performance gains
- Scalable to millions of simulations
- Measurable 25x improvement over BFS approach

### 2.7 Edge Case Handling
**Description:** Handle all edge cases mentioned in PRD
- Grid with all wilds (theoretical but possible)
- Clusters extending to grid edges
- Multiple clusters sharing single wild
- L-shaped and complex cluster patterns
- Empty grid (no clusters)

**Acceptance Criteria:**
- All edge cases handled correctly
- No crashes or undefined behavior
- Consistent results for complex patterns
- Proper handling of boundary positions
- Graceful handling of impossible scenarios

## Dependencies
- Grid system (Task 01) must be complete
- Symbol system with type checking
- Clear definition of symbol matching rules

## Testing Requirements
- Unit tests for Union-Find operations
- Integration tests for various cluster patterns
- Performance benchmarks comparing to BFS
- Test cases from PRD examples (8 Pink cluster with Wild)
- Edge case coverage tests
- Regression tests for deterministic behavior

## Notes
- This is performance-critical code - will run millions of times
- Union-Find is specifically mentioned as 25x faster than BFS
- Must handle the complex wild participation rules correctly
- Consider creating visual debugging tools for cluster validation
- Keep cluster detection separate from payout calculation