# A* Pathfinding Algorithm Implementation

This document describes the A* pathfinding algorithm implementation integrated with the Door's `find_closest_bin` function.

## Overview

The A* algorithm is a graph traversal and path search algorithm that finds the shortest path between nodes. In this implementation, it's used to find the optimal path from doors to bins while avoiding obstacles in the environment.

## Key Features

- **Efficient Pathfinding**: Uses A* algorithm with Manhattan distance heuristic
- **Obstacle Avoidance**: Navigates around walls and blocked areas using binary image data
- **Optimal Selection**: Each door is assigned to the bin with the shortest accessible path
- **Complete Integration**: Seamlessly integrated with existing Door and Bin entities
- **Path Storage**: Stores complete paths for later visualization or analysis

## Files Modified/Created

- `tools/astar.py` - Complete A* algorithm implementation
- `entities/doors.py` - Updated Door class with pathfinding integration
- `world/world.py` - Updated to use black/white images for pathfinding
- `test/test_astar.py` - Basic A* algorithm tests
- `test/test_integration.py` - Integration tests with Door/Bin system
- `test/test_advanced_astar.py` - Complex scenario testing
- `test/test_world_example.py` - Usage examples and demonstration

## API Reference

### A* Algorithm (`tools/astar.py`)

#### `Astar` Class
```python
class Astar:
    def __init__(self, start: Tuple[int, int], goal: Tuple[int, int], grid: np.ndarray)
    def find_path(self) -> Optional[List[Tuple[int, int]]]
```

#### Convenience Function
```python
def find_shortest_path(start: Tuple[int, int], goal: Tuple[int, int], grid: np.ndarray) -> Optional[List[Tuple[int, int]]]
```

**Parameters:**
- `start`: Starting position as (row, col) coordinates
- `goal`: Target position as (row, col) coordinates  
- `grid`: Binary numpy array where 0 = passable, non-zero = obstacle

**Returns:**
- List of (row, col) coordinates representing the path, or None if no path exists

### Door Class Updates (`entities/doors.py`)

#### New Methods
```python
def find_closest_bin(self, bins: List, map_grid: np.ndarray) -> Optional[core.Entity]:
    """Find the closest bin using A* pathfinding algorithm"""

def get_path_to_bin(self) -> Optional[List[Tuple[int, int]]]:
    """Get the path to the assigned bin"""
```

#### New Attributes
- `assigned_bin`: Number of the assigned bin (or None)
- `path_to_bin`: List of coordinates forming the path to the assigned bin

### World Class Updates (`world/world.py`)

#### Updated Methods
```python
def find_paths(self):
    """Find paths from each door to its closest bin using A* algorithm"""
```

The method now uses the black/white image (`self.bw_img`) for pathfinding instead of the color image.

## Usage Examples

### Basic Usage

```python
from world.world import World

# Create world from image
world = World("My World", "path/to/image.jpg")

# Find optimal paths
world.find_paths()

# Access results
for door in world.doors:
    if door.assigned_bin is not None:
        path = door.get_path_to_bin()
        print(f"Door {door.number} -> Bin {door.assigned_bin}")
        print(f"Path length: {len(path)} steps")
```

### Direct A* Usage

```python
from tools.astar import find_shortest_path
import numpy as np

# Create a simple grid (0 = passable, 1 = obstacle)
grid = np.array([
    [0, 0, 0, 1, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0]
])

# Find path from (0,0) to (2,4)
path = find_shortest_path((0, 0), (2, 4), grid)
if path:
    print(f"Path found: {path}")
else:
    print("No path exists")
```

### Custom Door/Bin Assignment

```python
from entities.doors import Door
from entities.bins import Bin
import numpy as np

# Create entities
door = Door(1, 0, 0)
bins = [Bin(1, 5, 5), Bin(2, 10, 10)]

# Create map (black/white image data)
map_grid = np.zeros((20, 20), dtype=np.uint8)
# Add obstacles...

# Find closest bin
closest_bin = door.find_closest_bin(bins, map_grid)
if closest_bin:
    path = door.get_path_to_bin()
    print(f"Assigned to bin {closest_bin.number}")
    print(f"Path: {path}")
```

## Algorithm Details

### Heuristic Function
The implementation uses Manhattan distance as the heuristic:
```python
h(n) = |n.x - goal.x| + |n.y - goal.y|
```

This is admissible for 4-directional movement (up, down, left, right).

### Movement
- **4-directional**: The algorithm allows movement in 4 directions (up, down, left, right)
- **Cost**: Each step has a uniform cost of 1
- **Obstacles**: Cells with non-zero values are treated as impassable

### Data Structures
- **Open Set**: Priority queue (heapq) for nodes to be evaluated
- **Closed Set**: Set of nodes already evaluated
- **g_score**: Cost from start to each node
- **f_score**: g_score + heuristic (priority for open set)
- **came_from**: Parent pointers for path reconstruction

## Testing

Run the test suite to verify the implementation:

```bash
# Basic algorithm tests
python test/test_astar.py

# Integration tests  
python test/test_integration.py

# Advanced scenario tests
python test/test_advanced_astar.py

# Usage examples
python test/test_world_example.py
```

## Performance

The A* implementation is optimized for typical pathfinding scenarios:

- **Time Complexity**: O(b^d) where b is branching factor and d is depth
- **Space Complexity**: O(b^d) for storing the open/closed sets
- **Typical Performance**: Finds paths in grids up to 20x20 in milliseconds

Example performance (from tests):
- 20x20 grid with 59 obstacles: ~0.001 seconds
- Complex 15x15 maze: ~0.002 seconds per path

## Error Handling

The implementation handles various edge cases:

- **Blocked Start/Goal**: Returns None if start or goal positions are obstacles
- **No Path Exists**: Returns None if no valid path can be found
- **Empty Bin List**: Door.find_closest_bin returns None gracefully
- **Invalid Coordinates**: Bounds checking prevents array access errors

## Integration Notes

1. **Coordinate System**: Uses (row, col) format matching numpy array indexing
2. **Image Data**: Expects binary images where 0=passable, non-zero=obstacle
3. **Entity Positions**: Door/Bin (x, y) coordinates are converted to (y, x) for array indexing
4. **Path Format**: Returned paths are lists of (row, col) tuples from start to goal

## Future Enhancements

Potential improvements for the implementation:

1. **Diagonal Movement**: Support 8-directional movement with appropriate cost adjustments
2. **Weighted Terrain**: Support different movement costs for different terrain types
3. **Dynamic Obstacles**: Update paths when obstacles change
4. **Multi-Goal Search**: Find paths to multiple goals simultaneously
5. **Path Smoothing**: Post-process paths to reduce unnecessary turns
