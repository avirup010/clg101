'''
This is a minimalist Snake game built with Pygame, featuring a resizable window, smooth animations, a dark/light mode toggle, speed adjustment, a pause function, and a help menu. The game starts with a welcome screen and allows the player to control the snake using the arrow keys, with food spawning randomly on the grid. The snake wraps around screen edges, grows upon eating food, and the game ends if it collides with itself.

Requirements to Run the Game
To run this game, you need to install Python and Pygame.

Installation Steps:
Install Python (if not already installed) – Download Python
Install Pygame using pip:
sh
Copy
Edit
pip install pygame
Run the game script:
sh
Copy
Edit
python snake_game.py
'''




import pygame
import random
import sys
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Get the display info
display_info = pygame.display.Info()
INITIAL_WIDTH = min(1280, display_info.current_w - 100)  # Start with reasonable default size
INITIAL_HEIGHT = min(720, display_info.current_h - 100)

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hovered = False
        
    def draw(self, screen, theme):
        color = theme['button_hover'] if self.hovered else theme['button']
        pygame.draw.rect(screen, color, self.rect, border_radius=self.rect.height // 2)
        
        text_surface = self.font.render(self.text, True, theme['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            return True
        return False

class Snake:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.reset()
        
    def reset(self):
        self.positions = [(self.grid_width // 2, self.grid_height // 2)]
        self.direction = (1, 0)
        self.grow = False
        
    def update(self):
        head = self.positions[0]
        new_head = (
            (head[0] + self.direction[0]) % self.grid_width,
            (head[1] + self.direction[1]) % self.grid_height
        )
        
        if new_head in self.positions:
            return False
            
        self.positions.insert(0, new_head)
        if not self.grow:
            self.positions.pop()
        self.grow = False
        return True
        
    def draw(self, screen, grid_size, color):
        for pos in self.positions:
            x = pos[0] * grid_size + grid_size // 2
            y = pos[1] * grid_size + grid_size // 2
            radius = grid_size // 2 - 2
            gfxdraw.aacircle(screen, x, y, radius, color)
            gfxdraw.filled_circle(screen, x, y, radius, color)

class Game:
    def __init__(self):
        # Create resizable window
        self.screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Minimal Snake")
        
        self.update_dimensions()
        self.clock = pygame.time.Clock()
        self.snake = Snake(self.grid_width, self.grid_height)
        self.food = self.generate_food()
        self.score = 0
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.dark_mode = True
        self.theme = {
            'background': (18, 18, 18),
            'grid': (30, 30, 30),
            'snake': (240, 240, 240),
            'food': (86, 182, 194),
            'text': (200, 200, 200),
            'overlay': (18, 18, 18, 180),
            'button': (40, 40, 40),
            'button_hover': (60, 60, 60)
        }
        self.speed = 10
        
        self.show_welcome = True
        self.show_help = False
        self.paused = False
        self.help_button = None
        self.update_button()
    
    def update_dimensions(self):
        self.width, self.height = self.screen.get_size()
        self.grid_size = min(max(20, min(self.width, self.height) // 40), 40)
        self.grid_width = self.width // self.grid_size
        self.grid_height = self.height // self.grid_size
    
    def update_button(self):
        button_width = 60
        button_height = 30
        self.help_button = Button(10, 10, button_width, button_height, "Help", self.small_font)
    
    def generate_food(self):
        while True:
            food = (
                random.randrange(self.grid_width),
                random.randrange(self.grid_height)
            )
            if food not in self.snake.positions:
                return food

    def draw_overlay_text(self, title, instructions):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, self.theme['overlay'], overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        
        title_surface = self.font.render(title, True, self.theme['text'])
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title_surface, title_rect)
        
        y = self.height // 3
        for line in instructions:
            text_surface = self.small_font.render(line, True, self.theme['text'])
            text_rect = text_surface.get_rect(center=(self.width // 2, y))
            self.screen.blit(text_surface, text_rect)
            y += 40
            
        if self.show_welcome:
            continue_text = self.small_font.render("Press any key to start", True, self.theme['text'])
            continue_rect = continue_text.get_rect(center=(self.width // 2, y + 40))
            self.screen.blit(continue_text, continue_rect)
    
    def draw_grid(self):
        for i in range(self.grid_width + 1):
            pygame.draw.line(
                self.screen,
                self.theme['grid'],
                (i * self.grid_size, 0),
                (i * self.grid_size, self.height)
            )
        for i in range(self.grid_height + 1):
            pygame.draw.line(
                self.screen,
                self.theme['grid'],
                (0, i * self.grid_size),
                (self.width, i * self.grid_size)
            )
    
    def draw_food(self):
        x = self.food[0] * self.grid_size + self.grid_size // 2
        y = self.food[1] * self.grid_size + self.grid_size // 2
        radius = self.grid_size // 2 - 2
        gfxdraw.aacircle(self.screen, x, y, radius, self.theme['food'])
        gfxdraw.filled_circle(self.screen, x, y, radius, self.theme['food'])
    
    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, self.theme['text'])
        self.screen.blit(score_text, (80, 10))
        
        speed_text = self.font.render(f"Speed: {self.speed}", True, self.theme['text'])
        speed_rect = speed_text.get_rect(topright=(self.width - 10, 10))
        self.screen.blit(speed_text, speed_rect)
    
    def draw_footer(self):
        footer_text = self.small_font.render("developed by Avi", True, self.theme['text'])
        padding = 10
        text_rect = footer_text.get_rect()
        pill_rect = pygame.Rect(
            self.width - text_rect.width - padding * 3,
            self.height - text_rect.height - padding * 2,
            text_rect.width + padding * 2,
            text_rect.height + padding
        )
        pygame.draw.rect(
            self.screen,
            self.theme['grid'],
            pill_rect,
            border_radius=pill_rect.height // 2
        )
        text_pos = (
            self.width - text_rect.width - padding * 2,
            self.height - text_rect.height - padding * 1.5
        )
        self.screen.blit(footer_text, text_pos)
    
    def run(self):
        instructions = [
            "Controls:",
            "Arrow Keys - Move Snake",
            "+ / - Keys - Adjust Speed",
            "T Key - Toggle Dark/Light Mode",
            "ESC Key - Pause Game",
            "Help Button - Show Instructions"
        ]
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.update_dimensions()
                    self.update_button()
                    self.snake = Snake(self.grid_width, self.grid_height)
                    self.food = self.generate_food()
                
                if self.help_button.handle_event(event):
                    self.show_help = not self.show_help
                    self.paused = self.show_help
                
                if event.type == pygame.KEYDOWN:
                    if self.show_welcome:
                        self.show_welcome = False
                        continue
                        
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                        
                    if not self.paused and not self.show_help:
                        if event.key == pygame.K_UP and self.snake.direction != (0, 1):
                            self.snake.direction = (0, -1)
                        if event.key == pygame.K_DOWN and self.snake.direction != (0, -1):
                            self.snake.direction = (0, 1)
                        if event.key == pygame.K_LEFT and self.snake.direction != (1, 0):
                            self.snake.direction = (-1, 0)
                        if event.key == pygame.K_RIGHT and self.snake.direction != (-1, 0):
                            self.snake.direction = (1, 0)
                        
                        if event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                            self.speed = min(20, self.speed + 1)
                        if event.key == pygame.K_MINUS:
                            self.speed = max(5, self.speed - 1)
                        
                        if event.key == pygame.K_t:
                            self.dark_mode = not self.dark_mode
                            self.theme = {
                                'background': (240, 240, 240) if not self.dark_mode else (18, 18, 18),
                                'grid': (200, 200, 200) if not self.dark_mode else (30, 30, 30),
                                'snake': (18, 18, 18) if not self.dark_mode else (240, 240, 240),
                                'food': (86, 182, 194),
                                'text': (18, 18, 18) if not self.dark_mode else (200, 200, 200),
                                'overlay': (240, 240, 240, 180) if not self.dark_mode else (18, 18, 18, 180),
                                'button': (220, 220, 220) if not self.dark_mode else (40, 40, 40),
                                'button_hover': (200, 200, 200) if not self.dark_mode else (60, 60, 60)
                            }
            
            self.screen.fill(self.theme['background'])
            self.draw_grid()
            self.draw_food()
            self.snake.draw(self.screen, self.grid_size, self.theme['snake'])
            self.draw_score()
            self.draw_footer()
            self.help_button.draw(self.screen, self.theme)
            
            if not self.paused and not self.show_help and not self.show_welcome:
                if not self.snake.update():
                    pygame.quit()
                    sys.exit()
                
                if self.snake.positions[0] == self.food:
                    self.snake.grow = True
                    self.food = self.generate_food()
                    self.score += 1
            
            if self.show_welcome:
                self.draw_overlay_text("Welcome to Snake!", instructions)
            elif self.show_help:
                self.draw_overlay_text("Game Instructions", instructions)
            
            pygame.display.flip()
            self.clock.tick(self.speed)

if __name__ == "__main__":
    game = Game()
    game.run()
