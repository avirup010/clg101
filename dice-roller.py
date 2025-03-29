import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (240, 242, 245)  # Softer gray-blue background
ACCENT_COLOR = (88, 101, 242)  # Vibrant indigo
ACCENT_HOVER = (108, 121, 255)  # Lighter hover state
DIE_BG = (245, 247, 250)  # Off-white die background
SHADOW = (0, 0, 0, 40)  # Subtle shadow

# Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dice Roller")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 26, bold=True)
small_font = pygame.font.SysFont('Arial', 20)

# Dice settings
dice_types = ["d4", "d6", "d8", "d10", "d12", "d20"]
selected_dice = "d6"
num_dice = 1
dice_values = []
rolling = False
roll_animation = 0

class Die:
    def __init__(self, x, y, value, die_type):
        self.x = x
        self.y = y
        self.value = value
        self.type = die_type
        self.rotation = 0
        self.scale = 1.0
        self.target_value = value

def draw_rounded_rect(surface, rect, color, radius=15, gradient=False):
    if gradient and isinstance(color, tuple) and len(color) == 2:
        # Simple vertical gradient
        for i in range(rect.height):
            alpha = i / rect.height
            current_color = tuple(int(c1 + (c2 - c1) * alpha) for c1, c2 in zip(color[0], color[1]))
            pygame.draw.line(surface, current_color, (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))
    else:
        pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_button(surface, rect, text, base_color, hover_color, gradient=False):
    mouse_pos = pygame.mouse.get_pos()
    color = hover_color if rect.collidepoint(mouse_pos) else base_color
    
    if gradient:
        draw_rounded_rect(surface, rect, (base_color, hover_color), radius=15, gradient=True)
    else:
        draw_rounded_rect(surface, rect, color, radius=15)
    
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    return rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]

def draw_die(die):
    size = int(90 * die.scale)  # Slightly larger dice
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, size, size)
    
    # Enhanced shadow
    shadow = pygame.Surface((size+8, size+8), pygame.SRCALPHA)
    pygame.draw.rect(shadow, SHADOW, (4, 4, size, size), border_radius=12)
    screen.blit(shadow, (die.x-4, die.y-4))
    
    # Die with subtle gradient
    draw_rounded_rect(surface, rect, (DIE_BG, (230, 232, 235)), 12, gradient=True)
    
    # Draw number with slight shadow
    text = font.render(str(die.value), True, BLACK)
    shadow_text = font.render(str(die.value), True, (0, 0, 0, 50))
    text_rect = text.get_rect(center=(size//2, size//2))
    surface.blit(shadow_text, (text_rect.x+1, text_rect.y+1))
    surface.blit(text, text_rect)
    
    # Rotate and blit
    rotated = pygame.transform.rotate(surface, die.rotation)
    final_rect = rotated.get_rect(center=(die.x + size//2, die.y + size//2))
    screen.blit(rotated, final_rect.topleft)

def update_dice_animation(dice):
    global rolling, roll_animation
    if not rolling:
        return
    
    roll_animation += 1
    dice_max = int(selected_dice[1:])
    
    for die in dice:
        if roll_animation < 30:
            die.value = random.randint(1, dice_max)
            die.rotation += random.randint(-15, 15)
            die.scale = 1.0 + abs(math.sin(roll_animation * 0.2)) * 0.2
        elif roll_animation < 40:
            die.value = die.target_value
            die.rotation *= 0.8
            die.scale = 1.0 + (40 - roll_animation) * 0.02
        else:
            die.rotation = 0
            die.scale = 1.0
            rolling = False
            roll_animation = 0

def adjust_dice_count(dice, target_count):
    current_count = len(dice)
    if current_count < target_count:
        start_x = (WIDTH - (target_count * 100)) // 2
        for i in range(current_count, target_count):
            dice.append(Die(start_x + i * 100, HEIGHT//2 - 45, 1, selected_dice))
    elif current_count > target_count:
        dice[target_count:] = []
    return dice

def main():
    global selected_dice, num_dice, dice_values, rolling
    
    dice = [Die(WIDTH//2-45, HEIGHT//2-45, 1, selected_dice)]
    button_cooldown = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Clear screen with soft background
        screen.fill(BG_COLOR)
        
        # Title with subtle shadow
        title = font.render("Dice Roller", True, BLACK)
        shadow_title = font.render("Dice Roller", True, (0, 0, 0, 30))
        screen.blit(shadow_title, (WIDTH//2 - title.get_width()//2 + 2, 52))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Adjust dice count
        dice = adjust_dice_count(dice, num_dice)
        
        # Draw dice
        total_width = num_dice * 100
        start_x = (WIDTH - total_width) // 2
        for i, die in enumerate(dice):
            die.x = start_x + i * 100
            die.y = HEIGHT//2 - 45
            draw_die(die)
        
        # Update animation
        update_dice_animation(dice)
        
        # Dice type selector with spacing
        for i, dtype in enumerate(dice_types):
            rect = pygame.Rect(20 + i*80, HEIGHT-150, 70, 45)
            if draw_button(screen, rect, dtype, ACCENT_COLOR, ACCENT_HOVER, gradient=True):
                selected_dice = dtype
                dice = [Die(0, 0, 1, selected_dice) for _ in range(num_dice)]
                dice_values = []
        
        # Number selector with modern styling
        num_text = small_font.render(f"Dice: {num_dice}", True, BLACK)
        screen.blit(num_text, (20, HEIGHT-80))
        
        minus = pygame.Rect(100, HEIGHT-90, 45, 45)
        plus = pygame.Rect(155, HEIGHT-90, 45, 45)
        
        if button_cooldown > 0:
            button_cooldown -= 1
            
        if draw_button(screen, minus, "-", ACCENT_COLOR, ACCENT_HOVER, gradient=True) and num_dice > 1 and button_cooldown == 0:
            num_dice -= 1
            dice_values = dice_values[:num_dice] if dice_values else []
            button_cooldown = 10
            
        if draw_button(screen, plus, "+", ACCENT_COLOR, ACCENT_HOVER, gradient=True) and num_dice < 5 and button_cooldown == 0:
            num_dice += 1
            dice_values = dice_values + [1] if dice_values else []
            button_cooldown = 10
        
        # Roll button with larger size and gradient
        roll_rect = pygame.Rect(WIDTH//2-110, HEIGHT-100, 220, 60)
        if draw_button(screen, roll_rect, "ROLL", ACCENT_COLOR, ACCENT_HOVER, gradient=True) and not rolling:
            rolling = True
            dice_max = int(selected_dice[1:])
            dice_values = [random.randint(1, dice_max) for _ in range(num_dice)]
            for i, die in enumerate(dice):
                die.target_value = dice_values[i]
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
