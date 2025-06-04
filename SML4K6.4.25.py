import pygame
import sys
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Land")

# Colors
SKY_BLUE = (107, 140, 255)
GROUND_GREEN = (86, 173, 86)
RED = (231, 76, 60)
BROWN = (155, 118, 83)
YELLOW = (241, 196, 15)
BLUE = (52, 152, 219)
GREEN = (46, 204, 113)
PURPLE = (155, 89, 182)
BLACK = (30, 30, 30)
WHITE = (240, 240, 240)
GRAY = (100, 100, 100)

# Game constants
FPS = 60
GRAVITY = 0.5
PLAYER_SPEED = 4
JUMP_STRENGTH = 11
SCROLL_THRESH = 200

# Font
font = pygame.font.SysFont(None, 32)
small_font = pygame.font.SysFont(None, 24)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 32
        self.vel_y = 0
        self.jumping = False
        self.direction = 1  # 1 for right, -1 for left
        self.animation_counter = 0
        self.invincible = 0
        self.lives = 3
        self.coins = 0
        self.active = True
        
    def move(self, dx, platforms, enemies, coins):
        if not self.active:
            return
            
        # Move horizontally
        self.x += dx
        if dx != 0:
            self.direction = 1 if dx > 0 else -1
        
        # Check collisions with platforms
        for platform in platforms:
            if self.collision(platform):
                if dx > 0:  # Moving right
                    self.x = platform.x - self.width
                if dx < 0:  # Moving left
                    self.x = platform.x + platform.width
        
        # Apply gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # Check collisions with platforms vertically
        for platform in platforms:
            if self.collision(platform):
                if self.vel_y > 0:  # Falling
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.jumping = False
                elif self.vel_y < 0:  # Jumping
                    self.y = platform.y + platform.height
                    self.vel_y = 0
        
        # Check collisions with enemies
        for enemy in enemies:
            if self.collision(enemy):
                if self.vel_y > 0 and self.y + self.height < enemy.y + enemy.height/2:
                    # Jump on enemy
                    enemy.active = False
                    self.vel_y = -JUMP_STRENGTH * 0.7
                    self.coins += 1
                elif self.invincible <= 0:
                    # Take damage
                    self.invincible = 60
                    self.lives -= 1
                    if self.lives <= 0:
                        self.active = False
        
        # Check collisions with coins
        for coin in coins[:]:
            if self.collision(coin):
                coins.remove(coin)
                self.coins += 1
    
    def collision(self, obj):
        return (self.x < obj.x + obj.width and
                self.x + self.width > obj.x and
                self.y < obj.y + obj.height and
                self.y + self.height > obj.y)
    
    def jump(self):
        if not self.jumping:
            self.vel_y = -JUMP_STRENGTH
            self.jumping = True
    
    def draw(self, screen, scroll_x):
        if not self.active:
            return
            
        if self.invincible > 0:
            if self.invincible % 6 < 3:  # Flashing effect
                return
            self.invincible -= 1
        
        # Draw Mario
        x_pos = self.x - scroll_x
        
        # Body
        pygame.draw.rect(screen, RED, (x_pos + 4, self.y + 8, self.width - 8, self.height - 8))
        
        # Head
        pygame.draw.rect(screen, (255, 200, 150), (x_pos + 4, self.y, self.width - 8, 12))
        
        # Hat
        pygame.draw.rect(screen, RED, (x_pos + 2, self.y - 4, self.width - 4, 8))
        pygame.draw.rect(screen, RED, (x_pos, self.y + 4, self.width, 4))
        
        # Animation - legs
        leg_offset = math.sin(self.animation_counter * 0.5) * 3 if abs(self.vel_y) < 0.1 else 0
        pygame.draw.rect(screen, BLUE, (x_pos + 4, self.y + self.height - 8, 6, 8))
        pygame.draw.rect(screen, BLUE, (x_pos + self.width - 10, self.y + self.height - 8 + leg_offset, 6, 8))
        
        self.animation_counter += 1

class Platform:
    def __init__(self, x, y, width, height, color=BROWN):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, screen, scroll_x):
        pygame.draw.rect(screen, self.color, (self.x - scroll_x, self.y, self.width, self.height))
        # Draw platform details
        pygame.draw.rect(screen, (139, 69, 19), (self.x - scroll_x, self.y, self.width, 4))
        for i in range(int(self.width / 20)):
            pygame.draw.line(screen, (101, 67, 33), 
                            (self.x - scroll_x + i*20, self.y + 4),
                            (self.x - scroll_x + i*20, self.y + self.height), 2)

