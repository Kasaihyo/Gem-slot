# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


# Workflow Rules

## Task Management Process

### 1. Finding Next Task
- Navigate to `/Tasks` directory to find all available tasks
- Look for tasks with **Status: Not Started** 
- Prioritize by **Priority** level (Critical > High > Medium > Low)

### 2. Starting a Task
- Update task status from **Not Started** to **In Progress**
- Mark current date/time when starting
- Break down into subtasks and tackle systematically

### 3. Research Phase (ALWAYS DO THIS FIRST)
- **BEFORE starting any task, consult `/Users/temogiorgadze/Documents/FluxGaming/Gem slot/Docs`**
- This documentation contains the source of truth and detailed scenarios
- Look for relevant game mechanics, edge cases, and implementation details
- Cross-reference with PRD (Product Requirements Document) for clarification
- Understand the complete context before writing any code

### 4. Implementation Guidelines
- Follow the technical requirements exactly as specified in task files
- Use the acceptance criteria as your checklist
- Implement unit tests for each component
- Ensure code follows the established patterns and architecture

### 5. Task Completion
- Verify all acceptance criteria are met
- Run comprehensive tests
- Update task status from **In Progress** to **Done**
- Mark completion date/time
- Document any deviations or additional notes

### 6. Quality Assurance
- Always reference the Docs folder for game rule clarifications
- Test edge cases and scenarios described in documentation
- Ensure implementation matches the intended game behavior
- Validate against performance requirements where applicable


## Project Overview

Esqueleto Explosivo 3 is a 5x5 grid slot game featuring cluster pays mechanics, cascading avalanches, explosive wilds, and progressive multipliers. The game is set in a Day of the Dead celebration theme with potential wins up to 7,500x bet.

## Game Architecture

### Core Game Mechanics
- **5x5 Grid** with cluster pays (5+ symbols connected horizontally/vertically)
- **Avalanche System**: Winning symbols removed, new symbols drop with gravity
- **Multiplier Progression**: 1x → 2x → 4x → 8x → 16x → 32x per avalanche sequence
- **Wild Spawning**: 100% chance after wins (50% regular Wild, 50% Explosivo Wild)
- **Explosivo Wilds**: Explode in 3x3 area, destroying only low-pay symbols

### Symbol System
- **High Pay**: Lady Skull (LDY)
- **Low Pay**: Pink (PNK), Green (GRN), Blue (BLU), Orange (ORG), Cyan (CYN)
- **Special**: Wild (WLD), Explosivo Wild (EW), Scatter (SCR)

### Free Spins Feature
- Triggered by 3+ Scatters
- Persistent multiplier system with upgrades
- EW collection mechanic: 3 EWs = +1 base multiplier level + 1 spin
- Maximum multiplier: 1024x

## Technical Implementation

### Platform Requirements
- HTML5 (JavaScript)
- Cross-platform: Desktop browsers, iOS, Android
- Performance: 60 FPS target, <100ms response time

### Key Technical Patterns
- **Union-Find Algorithm** for cluster detection (25x faster than BFS)
- **Deterministic RNG** through SpinRNG wrapper pattern
- **Configuration Management**: Centralized in config.py with dual dict/array storage
- **Memory Optimization**: Reuse patterns, lazy evaluation, vectorized operations

### Symbol Weight Distribution
```python
# Base Game weights normalized at runtime
BG_WEIGHTS = {
    "LADY_SK": 3,    # ~2.5%
    "PINK_SK": 14,   # ~11.7%
    "GREEN_SK": 16,  # ~13.3%
    "BLUE_SK": 18,   # ~15.0%
    "ORANGE_SK": 20, # ~16.7%
    "CYAN_SK": 22,   # ~18.3%
    "WILD": 12,      # ~10.0%
    "E_WILD": 8,     # ~6.7%
    "SCATTER": 7     # ~5.8%
}
```

### Performance Targets
- Base Game RTP: 94.22%
- Feature Buy RTP: 94.40%
- Max Win: 7,500x base bet
- Volatility: High (9.0-9.5 on 10-point scale)

## Development Guidelines

### Code Organization
- Game mechanics in `simulator/core/grid.py`
- Configuration in `simulator/config.py`
- RNG management in `simulator/core/rng.py`
- State management in `simulator/core/state.py`

### Testing Requirements
- Unit tests for each component
- Integration tests for game flows
- Regression tests for determinism
- Performance benchmarks

### Critical Implementation Notes
- Wilds can participate in multiple clusters simultaneously
- EWs in winning clusters are removed but still explode
- Spawned EWs only explode in the cascade where they land
- Max win cap (7,500x) ends round immediately
- Scatters are immune to explosions and don't participate in clusters