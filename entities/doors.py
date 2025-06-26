from . import core
import numpy as np
from typing import Tuple, List, Optional
from tools.astar import find_shortest_path

class Door(core.Entity):
    def __init__(self, number: int, x: int, y: int):
        super().__init__(number, x, y, type="door")

        self.assigned_bin = None  # Initially, no bin is assigned to this door
        self.path_to_bin = None  # Path to the bin


    def assign_bin(self, bin_entity: core.Entity):
        if bin_entity.type != "bin":
            raise ValueError("Assigned entity must be a bin.")
        
        self.assigned_bin = bin_entity.number

    def find_closest_bin(self, bins: List, map_grid: np.ndarray) -> Optional[core.Entity]:
        """Find the closest bin using A* pathfinding algorithm"""
        if not bins:
            print(f"No bins available to find closest bin for door {self.number}.")
            return None
        
        closest_bin = None
        shortest_path = None
        shortest_distance = float('inf')
        
        # Convert door position to grid coordinates
        door_pos = (self.y, self.x)  # Note: numpy arrays are (row, col) = (y, x)
        
        for bin_entity in bins:
            # Convert bin position to grid coordinates
            bin_pos = (bin_entity.y, bin_entity.x)
            
            # Find path using A* algorithm
            path = find_shortest_path(door_pos, bin_pos, map_grid)
            
            if path is not None:
                path_length = len(path)
                if path_length < shortest_distance:
                    shortest_distance = path_length
                    shortest_path = path
                    closest_bin = bin_entity
        
        if closest_bin is not None:
            self.assigned_bin = closest_bin.number
            self.path_to_bin = shortest_path
            print(f"Door {self.number} assigned to bin {closest_bin.number} with path length {shortest_distance}")
            return closest_bin
        else:
            print(f"No accessible path found from door {self.number} to any bin.")
            return None
    
    def get_path_to_bin(self) -> Optional[List[Tuple[int, int]]]:
        """Get the path to the assigned bin"""
        return self.path_to_bin
            