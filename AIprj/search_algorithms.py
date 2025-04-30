from typing import List, Tuple, Dict, Set, Optional, Callable
import numpy as np
import heapq
from collections import deque


class SearchAlgorithms:
    def __init__(self, maze: np.ndarray):
        """
        Initialize the search algorithms with the maze.
        
        Args:
            maze: 2D numpy array representing the maze (0: path, 1: wall)
        """
        self.maze = maze
        self.height, self.width = maze.shape
        
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  algorithm: str) -> List[Tuple[int, int]]:
        """
        Find a path from start to goal using the specified algorithm.
        
        Args:
            start: (x, y) tuple representing the start position
            goal: (x, y) tuple representing the goal position
            algorithm: String specifying the algorithm to use ('BFS', 'DFS', or 'UCS')
            
        Returns:
            List of (x, y) tuples representing the path from start to goal
        """
        if algorithm == 'BFS':
            return self._bfs(start, goal)
        elif algorithm == 'DFS':
            return self._dfs(start, goal)
        elif algorithm == 'UCS':
            return self._ucs(start, goal)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def _get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Get valid neighboring positions from the current position.
        
        Args:
            x: Current x position
            y: Current y position
            
        Returns:
            List of (x, y) tuples representing valid neighbors
        """
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.width and 0 <= ny < self.height and 
                    self.maze[ny, nx] == 0):  # Check if it's a valid path
                neighbors.append((nx, ny))
                
        return neighbors
    
    def _reconstruct_path(self, came_from: Dict[Tuple[int, int], Tuple[int, int]], 
                         start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Reconstruct the path from start to goal using the came_from dictionary.
        
        Args:
            came_from: Dictionary mapping each position to the position it came from
            start: The starting position
            goal: The goal position
            
        Returns:
            List of positions from start to goal
        """
        current = goal
        path = [current]
        
        while current != start:
            if current not in came_from:
                # No path found
                return []
            current = came_from[current]
            path.append(current)
            
        return path[::-1]  # Reverse to get path from start to goal
    
    def _bfs(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Find a path using Breadth-First Search.
        
        Args:
            start: Starting position
            goal: Goal position
            
        Returns:
            List of positions from start to goal
        """
        queue = deque([start])
        visited = {start}
        came_from = {}
        
        while queue:
            current = queue.popleft()
            
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)
            
            for neighbor in self._get_neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    came_from[neighbor] = current
                    
        return []  # No path found
    
    def _dfs(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Find a path using Depth-First Search.
        
        Args:
            start: Starting position
            goal: Goal position
            
        Returns:
            List of positions from start to goal
        """
        stack = [start]
        visited = {start}
        came_from = {}
        
        while stack:
            current = stack.pop()
            
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)
            
            for neighbor in self._get_neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
                    came_from[neighbor] = current
                    
        return []  # No path found
    
    def _ucs(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Find a path using Uniform Cost Search.
        
        Args:
            start: Starting position
            goal: Goal position
            
        Returns:
            List of positions from start to goal
        """
        # Priority queue: (cost, position)
        priority_queue = [(0, start)]
        visited = set()
        came_from = {}
        cost_so_far = {start: 0}
        
        while priority_queue:
            current_cost, current = heapq.heappop(priority_queue)
            
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)
            
            if current in visited:
                continue
                
            visited.add(current)
            
            for neighbor in self._get_neighbors(*current):
                # In a grid, the cost of moving one step is 1
                new_cost = current_cost + 1
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    heapq.heappush(priority_queue, (new_cost, neighbor))
                    came_from[neighbor] = current
                    
        return []  # No path found