# Wild Spawning System Integration Guide

## Overview
The wild spawning system is a critical game mechanic that triggers after winning clusters are removed. It guarantees a wild spawn for each winning cluster with a 50/50 chance of spawning either a regular Wild (WLD) or Explosivo Wild (EW).

## Integration Points

### 1. Game Flow Integration

The wild spawning should be integrated into the avalanche sequence at this specific point:

```python
# Avalanche sequence order:
1. Detect winning clusters
2. Calculate wins
3. Store cluster footprints (IMPORTANT: before removal)
4. Remove winning symbols
5. **SPAWN WILDS HERE** (before gravity)
6. Apply gravity
7. Drop new symbols
8. Check for Explosivo Wilds to explode
```

### 2. Code Example

```python
from simulator.core.wild_spawning import WildSpawningSystem
from simulator.core.clusters import ClusterDetector
from simulator.core.grid import Grid
from simulator.core.rng import SpinRNG

# Initialize systems
wild_system = WildSpawningSystem()
cluster_detector = ClusterDetector()
grid = Grid()
rng = SpinRNG(seed=12345)

# Game flow
def process_avalanche(grid, rng):
    # 1. Detect clusters
    clusters = cluster_detector.find_clusters(grid)
    
    if not clusters:
        return False  # No wins, avalanche ends
    
    # 2. Calculate wins (implementation depends on paytable system)
    # ...
    
    # 3. Important: Store footprints before removal!
    # (The cluster positions are already stored in cluster.positions)
    
    # 4. Remove winning symbols
    winning_positions = cluster_detector.get_winning_positions(clusters)
    grid.remove_positions(winning_positions)
    
    # 5. SPAWN WILDS - This is the key integration point
    spawn_results = wild_system.spawn_wilds_for_clusters(grid, clusters, rng)
    
    # Track spawned EW positions for explosion prevention
    spawned_ew_positions = [
        spawn.spawned_position 
        for spawn in spawn_results 
        if spawn.success and spawn.wild_type == Symbol.E_WILD
    ]
    
    # 6. Apply gravity
    grid.apply_gravity()
    
    # 7. Drop new symbols
    grid.drop_new_symbols(rng)
    
    # Continue with explosion checks, etc.
    return True
```

### 3. Important Considerations

#### Spawned EW Tracking
Spawned Explosivo Wilds must NOT explode in the same cascade where they spawn:

```python
class GameState:
    def __init__(self):
        self.spawned_ew_positions = set()
        
    def mark_spawned_ews(self, spawn_results):
        """Mark EWs that were just spawned to prevent explosion."""
        self.spawned_ew_positions.clear()
        for spawn in spawn_results:
            if spawn.success and spawn.wild_type == Symbol.E_WILD:
                self.spawned_ew_positions.add(spawn.spawned_position)
    
    def can_ew_explode(self, position):
        """Check if an EW at this position can explode."""
        return position not in self.spawned_ew_positions
```

#### Multiple Clusters
The system handles multiple clusters automatically with collision resolution:

```python
# Example with 3 simultaneous clusters
clusters = [cluster1, cluster2, cluster3]
spawn_results = wild_system.spawn_wilds_for_clusters(grid, clusters, rng)

# Each cluster gets a spawn attempt
# Collisions are resolved automatically
# Failed spawns are tracked in spawn.success
```

#### Edge Cases Handled
- Clusters with no empty positions (spawn fails gracefully)
- Overlapping cluster footprints (each cluster independently selects)
- Collision resolution (first-come-first-served)
- Grid boundary positions (only valid positions considered)

## Configuration

The wild type probabilities can be adjusted if needed:

```python
# In wild_spawning.py
class WildSpawningSystem:
    # Default: 50/50 split
    WILD_PROBABILITY = 0.5
    EXPLOSIVO_WILD_PROBABILITY = 0.5
    
    # Must always sum to 1.0
```

## Testing Integration

Always test the following scenarios:
1. Single cluster spawn
2. Multiple cluster spawns
3. Overlapping footprints
4. Full footprint (no empty positions)
5. EW spawn marking for explosion prevention
6. Deterministic behavior with fixed RNG seed

## Performance Notes

The wild spawning system is optimized for performance:
- O(n) complexity where n is cluster positions
- Minimal memory allocation
- Efficient position selection
- No recursive algorithms

## Future Enhancements

If spawn probabilities need to vary by game mode:

```python
class WildSpawningSystem:
    def __init__(self, wild_prob=0.5, ew_prob=0.5):
        self.WILD_PROBABILITY = wild_prob
        self.EXPLOSIVO_WILD_PROBABILITY = ew_prob
        # Validate probabilities sum to 1.0
```