class Enemy:
    def __init__(self, x, y, width=24, height=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.direction = -1
        self.speed = 1
        self.active = True
    
    def move(self, platforms):
        if not self.active:
            return
            
        self.x += self.direction * self.speed
        
        # Change direction if at edge or hitting wall
        on_ground = False
        for platform in platforms:
            # Check if enemy is on a platform
            if (self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                abs((self.y + self.height) - platform.y) < 5):
                on_ground = True
                
                # Check if at edge
                if (self.direction == -1 and self.x <= platform.x) or \
                   (self.direction == 1 and self.x + self.width >= platform.x + platform.width):
                    self.direction *= -1
        
        # If not on ground, turn around
        if not on_ground:
            self.direction *= -1
    
    def draw(self, screen, scroll_x):
        if not self.active:
            return
            
        x_pos = self.x - scroll_x
        
        # Draw Goomba
        pygame.draw.ellipse(screen, BROWN, (x_pos, self.y, self.width, self.height))
        pygame.draw.ellipse(screen, (101, 67, 33), (x_pos, self.y, self.width, self.height/2))
        
        # Eyes
        eye_offset = 4 if self.direction > 0 else -4
        pygame.draw.circle(screen, WHITE, (x_pos + 8 + eye_offset, self.y + 8), 4)
        pygame.draw.circle(screen, WHITE, (x_pos + self.width - 8 + eye_offset, self.y + 8), 4)
        pygame.draw.circle(screen, BLACK, (x_pos + 8 + eye_offset, self.y + 8), 2)
        pygame.draw.circle(screen, BLACK, (x_pos + self.width - 8 + eye_offset, self.y + 8), 2)
        
        # Feet
        pygame.draw.ellipse(screen, (101, 67, 33), (x_pos + 2, self.y + self.height - 6, 8, 6))
        pygame.draw.ellipse(screen, (101, 67, 33), (x_pos + self.width - 10, self.y + self.height - 6, 8, 6))

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 12
        self.height = 12
        self.animation_counter = 0
    
    def draw(self, screen, scroll_x):
        self.animation_counter += 0.2
        y_offset = math.sin(self.animation_counter) * 3
        
        # Draw coin
        pygame.draw.circle(screen, YELLOW, (self.x - scroll_x + self.width//2, self.y + y_offset + self.height//2), 6)
        pygame.draw.circle(screen, (255, 223, 0), (self.x - scroll_x + self.width//2, self.y + y_offset + self.height//2), 4)
        pygame.draw.circle(screen, (255, 239, 0), (self.x - scroll_x + self.width//2, self.y + y_offset + self.height//2), 2)

class Goal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 60
    
    def draw(self, screen, scroll_x):
        # Draw flag pole
        pygame.draw.rect(screen, GRAY, (self.x - scroll_x + 14, self.y, 2, self.height))
        
        # Draw flag
        pygame.draw.polygon(screen, RED, [
            (self.x - scroll_x + 16, self.y + 10),
            (self.x - scroll_x + 16, self.y + 30),
            (self.x - scroll_x + 30, self.y + 20)
        ])

class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.platforms = []
        self.enemies = []
        self.coins = []
        self.goal = None
        self.level_width = 2000
        self.player_start = (50, 300)
        
        # Create level based on level number
        if level_num == 1:
            self.create_level_1()
        elif level_num == 2:
            self.create_level_2()
        elif level_num == 3:
            self.create_level_3()
    
    def create_level_1(self):
        # Ground
        self.platforms.append(Platform(0, HEIGHT - 40, self.level_width, 40, GROUND_GREEN))
        
        # Platforms
        self.platforms.append(Platform(200, 300, 100, 20))
        self.platforms.append(Platform(400, 250, 80, 20))
        self.platforms.append(Platform(600, 200, 120, 20))
        self.platforms.append(Platform(900, 250, 100, 20))
        self.platforms.append(Platform(1200, 300, 150, 20))
        
        # Coins
        for i in range(5):
            self.coins.append(Coin(300 + i*150, 250))
        
        # Enemies
        self.enemies.append(Enemy(300, 300))
        self.enemies.append(Enemy(700, 200))
        self.enemies.append(Enemy(1100, 300))
        
        # Goal
        self.goal = Goal(1800, 220)
    
    def create_level_2(self):
        # Ground
        self.platforms.append(Platform(0, HEIGHT - 40, self.level_width, 40, GROUND_GREEN))
        
        # Platforms
        self.platforms.append(Platform(150, 280, 80, 20))
        self.platforms.append(Platform(300, 220, 100, 20))
        self.platforms.append(Platform(500, 280, 120, 20))
        self.platforms.append(Platform(700, 180, 80, 20))
        self.platforms.append(Platform(900, 250, 100, 20))
        self.platforms.append(Platform(1100, 300, 150, 20))
        self.platforms.append(Platform(1400, 200, 100, 20))
        
        # Coins
        for i in range(8):
            self.coins.append(Coin(200 + i*120, 200 + (i % 3)*20))
        
        # Enemies
        self.enemies.append(Enemy(250, 280))
        self.enemies.append(Enemy(550, 280))
        self.enemies.append(Enemy(750, 180))
        self.enemies.append(Enemy(1200, 300))
        
        # Goal
        self.goal = Goal(1850, 150)
    
    def create_level_3(self):
        # Ground
        self.platforms.append(Platform(0, HEIGHT - 40, self.level_width, 40, GROUND_GREEN))
        
        # Platforms
        self.platforms.append(Platform(100, 250, 100, 20))
        self.platforms.append(Platform(300, 180, 80, 20))
        self.platforms.append(Platform(500, 300, 120, 20))
        self.platforms.append(Platform(700, 220, 100, 20))
        self.platforms.append(Platform(900, 150, 80, 20))
        self.platforms.append(Platform(1100, 250, 100, 20))
        self.platforms.append(Platform(1300, 180, 120, 20))
        self.platforms.append(Platform(1500, 280, 100, 20))
        self.platforms.append(Platform(1700, 200, 150, 20))
        
        # Coins
        for i in range(10):
            self.coins.append(Coin(150 + i*100, 180 + (i % 4)*30))
        
        # Enemies
        self.enemies.append(Enemy(350, 180))
        self.enemies.append(Enemy(550, 300))
        self.enemies.append(Enemy(750, 220))
        self.enemies.append(Enemy(950, 150))
        self.enemies.append(Enemy(1350, 180))
        self.enemies.append(Enemy(1750, 200))
        
        # Goal
        self.goal = Goal(1900, 120)

class Game:
    def __init__(self):
        self.state = "menu"  # menu, level_select, playing, game_over, victory
        self.current_level = 1
        self.player = None
        self.level = None
        self.scroll_x = 0
        self.level_complete = [False] * 3
        self.level_complete[0] = True  # First level always available
        
    def start_level(self, level_num):
        self.current_level = level_num
        self.level = Level(level_num)
        self.player = Player(*self.level.player_start)
        self.scroll_x = 0
        self.state = "playing"
    
    def run(self):
        clock = pygame.time.Clock()
        
        while True:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing":
                            self.state = "level_select"
                    
                    if self.state == "playing":
                        if event.key == pygame.K_SPACE:
                            self.player.jump()
                    
                    if self.state == "menu":
                        if event.key == pygame.K_RETURN:
                            self.state = "level_select"
                    
                    if self.state == "level_select":
                        if event.key == pygame.K_1 and self.level_complete[0]:
                            self.start_level(1)
                        if event.key == pygame.K_2 and self.level_complete[1]:
                            self.start_level(2)
                        if event.key == pygame.K_3 and self.level_complete[2]:
                            self.start_level(3)
                    
                    if self.state in ["game_over", "victory"]:
                        if event.key == pygame.K_RETURN:
                            self.state = "level_select"
            
            # Game logic
            if self.state == "playing":
                keys = pygame.key.get_pressed()
                dx = 0
                if keys[pygame.K_LEFT]:
                    dx = -PLAYER_SPEED
                if keys[pygame.K_RIGHT]:
                    dx = PLAYER_SPEED
                
                self.player.move(dx, self.level.platforms, self.level.enemies, self.level.coins)
                
                # Move enemies
                for enemy in self.level.enemies:
                    if enemy.active:
                        enemy.move(self.level.platforms)
                
                # Scroll screen
                if self.player.x - self.scroll_x > WIDTH - SCROLL_THRESH:
                    self.scroll_x = self.player.x - (WIDTH - SCROLL_THRESH)
                if self.player.x - self.scroll_x < SCROLL_THRESH:
                    self.scroll_x = self.player.x - SCROLL_THRESH
                
                # Keep scroll within level bounds
                if self.scroll_x < 0:
                    self.scroll_x = 0
                if self.scroll_x > self.level.level_width - WIDTH:
                    self.scroll_x = self.level.level_width - WIDTH
                
                # Check if player reached goal
                if self.player.collision(self.level.goal):
                    self.level_complete[self.current_level - 1] = True
                    if self.current_level < 3:
                        self.level_complete[self.current_level] = True
                    self.state = "victory"
                
                # Check if player died
                if not self.player.active or self.player.y > HEIGHT:
                    self.state = "game_over"
            
            # Drawing
            screen.fill(SKY_BLUE)
            
            # Draw clouds
            for i in range(5):
                x = (i * 300 + self.scroll_x // 3) % (WIDTH + 300) - 100
                pygame.draw.ellipse(screen, WHITE, (x, 50, 80, 40))
                pygame.draw.ellipse(screen, WHITE, (x + 20, 40, 70, 40))
                pygame.draw.ellipse(screen, WHITE, (x + 40, 50, 60, 40))
            
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "level_select":
                self.draw_level_select()
            elif self.state == "playing":
                self.draw_game()
            elif self.state == "game_over":
                self.draw_game()
                self.draw_game_over()
            elif self.state == "victory":
                self.draw_game()
                self.draw_victory()
            
            # Draw UI
            if self.state == "playing":
                self.draw_ui()
            
            pygame.display.flip()
            clock.tick(FPS)
    
    def draw_menu(self):
        # Draw title
        title = font.render("SUPER MARIO LAND", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        
        # Draw instructions
        instructions = small_font.render("Press ENTER to start", True, WHITE)
        screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT//2))
        
        # Draw character
        pygame.draw.rect(screen, RED, (WIDTH//2 - 10, HEIGHT*3//4 - 20, 20, 30))
        pygame.draw.rect(screen, (255, 200, 150), (WIDTH//2 - 10, HEIGHT*3//4 - 30, 20, 15))
        pygame.draw.rect(screen, RED, (WIDTH//2 - 15, HEIGHT*3//4 - 35, 30, 10))
        
        # Draw ground
        pygame.draw.rect(screen, GROUND_GREEN, (0, HEIGHT - 40, WIDTH, 40))
    
    def draw_level_select(self):
        # Draw title
        title = font.render("SELECT A LEVEL", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Draw level options
        for i in range(3):
            color = GREEN if self.level_complete[i] else GRAY
            level_text = font.render(f"LEVEL {i+1}", True, color)
            screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 150 + i*80))
            
            if self.level_complete[i]:
                key_text = small_font.render(f"Press {i+1} to play", True, WHITE)
                screen.blit(key_text, (WIDTH//2 - key_text.get_width()//2, 190 + i*80))
            
            # Draw level preview
            preview_y = 150 + i*80
            pygame.draw.rect(screen, GROUND_GREEN, (WIDTH//2 - 70, preview_y - 10, 140, 60))
            
            # Draw platforms
            pygame.draw.rect(screen, BROWN, (WIDTH//2 - 60, preview_y + 10, 40, 10))
            pygame.draw.rect(screen, BROWN, (WIDTH//2, preview_y, 30, 10))
            
            # Draw player
            pygame.draw.rect(screen, RED, (WIDTH//2 - 50, preview_y, 8, 12))
            
            # Draw goal
            pygame.draw.rect(screen, GRAY, (WIDTH//2 + 50, preview_y - 20, 3, 30))
            pygame.draw.polygon(screen, RED, [
                (WIDTH//2 + 53, preview_y - 15),
                (WIDTH//2 + 53, preview_y),
                (WIDTH//2 + 65, preview_y - 7)
            ])
    
    def draw_game(self):
        # Draw platforms
        for platform in self.level.platforms:
            platform.draw(screen, self.scroll_x)
        
        # Draw coins
        for coin in self.level.coins:
            coin.draw(screen, self.scroll_x)
        
        # Draw enemies
        for enemy in self.level.enemies:
            if enemy.active:
                enemy.draw(screen, self.scroll_x)
        
        # Draw goal
        if self.level.goal:
            self.level.goal.draw(screen, self.scroll_x)
        
        # Draw player
        self.player.draw(screen, self.scroll_x)
    
    def draw_ui(self):
        # Draw lives
        for i in range(self.player.lives):
            pygame.draw.rect(screen, RED, (10 + i*25, 10, 15, 20))
        
        # Draw coins
        coin_text = small_font.render(f"Coins: {self.player.coins}", True, YELLOW)
        screen.blit(coin_text, (WIDTH - coin_text.get_width() - 10, 10))
        
        # Draw level
        level_text = small_font.render(f"Level: {self.current_level}", True, WHITE)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 10))
        
        # Draw controls hint
        hint = small_font.render("ESC: Level Select", True, GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        game_over = font.render("GAME OVER", True, RED)
        screen.blit(game_over, (WIDTH//2 - game_over.get_width()//2, HEIGHT//3))
        
        restart = small_font.render("Press ENTER to continue", True, WHITE)
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT*2//3))
    
    def draw_victory(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        victory = font.render("LEVEL COMPLETE!", True, GREEN)
        screen.blit(victory, (WIDTH//2 - victory.get_width()//2, HEIGHT//3))
        
        coins = small_font.render(f"Coins collected: {self.player.coins}", True, YELLOW)
        screen.blit(coins, (WIDTH//2 - coins.get_width()//2, HEIGHT//2))
        
        next_level = small_font.render("Press ENTER to continue", True, WHITE)
        screen.blit(next_level, (WIDTH//2 - next_level.get_width()//2, HEIGHT*2//3))

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()
