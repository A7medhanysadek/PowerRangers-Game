import random
import numpy as np
from typing import List, Tuple, Dict, Set


class MazeGenerator:
    def __init__(self, width: int, height: int):
        """
        Initialize the maze generator with given dimensions.
        
        Args:
            width: Width of the maze
            height: Height of the maze
        """
        self.width = width
        self.height = height
        self.maze = np.ones((height, width), dtype=int)  # 1 represents walls
        
    def generate_maze(self) -> np.ndarray:
        """
        Generate a random maze using the Recursive Backtracking algorithm.
        
        Returns:
            2D numpy array representing the maze (0: path, 1: wall)
        """
        # Start with all walls
        self.maze = np.ones((self.height, self.width), dtype=int)
        
        # Ensure odd dimensions for proper maze generation
        start_x, start_y = 1, 1
        self.maze[start_y, start_x] = 0  # Starting cell
        self._recursive_backtrack(start_x, start_y)
        
        # Ensure the maze has a minimum number of paths
        path_count = np.count_nonzero(self.maze == 0)
        desired_path_percentage = 0.35  # Adjust for desired path density
        desired_paths = int(self.width * self.height * desired_path_percentage)
        
        if path_count < desired_paths:
            self._add_additional_paths(desired_paths - path_count)
            
        return self.maze
        
    def _recursive_backtrack(self, x: int, y: int) -> None:
        """
        Perform recursive backtracking to carve out maze paths.
        
        Args:
            x: Current x position
            y: Current y position
        """
        # Define possible directions: (dx, dy)
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            
            # Check if the new position is within bounds and is a wall
            if (0 < new_x < self.width-1 and 0 < new_y < self.height-1 and 
                    self.maze[new_y, new_x] == 1):
                
                # Carve a path by setting cells to 0
                self.maze[y + dy//2, x + dx//2] = 0  # Remove the wall between cells
                self.maze[new_y, new_x] = 0  # Mark the new cell as visited
                
                # Continue recursively
                self._recursive_backtrack(new_x, new_y)
                
    def _add_additional_paths(self, num_paths: int) -> None:
        """
        Add additional paths to make the maze less dense.
        
        Args:
            num_paths: Number of additional paths to add
        """
        walls = [(x, y) for y in range(1, self.height-1) for x in range(1, self.width-1) 
                if self.maze[y, x] == 1 and self._has_adjacent_paths(x, y)]
        
        random.shuffle(walls)
        paths_added = 0
        
        for x, y in walls:
            if paths_added >= num_paths:
                break
                
            self.maze[y, x] = 0
            paths_added += 1
    
    def _has_adjacent_paths(self, x: int, y: int) -> bool:
        """
        Check if a wall has adjacent paths (for adding additional paths).
        
        Args:
            x: Wall x position
            y: Wall y position
            
        Returns:
            True if the wall has adjacent paths, False otherwise
        """
        adjacent_cells = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        path_count = 0
        
        for ax, ay in adjacent_cells:
            if (0 <= ax < self.width and 0 <= ay < self.height and 
                    self.maze[ay, ax] == 0):
                path_count += 1
                
        return path_count >= 2
        
    def get_random_positions(self, num_positions: int) -> List[Tuple[int, int]]:
        """
        Get random valid (path) positions in the maze.
        
        Args:
            num_positions: Number of positions to generate
            
        Returns:
            List of (x, y) tuples representing positions
        """
        path_positions = [(x, y) for y in range(self.height) for x in range(self.width) 
                         if self.maze[y, x] == 0]
        
        if len(path_positions) < num_positions:
            raise ValueError(f"Not enough paths in maze to place {num_positions} characters")
            
        return random.sample(path_positions, num_positions)
    
    def find_optimal_meeting_point(self, positions: List[Tuple[int, int]]) -> Tuple[int, int]:
        """
        Find the optimal meeting point that minimizes total distance from all positions.
        Uses a simplified approach based on the median of positions.
        
        Args:
            positions: List of starting positions for each character
            
        Returns:
            (x, y) tuple representing the optimal meeting point
        """
        # For simplicity, we'll use a grid search approach
        all_path_positions = [(x, y) for y in range(self.height) for x in range(self.width) 
                            if self.maze[y, x] == 0]
        
        min_total_distance = float('inf')
        optimal_point = all_path_positions[0]
        
        for point in all_path_positions:
            # Calculate total Manhattan distance from this point to all positions
            total_distance = sum(abs(point[0] - pos[0]) + abs(point[1] - pos[1]) 
                                for pos in positions)
            
            if total_distance < min_total_distance:
                min_total_distance = total_distance
                optimal_point = point
                
        return optimal_point