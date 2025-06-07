# Task 01: Core Game Grid Implementation

**Priority:** Critical
**Status:** ✅ Done
**Estimated Effort:** 2-3 days
**Completed:** 2025-01-06

## Description
Implement the fundamental 5x5 grid system that serves as the foundation for Esqueleto Explosivo 3. This includes the grid data structure, symbol management, and basic grid operations like gravity and symbol dropping.

## Technical Requirements
- Grid must be exactly 5x5 (25 positions)
- Row and column indexing: Row 0-4, Column 0-4
- Symbol storage must support all 9 symbol types (LDY, PNK, GRN, BLU, ORG, CYN, WLD, EW, SCR)
- Grid operations must be deterministic and reproducible

## Subtasks

### 1.1 Grid Data Structure Implementation
**Description:** Create the core grid data structure in simulator/core/grid.py
- Implement a 5x5 grid using appropriate data structure (likely 2D array or flat array with index mapping)
- Define constants for grid dimensions (ROWS = 5, COLS = 5)
- Create position indexing system (row, col) with validation
- Implement grid initialization with empty positions
- Add method to convert between (row, col) and flat index
- Ensure thread-safe operations for future parallel processing

**Acceptance Criteria:**
- Grid can store all 9 symbol types plus empty state
- Position validation prevents out-of-bounds access
- Grid state can be copied/cloned for state management
- Unit tests cover all basic grid operations

### 1.2 Symbol System Implementation
**Description:** Create the symbol management system in simulator/core/symbol.py
- Define symbol enum/constants: LDY, PNK, GRN, BLU, ORG, CYN, WLD, EW, SCR
- Implement symbol properties (isLowPay, isHighPay, isWild, isScatter)
- Create symbol type checking methods
- Define symbol display mappings for debugging/visualization
- Implement symbol substitution rules (Wild substitutes for paying symbols)

**Acceptance Criteria:**
- All 9 symbols defined with correct properties
- Low-pay symbols: PNK, GRN, BLU, ORG, CYN
- High-pay symbol: LDY
- Special symbols: WLD (Wild), EW (Explosivo Wild), SCR (Scatter)
- Symbol type checking methods work correctly

### 1.3 Gravity System Implementation
**Description:** Implement the gravity mechanic that makes symbols fall after removals
- Create applyGravity() method in grid.py
- Symbols must fall straight down to fill empty spaces
- Multiple symbols in same column fall maintaining their relative order
- Gravity applies column by column independently
- Must handle partial column collapses correctly

**Acceptance Criteria:**
- Symbols fall to lowest available position in their column
- No floating symbols after gravity application
- Original symbol order preserved during fall
- Performance optimized for repeated gravity applications

### 1.4 Symbol Drop Mechanism
**Description:** Implement the system for dropping new symbols into empty positions
- Create dropNewSymbols() method that fills all empty positions
- Integrate with RNG system (SpinRNG) for symbol selection
- Use provided weight distributions (P_BG or P_FS based on game mode)
- Symbols drop from top, filling empty positions from top to bottom
- Must use normalized probability distributions

**Acceptance Criteria:**
- All empty positions filled after drop
- Correct probability distribution applied (BG or FS)
- Deterministic results with same RNG seed
- No position-specific weight adjustments (pure random)

### 1.5 Grid State Management
**Description:** Implement state tracking and validation for the grid
- Create methods to save/restore grid state
- Implement grid validation (no invalid symbols, proper structure)
- Add debugging visualization (ASCII representation matching PRD examples)
- Create method to count symbols by type
- Implement position querying methods

**Acceptance Criteria:**
- Grid state can be serialized/deserialized
- ASCII visualization matches PRD format exactly
- Symbol counting accurate for all types
- State validation catches any corruption

### 1.6 Performance Optimization
**Description:** Optimize grid operations for high-performance simulation
- Implement efficient symbol lookup tables
- Consider bit-packed storage (mentioned in technical doc as 16x memory reduction)
- Optimize gravity algorithm to minimize iterations
- Profile and optimize hot paths
- Ensure compatibility with NumPy operations where beneficial

**Acceptance Criteria:**
- Grid operations meet performance targets for millions of simulations
- Memory usage optimized (consider bit-packing if beneficial)
- No unnecessary object allocations in hot paths
- Compatible with future parallelization

## Dependencies
- Symbol constants must be defined first
- RNG system (SpinRNG) must be available for symbol dropping
- Weight configuration must be loaded from config.py

## Testing Requirements
- Unit tests for all grid operations
- Integration tests for gravity + symbol drop sequences
- Performance benchmarks for grid operations
- Regression tests to ensure deterministic behavior

## Notes
- Grid is foundation for all game mechanics - must be rock solid
- Consider future needs: cluster detection will traverse grid frequently
- Maintain clear separation between grid logic and game rules
- Follow established patterns from technical architecture document