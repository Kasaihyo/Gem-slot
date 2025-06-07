# Explosivo Wild Explosion System Integration Guide

## Overview
The explosion system manages Explosivo Wild (EW) explosions that destroy low-pay symbols in a 3x3 area. This document explains how to integrate the explosion system into the game flow.

## Key Components

### ExplosionSystem
Main class that manages all explosion mechanics:
- Tracks EW eligibility (landed vs spawned)
- Calculates 3x3 explosion areas
- Executes simultaneous explosions
- Tracks EW collection for free spins

### EWTracker
Tracks EW states:
- `landed_this_drop`: EWs from symbol generation
- `in_winning_clusters`: EWs that were in clusters
- `spawned_this_cascade`: EWs spawned (not eligible)
- `collected_count`: Total EWs collected

## Integration Flow

```python
from simulator.core.explosions import ExplosionSystem

# Initialize once per game session
explosion_system = ExplosionSystem()

# For each cascade:
def process_cascade(grid, clusters):
    # 1. Track EWs that landed this drop (after symbols drop)
    explosion_system.track_landed_ews(grid)
    
    # 2. If clusters found, track cluster EWs
    if clusters:
        explosion_system.track_cluster_ews(clusters, grid)
        # Remove cluster symbols...
        # Spawn wilds...
        
        # Track any spawned EWs
        for spawn in spawn_results:
            if spawn.wild_type == Symbol.E_WILD and spawn.success:
                explosion_system.track_spawned_ew(spawn.spawned_position)
    
    # 3. Apply gravity
    grid.apply_gravity()
    
    # 4. Check for new clusters
    new_clusters = cluster_detector.find_clusters(grid)
    
    # 5. If no clusters, check for explosions
    if explosion_system.should_check_explosions(clusters_found=len(new_clusters) == 0):
        explosion_events = explosion_system.execute_explosions(grid)
        
        # Apply gravity again after explosions
        if explosion_events:
            grid.apply_gravity()
    
    # 6. Reset for next cascade
    explosion_system.reset_cascade_state()
```

## Important Notes

### Timing
- Explosions occur ONLY when no winning clusters are found
- EWs in winning clusters are collected but removed before explosion check
- Spawned EWs are NOT eligible to explode in their spawn cascade

### EW Collection
- EWs are collected when:
  - They appear in winning clusters (collected immediately)
  - They explode (collected during explosion)
- Use `explosion_system.get_collected_count()` to track total
- Reset with `explosion_system.reset_collected_count()` when needed

### Explosion Rules
- Only destroys low-pay symbols (PNK, GRN, BLU, ORG, CYN)
- Preserves: High-pay (LDY), Wilds (WLD), other EWs, Scatters (SCR)
- All eligible EWs explode simultaneously (no chaining)
- 3x3 area centered on EW position (clipped at grid edges)

## Example Usage

```python
# Complete cascade example
def play_cascade(grid, rng):
    # Initial symbol drop
    drop_symbols(grid, rng)
    explosion_system.track_landed_ews(grid)
    
    while True:
        # Find clusters
        clusters = cluster_detector.find_clusters(grid)
        
        if clusters:
            # Track and remove cluster EWs
            explosion_system.track_cluster_ews(clusters, grid)
            remove_clusters(clusters, grid)
            
            # Spawn wilds
            spawns = wild_spawner.spawn_wilds_for_clusters(grid, clusters, rng)
            for spawn in spawns:
                if spawn.wild_type == Symbol.E_WILD and spawn.success:
                    explosion_system.track_spawned_ew(spawn.spawned_position)
            
            # Apply gravity and continue
            grid.apply_gravity()
        else:
            # No clusters - check explosions
            if explosion_system.should_check_explosions(clusters_found=False):
                events = explosion_system.execute_explosions(grid)
                if events:
                    grid.apply_gravity()
                    continue  # Check for new clusters after explosion
            
            # No clusters or explosions - cascade ends
            break
    
    # Reset for next cascade
    explosion_system.reset_cascade_state()
```

## Testing
See `tests/test_explosions.py` and `tests/test_explosions_integration.py` for comprehensive examples.