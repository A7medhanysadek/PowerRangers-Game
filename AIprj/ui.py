import pygame
from typing import List, Tuple, Dict, Optional, Callable
import numpy as np


class UI:
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    PINK = (255, 192, 203)
    CYAN = (0, 255, 255)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (211, 211, 211)
    
    # Ranger colors corresponding to emojis
    RANGER_COLORS = [
        (255, 0, 0),    # Red
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (255, 0, 255),  # Pink/Purple
    ]
    
    # Ranger emojis
    RANGER_EMOJIS = ["🔴", "🔵", "🟡", "🟢", "🟣"]
    
    def __init__(self, width: int, height: int, cell_size: int):
        """
        Initialize the UI with given dimensions.
        
        Args:
            width: Width of the maze in cells
            height: Height of the maze in cells
            cell_size: Size of each maze cell in pixels
        """
        self.maze_width = width
        self.maze_height = height
        self.cell_size = cell_size
        
        # Calculate actual window dimensions
        self.maze_pixel_width = width * cell_size
        self.maze_pixel_height = height * cell_size
        
        # Add space for buttons and status information
        self.control_height = 150
        self.window_width = self.maze_pixel_width
        self.window_height = self.maze_pixel_height + self.control_height
        
        # Initialize pygame
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Setup display
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Power Rangers Maze Assemble")
        
        # Button dimensions and positions
        button_width = 100
        button_height = 40
        button_margin = 20
        self.buttons = {
            'BFS': pygame.Rect(button_margin, self.maze_pixel_height + 30, button_width, button_height),
            'DFS': pygame.Rect(2*button_margin + button_width, self.maze_pixel_height + 30, button_width, button_height),
            'UCS': pygame.Rect(3*button_margin + 2*button_width, self.maze_pixel_height + 30, button_width, button_height)
        }
        
        # Load sound effects (optional)
        try:
            pygame.mixer.init()
            self.success_sound = pygame.mixer.Sound("assets/success.wav")
        except:
            self.success_sound = None
            print("Warning: Could not load sound effects. Game will continue without sounds.")
            
        # Initialize clock
        self.clock = pygame.time.Clock()
        
    def draw_maze(self, maze: np.ndarray, 
                 ranger_positions: List[Tuple[int, int]], 
                 meeting_point: Optional[Tuple[int, int]] = None,
                 paths: Optional[List[List[Tuple[int, int]]]] = None) -> None:
        """
        Draw the maze with rangers and paths.
        
        Args:
            maze: 2D numpy array representing the maze
            ranger_positions: List of (x, y) positions for each ranger
            meeting_point: Optional (x, y) position for the meeting point
            paths: Optional list of paths for each ranger
        """
        # Fill the background
        self.screen.fill(self.LIGHT_GRAY)
        
        # Draw maze
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                if maze[y, x] == 1:  # Wall
                    pygame.draw.rect(self.screen, self.BLACK, rect)
                else:  # Path
                    pygame.draw.rect(self.screen, self.WHITE, rect)
        
        # Draw paths if available
        if paths:
            for i, path in enumerate(paths):
                if path:
                    # Draw path with ranger color (semi-transparent)
                    color = self.RANGER_COLORS[i]
                    alpha_color = (*color, 100)  # Add alpha for transparency
                    
                    for x, y in path:
                        rect = pygame.Rect(
                            x * self.cell_size + self.cell_size // 4,
                            y * self.cell_size + self.cell_size // 4,
                            self.cell_size // 2,
                            self.cell_size // 2
                        )
                        # Create a surface with per-pixel alpha
                        s = pygame.Surface((self.cell_size // 2, self.cell_size // 2), pygame.SRCALPHA)
                        s.fill(alpha_color)
                        self.screen.blit(s, rect)
        
        # Draw meeting point
        if meeting_point:
            x, y = meeting_point
            center_x = x * self.cell_size + self.cell_size // 2
            center_y = y * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 3
            pygame.draw.circle(self.screen, self.ORANGE, (center_x, center_y), radius)
            
            # Draw a star shape or target icon for the meeting point
            points = []
            for i in range(8):
                angle = 2 * 3.14159 * i / 8
                radius_multiplier = 0.8 if i % 2 == 0 else 0.4
                point_x = center_x + int(radius * radius_multiplier * 1.2 * np.cos(angle))
                point_y = center_y + int(radius * radius_multiplier * 1.2 * np.sin(angle))
                points.append((point_x, point_y))
            
            pygame.draw.polygon(self.screen, self.YELLOW, points)
        
        # Draw rangers
        font = pygame.font.SysFont('segoe ui emoji', self.cell_size)  # Font with emoji support
        for i, (x, y) in enumerate(ranger_positions):
            # Draw colored circle for ranger
            center_x = x * self.cell_size + self.cell_size // 2
            center_y = y * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 2 - 2
            
            # Draw emoji text
            text = font.render(self.RANGER_EMOJIS[i], True, self.BLACK)
            text_rect = text.get_rect(center=(center_x, center_y))
            self.screen.blit(text, text_rect)
            
    def draw_control_panel(self, selected_algorithm: Optional[str] = None) -> None:
        """
        Draw the control panel with algorithm buttons.
        
        Args:
            selected_algorithm: Currently selected algorithm
        """
        # Draw background for control panel
        control_panel_rect = pygame.Rect(0, self.maze_pixel_height, self.window_width, self.control_height)
        pygame.draw.rect(self.screen, self.GRAY, control_panel_rect)
        
        # Draw title
        title_text = self.font.render("Rangers Maze Assemble", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.window_width // 2, self.maze_pixel_height + 15))
        self.screen.blit(title_text, title_rect)
        
        # Draw algorithm buttons
        for algo, rect in self.buttons.items():
            color = self.GREEN if algo == selected_algorithm else self.LIGHT_GRAY
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, self.BLACK, rect, 2, border_radius=5)  # Button border
            
            # Button text
            text = self.font.render(algo, True, self.BLACK)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            
    def draw_success_message(self) -> None:
        """Draw the 'Rangers Assemble!' success message."""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.window_width, self.maze_pixel_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw the success message
        large_font = pygame.font.SysFont('Arial', 48, bold=True)
        text = large_font.render("Rangers Assemble!", True, self.YELLOW)
        text_rect = text.get_rect(center=(self.window_width // 2, self.maze_pixel_height // 2))
        
        # Create a text shadow effect
        shadow_offset = 3
        shadow_text = large_font.render("Rangers Assemble!", True, self.RED)
        shadow_rect = shadow_text.get_rect(center=(self.window_width // 2 + shadow_offset, 
                                                  self.maze_pixel_height // 2 + shadow_offset))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(text, text_rect)
        
        # Play success sound if available
        if self.success_sound:
            self.success_sound.play()
    
    def check_button_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """
        Check if a button was clicked.
        
        Args:
            pos: (x, y) position of the mouse click
            
        Returns:
            Button name if clicked, None otherwise
        """
        for algo, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return algo
        return None
        
    def display_algorithm_info(self, algorithm: str) -> None:
        """
        Display information about the selected algorithm.
        
        Args:
            algorithm: Selected algorithm name
        """
        info_text = ""
        if algorithm == "BFS":
            info_text = "BFS: Breadth-First Search - Explores all neighbors at current depth"
        elif algorithm == "DFS":
            info_text = "DFS: Depth-First Search - Explores as far as possible along each branch"
        elif algorithm == "UCS":
            info_text = "UCS: Uniform Cost Search - Considers path cost to find optimal path"
        
        text = self.small_font.render(info_text, True, self.WHITE)
        text_rect = text.get_rect(center=(self.window_width // 2, self.maze_pixel_height + 80))
        self.screen.blit(text, text_rect)
        
    def update_display(self) -> None:
        """Update the display."""
        pygame.display.flip()
        self.clock.tick(30)  # Limit to 30 frames per second