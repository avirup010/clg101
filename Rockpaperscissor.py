import pygame
import sys
import random
import time

# Initialize pygame and set up the window
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rock Paper Scissors")
clock = pygame.time.Clock()

# Define colors
BACKGROUND = (30, 30, 40)
TEXT_COLOR = (240, 240, 240)
BUTTON_COLOR = (60, 60, 80)
HOVER_COLOR = (80, 120, 255)
WIN_COLOR = (100, 230, 100)
LOSE_COLOR = (230, 100, 100)
TIE_COLOR = (230, 230, 100)

# Game states
IDLE = 0
ANIMATING = 1
RESULT = 2

# Game variables
game_state = IDLE
user_score = 0
computer_score = 0
user_choice = None
computer_choice = None
result = None
animation_start_time = 0
choices = ["rock", "paper", "scissors"]
choice_symbols = {"rock": "✊", "paper": "✋", "scissors": "✌️"}

# Set up fonts
try:
    title_font = pygame.font.SysFont("Arial", 36, bold=True)
    button_font = pygame.font.SysFont("Arial", 24)
    score_font = pygame.font.SysFont("Arial", 48, bold=True)
    symbol_font = pygame.font.SysFont("Arial", 60)
    result_font = pygame.font.SysFont("Arial", 36, bold=True)
except:
    # Fallback to default font if custom font fails
    title_font = pygame.font.Font(None, 36)
    button_font = pygame.font.Font(None, 24)
    score_font = pygame.font.Font(None, 48)
    symbol_font = pygame.font.Font(None, 60)
    result_font = pygame.font.Font(None, 36)

# Button class
class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        
    def draw(self):
        color = HOVER_COLOR if self.hovered else BUTTON_COLOR
        
        # Draw button background
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        # Draw button text
        text_surf = button_font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            self.action()
            return True
        return False

# Create buttons
buttons = []
button_width = 150
button_height = 50
button_y = HEIGHT - 100
button_spacing = (WIDTH - button_width * 3) / 4

for i, choice in enumerate(choices):
    x = button_spacing + i * (button_width + button_spacing)
    
    def make_action(c=choice):  # Use default argument to capture current value
        return lambda: play_game(c)
    
    buttons.append(Button(x, button_y, button_width, button_height, choice.upper(), make_action()))

# Add reset button
reset_button = Button(WIDTH//2 - 75, HEIGHT - 170, 150, 50, "RESET", lambda: reset_game())
buttons.append(reset_button)

def play_game(choice):
    global game_state, user_choice, computer_choice, animation_start_time
    user_choice = choice
    game_state = ANIMATING
    animation_start_time = time.time()

def determine_winner():
    global result, user_score, computer_score, game_state
    
    computer_choice = random.choice(choices)
    
    if user_choice == computer_choice:
        result = "TIE"
    elif ((user_choice == "rock" and computer_choice == "scissors") or
          (user_choice == "paper" and computer_choice == "rock") or
          (user_choice == "scissors" and computer_choice == "paper")):
        result = "YOU WIN"
        user_score += 1
    else:
        result = "CPU WINS"
        computer_score += 1
        
    game_state = RESULT

def reset_game():
    global user_score, computer_score, game_state
    user_score = 0
    computer_score = 0
    game_state = IDLE

def draw_game():
    # Clear screen
    screen.fill(BACKGROUND)
    
    # Draw title
    title = title_font.render("ROCK PAPER SCISSORS", True, TEXT_COLOR)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
    
    # Draw score
    score_text = score_font.render(f"{user_score} - {computer_score}", True, TEXT_COLOR)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 80))
    
    # Draw player labels
    you_text = button_font.render("YOU", True, TEXT_COLOR)
    cpu_text = button_font.render("CPU", True, TEXT_COLOR)
    screen.blit(you_text, (WIDTH//4 - you_text.get_width()//2, 150))
    screen.blit(cpu_text, (3*WIDTH//4 - cpu_text.get_width()//2, 150))
    
    # Draw buttons
    for button in buttons:
        button.draw()
    
    # Draw choices and result based on game state
    if game_state == IDLE:
        if user_choice:
            draw_choice(user_choice, WIDTH//4, HEIGHT//3 + 50)
            draw_choice(computer_choice, 3*WIDTH//4, HEIGHT//3 + 50)
    
    elif game_state == ANIMATING:
        # Animate for 1 second then determine winner
        elapsed = time.time() - animation_start_time
        
        if elapsed < 1.0:
            # Draw animated "thinking" indicators
            animation_frame = int((elapsed * 10) % 3)
            thinking = "." * (animation_frame + 1)
            thinking_text = button_font.render(thinking, True, TEXT_COLOR)
            
            screen.blit(thinking_text, (WIDTH//4 - 10, HEIGHT//3 + 50))
            screen.blit(thinking_text, (3*WIDTH//4 - 10, HEIGHT//3 + 50))
        else:
            determine_winner()
    
    elif game_state == RESULT:
        # Draw choices
        draw_choice(user_choice, WIDTH//4, HEIGHT//3 + 50)
        draw_choice(computer_choice, 3*WIDTH//4, HEIGHT//3 + 50)
        
        # Draw result
        if result == "YOU WIN":
            color = WIN_COLOR
        elif result == "CPU WINS":
            color = LOSE_COLOR
        else:
            color = TIE_COLOR
            
        result_text = result_font.render(result, True, color)
        screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2))

def draw_choice(choice, x, y):
    if not choice:
        return
        
    # Draw choice symbol
    symbol = choice_symbols[choice]
    text = symbol_font.render(symbol, True, TEXT_COLOR)
    screen.blit(text, (x - text.get_width()//2, y - text.get_height()//2))
    
    # Draw choice name
    name = button_font.render(choice.upper(), True, TEXT_COLOR)
    screen.blit(name, (x - name.get_width()//2, y + 40))

def main():
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if game_state != ANIMATING:  # Only allow interaction when not animating
                for button in buttons:
                    button.handle_event(event)
        
        # Update
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.update(mouse_pos)
            
        # Draw
        draw_game()
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()