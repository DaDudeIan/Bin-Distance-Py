import heapq
import numpy as np
from typing import List, Tuple, Optional

class Astar:
    def __init__(self, start: Tuple[int, int], goal: Tuple[int, int], grid: np.ndarray):
        self.start = start
        self.goal = goal
        self.grid = grid  # Binary grid where 0 = passable, non-zero = obstacle
        self.rows, self.cols = grid.shape
        
        # A* data structures
        self.open_set = []  # Priority queue (heap)
        self.open_set_hash = set()  # For O(1) lookup
        self.closed_set = set()
        self.came_from = {}  # Parent nodes for path reconstruction
        self.g_score = {}  # Cost from start to node
        self.f_score = {}  # g_score + heuristic
        
        # Initialize start node
        self.g_score[start] = 0
        self.f_score[start] = self.heuristic(start, goal)
        heapq.heappush(self.open_set, (self.f_score[start], start))
        self.open_set_hash.add(start)
    
    def heuristic(self, node: Tuple[int, int], goal: Tuple[int, int]) -> float:
        i = 9
        if i == 0:
            """Manhattan distance heuristic"""
            return abs(node[0] - goal[0]) + abs(node[1] - goal[1])
        elif i == 1:
            """Diagonal distance heuristic"""
            dx = abs(node[0] - goal[0])
            dy = abs(node[1] - goal[1])
            return max(dx, dy) + (np.sqrt(2) - 1) * min(dx, dy)
        elif i == 2:
            """Chebyshev distance heuristic"""
            return max(abs(node[0] - goal[0]), abs(node[1] - goal[1]))
        else:
            """Euclidean distance heuristic"""
            return float(np.linalg.norm(np.array(node) - np.array(goal)))
    
    def get_neighbors(self, node: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring nodes (8-directional movement including diagonals)"""
        neighbors = []
        row, col = node
        
        # 8-directional movement (up, down, left, right, and diagonals)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),  # cardinal directions
                     (-1, -1), (-1, 1), (1, -1), (1, 1)]  # diagonal directions
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Check bounds
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                # Check if cell is passable (0 = passable, non-zero = obstacle)
                if self.grid[new_row, new_col] == 0:
                    neighbors.append((new_row, new_col))
        
        return neighbors
    
    def reconstruct_path(self) -> List[Tuple[int, int]]:
        """Reconstruct the path from start to goal"""
        path = []
        current = self.goal
        
        while current in self.came_from:
            path.append(current)
            current = self.came_from[current]
        
        path.append(self.start)
        path.reverse()
        return path
    
    def find_path(self) -> Optional[List[Tuple[int, int]]]:
        """Execute A* algorithm to find shortest path"""
        
        # Check if start or goal is blocked
        if self.grid[self.start[0], self.start[1]] != 0:
            print(f"Start position {self.start} is blocked")
            return None
        if self.grid[self.goal[0], self.goal[1]] != 0:
            print(f"Goal position {self.goal} is blocked")
            return None
        
        while self.open_set:
            # Get node with lowest f_score
            current_f, current = heapq.heappop(self.open_set)
            self.open_set_hash.remove(current)
            
            # Skip if we've already processed this node with a better score
            if current in self.closed_set:
                continue
            
            # Add to closed set
            self.closed_set.add(current)
            
            # Check if we reached the goal
            if current == self.goal:
                return self.reconstruct_path()
            
            # Explore neighbors
            for neighbor in self.get_neighbors(current):
                if neighbor in self.closed_set:
                    continue
                
                # Calculate movement cost (1 for cardinal, √2 for diagonal)
                dx = abs(neighbor[0] - current[0])
                dy = abs(neighbor[1] - current[1])
                movement_cost = np.sqrt(2) if (dx == 1 and dy == 1) else 1.0
                
                # Calculate tentative g_score
                tentative_g = self.g_score[current] + movement_cost
                
                # If this is a new node or we found a better path
                if neighbor not in self.g_score or tentative_g < self.g_score[neighbor]:
                    self.came_from[neighbor] = current
                    self.g_score[neighbor] = tentative_g
                    self.f_score[neighbor] = tentative_g + self.heuristic(neighbor, self.goal)
                    
                    # Add to open set if not already there
                    if neighbor not in self.open_set_hash:
                        heapq.heappush(self.open_set, (self.f_score[neighbor], neighbor))
                        self.open_set_hash.add(neighbor)
        
        # No path found
        return None

def find_shortest_path(start: Tuple[int, int], goal: Tuple[int, int], grid: np.ndarray) -> Optional[List[Tuple[int, int]]]:
    """Convenience function to find shortest path using A*"""
    astar = Astar(start, goal, grid)
    return astar.find_path()


