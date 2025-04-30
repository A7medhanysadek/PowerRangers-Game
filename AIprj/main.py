import pygame
import numpy as np
import time
import sys
import os
from maze_generator import MazeGenerator  
from search_algorithms import SearchAlgorithms  
from ui import UI  


class RangersMazeGame:
    def __init__(self, maze_width: int = 30, maze_height: int = 25, cell_size: int = 25, num_rangers: int = 4):
       
        pygame.init()
        pygame.font.init()
        
        self.num_rangers = max(2, min(5, num_rangers))
    
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.cell_size = cell_size
        
        self.maze_pixel_width = maze_width * cell_size
        self.maze_pixel_height = maze_height * cell_size
        self.control_height = 200  
        self.window_width = self.maze_pixel_width
        self.window_height = self.maze_pixel_height + self.control_height
  
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Power Rangers Maze Assemble")
        
        # Initialize fonts
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.large_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.medium_font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (128, 0, 128)
        self.PINK = (255, 192, 203)
        self.CYAN = (0, 255, 255)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (211, 211, 211)
        self.DARK_BLUE = (0, 0, 128)
        
        
        self.maze_generator = MazeGenerator(maze_width, maze_height)
        self.ui = UI(maze_width, maze_height, cell_size)
        
        
        self.maze = None
        self.search_algorithms = None
        self.ranger_positions = []
        self.meeting_point = None
        self.paths = []
        self.selected_algorithm = None
        self.assembled = False
        self.game_state = "menu"  
        
        button_width = 200
        button_height = 50
        button_margin = 30
       
        menu_start_y = self.window_height // 2
        self.menu_buttons = {
            'start': pygame.Rect((self.window_width - button_width) // 2, 
                                menu_start_y, 
                                button_width, button_height),
            'quit': pygame.Rect((self.window_width - button_width) // 2, 
                               menu_start_y + button_height + button_margin, 
                               button_width, button_height)
        }
      
        self.game_buttons = {
            'BFS': pygame.Rect(button_margin, 
                              self.maze_pixel_height + 30, 
                              button_width//2, button_height),
            'DFS': pygame.Rect(2*button_margin + button_width//2, 
                              self.maze_pixel_height + 30, 
                              button_width//2, button_height),
            'UCS': pygame.Rect(3*button_margin + button_width, 
                              self.maze_pixel_height + 30, 
                              button_width//2, button_height),
            'reset': pygame.Rect(self.window_width - button_width//2 - button_margin, 
                                self.maze_pixel_height + 30, 
                                button_width//2, button_height)
        }
        
        # Try to load logo
        self.logo = None
        if os.path.exists("assets/logo.png"):
            try:
                self.logo = pygame.image.load("assets/logo.png")
                max_logo_width = self.window_width * 0.8
                max_logo_height = self.window_height * 0.4
                logo_width, logo_height = self.logo.get_size()
                scale = min(max_logo_width / logo_width, max_logo_height / logo_height)
                new_width = int(logo_width * scale)
                new_height = int(logo_height * scale)
                self.logo = pygame.transform.scale(self.logo, (new_width, new_height))
            except pygame.error:
                print("Warning: Could not load logo image. Continuing without logo.")
        
       
        self.success_sound = None
        self.background_music = None
        try:
            pygame.mixer.init()
            if os.path.exists("assets/success.wav"):
                self.success_sound = pygame.mixer.Sound("assets/success.wav")
            
            
            if os.path.exists("theme.mp3"):
                pygame.mixer.music.load("theme.mp3")
                pygame.mixer.music.set_volume(0.5)  
                pygame.mixer.music.play(-1) 
        except:
            print("Warning: Could not load sound effects. Game will continue without sounds.")
        
        # Initialize clock
        self.clock = pygame.time.Clock()
    
    def generate_maze(self):
        self.maze = self.maze_generator.generate_maze()
        self._create_multiple_solution_paths()
        
        self.search_algorithms = SearchAlgorithms(self.maze)
        self.ranger_positions = self.maze_generator.get_random_positions(self.num_rangers)
        self.meeting_point = self._find_distant_meeting_point()
        self.paths = [[] for _ in range(self.num_rangers)]
        self.assembled = False
        self.selected_algorithm = None
        
    def _create_multiple_solution_paths(self):
        """Create multiple solution paths by strategically removing walls."""
        height, width = self.maze.shape
       
        num_additional_paths = (width * height) // 40
      
        candidate_walls = []
        for y in range(1, height-1):
            for x in range(1, width-1):
                
                if self.maze[y, x] == 1:
                    adjacent_paths = 0
                    adjacent_walls = 0
                    
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            if self.maze[ny, nx] == 0:
                                adjacent_paths += 1
                            else:
                                adjacent_walls += 1

                    if adjacent_paths >= 2 and adjacent_walls >= 1:
                        candidate_walls.append((x, y))

        import random
        random.shuffle(candidate_walls)
        num_walls_to_remove = min(len(candidate_walls), num_additional_paths)
        
        for i in range(num_walls_to_remove):
            x, y = candidate_walls[i]
            self.maze[y, x] = 0 
            
    def _find_distant_meeting_point(self):
        height, width = self.maze.shape
        path_positions = [(x, y) for y in range(height) for x in range(width) 
                         if self.maze[y, x] == 0]
       
        avg_x = sum(pos[0] for pos in self.ranger_positions) / len(self.ranger_positions)
        avg_y = sum(pos[1] for pos in self.ranger_positions) / len(self.ranger_positions)
       
        min_distance = width + height  
        meeting_point = self.maze_generator.find_optimal_meeting_point(self.ranger_positions)
        
        import random
     
        sample_size = min(len(path_positions), 100)
        sampled_positions = random.sample(path_positions, sample_size)
        
        for pos in sampled_positions:
            
            distance = ((pos[0] - avg_x) ** 2 + (pos[1] - avg_y) ** 2) ** 0.5
           
            all_reachable = True
            for ranger_pos in self.ranger_positions:
                temp_search = SearchAlgorithms(self.maze)
                path = temp_search.find_path(ranger_pos, pos, 'BFS')
                if not path:
                    all_reachable = False
                    break
            
            if all_reachable and distance > min_distance:
                min_distance = distance
                meeting_point = pos
        
        return meeting_point
    
    def calculate_paths(self, algorithm: str):
       
        self.selected_algorithm = algorithm
        self.paths = []
        
     
        for i, pos in enumerate(self.ranger_positions):
            path = self.search_algorithms.find_path(pos, self.meeting_point, algorithm)
            self.paths.append(path)
        
        self._calculate_path_statistics()
    
    def animate_paths(self):
     
        max_length = max(len(path) for path in self.paths)
        current_positions = self.ranger_positions.copy()
      
        for step in range(1, max_length):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            # Update positions for each ranger that still has steps left
            for i, path in enumerate(self.paths):
                if step < len(path):
                    current_positions[i] = path[step]
            
            # Draw current state
            self.ui.draw_maze(self.maze, current_positions, self.meeting_point, self.paths)
            self.draw_control_panel()
            pygame.display.flip()
            
            # Short delay for animation
            time.sleep(0.1)
        
        # Check if all rangers reached the meeting point
        self.assembled = all(pos == self.meeting_point for pos in current_positions)
        
        # Show success message if all rangers assembled
        if self.assembled:
            self.game_state = "success"
            self.ui.draw_maze(self.maze, current_positions, self.meeting_point, self.paths)
            self.draw_success_message()
            pygame.display.flip()
            
            # Play success sound if available
            if self.success_sound:
                self.success_sound.play()
            
            time.sleep(3)  # Show success message for 3 seconds
            self.game_state = "game"
    
    def draw_menu(self):
        """Draw the start menu."""
        # Fill background
        self.screen.fill(self.DARK_BLUE)
        
        # Draw logo if available
        if self.logo:
            logo_rect = self.logo.get_rect(center=(self.window_width // 2, self.window_height // 4))
            self.screen.blit(self.logo, logo_rect)
        else:
            # Draw text logo if image not available
            title_text = self.title_font.render("POWER RANGERS", True, self.YELLOW)
            subtitle_text = self.large_font.render("MAZE ASSEMBLE", True, self.RED)
            
            # Position the text
            title_rect = title_text.get_rect(center=(self.window_width // 2, self.window_height // 4 - 30))
            subtitle_rect = subtitle_text.get_rect(center=(self.window_width // 2, self.window_height // 4 + 30))
            
            # Draw with a shadow effect
            shadow_offset = 3
            shadow_title = self.title_font.render("POWER RANGERS", True, self.BLACK)
            shadow_subtitle = self.large_font.render("MAZE ASSEMBLE", True, self.BLACK)
            
            shadow_title_rect = shadow_title.get_rect(center=(self.window_width // 2 + shadow_offset, 
                                                            self.window_height // 4 - 30 + shadow_offset))
            shadow_subtitle_rect = shadow_subtitle.get_rect(center=(self.window_width // 2 + shadow_offset, 
                                                                  self.window_height // 4 + 30 + shadow_offset))
            
            self.screen.blit(shadow_title, shadow_title_rect)
            self.screen.blit(shadow_subtitle, shadow_subtitle_rect)
            self.screen.blit(title_text, title_rect)
            self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons
        for text, rect in self.menu_buttons.items():
            # Button background
            pygame.draw.rect(self.screen, self.RED, rect, border_radius=10)
            pygame.draw.rect(self.screen, self.BLACK, rect, 2, border_radius=10)  # Border
            
            # Button text
            button_text = self.medium_font.render(text.upper(), True, self.WHITE)
            text_rect = button_text.get_rect(center=rect.center)
            self.screen.blit(button_text, text_rect)
        
        # Draw footer
        version_text = self.small_font.render("v1.0", True, self.WHITE)
        version_rect = version_text.get_rect(bottomright=(self.window_width - 10, self.window_height - 10))
        self.screen.blit(version_text, version_rect)
    
    def _calculate_path_statistics(self):
        """Calculate and store statistics about the calculated paths."""
        self.path_stats = {
            'total_length': 0,
            'avg_length': 0,
            'max_length': 0,
            'min_length': float('inf')
        }
        
        total_length = 0
        path_lengths = []
        
        for path in self.paths:
            if path:
                path_len = len(path)
                path_lengths.append(path_len)
                total_length += path_len
                self.path_stats['max_length'] = max(self.path_stats['max_length'], path_len)
                self.path_stats['min_length'] = min(self.path_stats['min_length'], path_len)
        
        if path_lengths:
            self.path_stats['total_length'] = total_length
            self.path_stats['avg_length'] = total_length / len(path_lengths)
        else:
            self.path_stats['min_length'] = 0
    
    def draw_control_panel(self):
        """Draw the control panel with algorithm buttons."""
        # Draw background for control panel
        control_panel_rect = pygame.Rect(0, self.maze_pixel_height, self.window_width, self.control_height)
        pygame.draw.rect(self.screen, self.GRAY, control_panel_rect)
        
        # Draw title
        title_text = self.medium_font.render("Rangers Maze Assemble", True, self.WHITE)
        title_rect = title_text.get_rect(centerx=self.window_width // 2, top=self.maze_pixel_height + 5)
        self.screen.blit(title_text, title_rect)
        
       
        for algo, rect in self.game_buttons.items():
            
            if algo == 'reset':
                color = self.ORANGE
            else:
                color = self.GREEN if algo == self.selected_algorithm else self.LIGHT_GRAY
            
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, self.BLACK, rect, 2, border_radius=5)  # Button border
            
           
            text = self.medium_font.render(algo, True, self.BLACK)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
    
    def draw_success_message(self):
       
        overlay = pygame.Surface((self.window_width, self.maze_pixel_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  
        self.screen.blit(overlay, (0, 0))
    
        text = self.title_font.render("Rangers Assemble!", True, self.YELLOW)
        text_rect = text.get_rect(center=(self.window_width // 2, self.maze_pixel_height // 2))
        
        shadow_offset = 3
        shadow_text = self.title_font.render("Rangers Assemble!", True, self.RED)
        shadow_rect = shadow_text.get_rect(center=(self.window_width // 2 + shadow_offset, 
                                                  self.maze_pixel_height // 2 + shadow_offset))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(text, text_rect)
    
    def check_menu_click(self, pos):
       
        for text, rect in self.menu_buttons.items():
            if rect.collidepoint(pos):
                return text
        return None
    
    def check_game_click(self, pos):
       
        for text, rect in self.game_buttons.items():
            if rect.collidepoint(pos):
                return text
        return None
    
    def run(self):
        
        running = True
        
        while running:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state == "game":
                            self.game_state = "menu"
                        else:
                            running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == "menu":
                        
                        button = self.check_menu_click(event.pos)
                        if button == "start":
                            self.game_state = "game"
                            self.generate_maze()
                        elif button == "quit":
                            running = False
                    elif self.game_state == "game":
                        
                        button = self.check_game_click(event.pos)
                        if button in ["BFS", "DFS", "UCS"]:
                            self.calculate_paths(button)
                            self.animate_paths()
                        elif button == "reset":
                            self.generate_maze()
            
           
            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "game":
                self.ui.draw_maze(self.maze, self.ranger_positions, self.meeting_point, 
                                 None if self.selected_algorithm is None else self.paths)
                self.draw_control_panel()
            elif self.game_state == "success":
                self.ui.draw_maze(self.maze, self.ranger_positions, self.meeting_point, self.paths)
                self.draw_success_message()
                self.draw_control_panel()
            
            pygame.display.flip()
            self.clock.tick(30)  #
        
        pygame.quit()


def main():
    maze_width = 30
    maze_height = 25
    cell_size = 20
    num_rangers = 5
    
    if len(sys.argv) > 1:
        try:
            maze_width = int(sys.argv[1])
            if len(sys.argv) > 2:
                maze_height = int(sys.argv[2])
            if len(sys.argv) > 3:
                cell_size = int(sys.argv[3])
            if len(sys.argv) > 4:
                num_rangers = int(sys.argv[4])
        except ValueError:
            print("Invalid arguments. Using default settings.")
   
    game = RangersMazeGame(maze_width, maze_height, cell_size, num_rangers)
    game.run()


if __name__ == "__main__":
    main()