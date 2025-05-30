import pygame  # Main game library
import random  # For enemy placement
import sys     # For system exit

# Initializing pygame
pygame.init()

# Screen dimensions and setup
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Creating game window
pygame.display.set_caption("Tank War")  # Title of the game window
clock = pygame.time.Clock()  # Clock to control FPS
font = pygame.font.SysFont(None, 36)  # Font for rendering text

# Defining some colors
WHITE, BLACK, RED, GREEN, BLUE = (255, 255, 255), (0, 0, 0), (200, 0, 0), (0, 255, 0), (0, 0, 255)

# Base class for all game objects (uses inheritance)
class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self._rect = pygame.Rect(x, y, width, height)  # Protected rectangle for position and size
        self._color = color  # Protected color

    def draw(self, surface):
        pygame.draw.rect(surface, self._color, self._rect)  # Drawing rectangle object

    def get_rect(self):
        return self._rect  # Accessor for rectangle

# Class for bullets/projectiles fired by the tank
class Projectile(GameObject):
    def __init__(self, x, y, direction, speed=10, damage=20):
        super().__init__(x, y, 10, 4, RED)  # Projectile is a small red rectangle
        self._speed = speed * direction  # Direction: 1 for right
        self._damage = damage  # Damage value

    def update(self):
        self._rect.x += self._speed  # Moving projectile
        if self._rect.right < 0 or self._rect.left > WIDTH:
            self.kill()  # Removing if it leaves screen

    def get_damage(self):
        return self._damage  # Returning damage value

# Player tank class
class Tank(GameObject):
    def __init__(self):
        super().__init__(100, HEIGHT - 80, 60, 40, BLUE)  # Initial tank size and position
        self._health = 100  # Starting health
        self._lives = 3     # Number of lives
        self._projectiles = pygame.sprite.Group()  # Group of bullets
        self._direction = 1  # Always faces/shoots right

        # Jump-related attributes
        self._vel_y = 0           # Vertical velocity
        self._on_ground = True    # Is the tank touching the ground?
        self._gravity = 0.5       # Gravity constant
        self._jump_power = -10    # Jump velocity (negative to go up)

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self._rect.x -= 5  # Move left
        if keys[pygame.K_RIGHT]:
            self._rect.x += 5  # Move right
        if keys[pygame.K_UP] and self._on_ground:  # Jump when UP key pressed and on ground
            self._vel_y = self._jump_power
            self._on_ground = False

        # Apply gravity
        self._vel_y += self._gravity
        self._rect.y += self._vel_y

        # Ground collision detection (simulate ground at HEIGHT - 40)
        if self._rect.bottom >= HEIGHT - 40:
            self._rect.bottom = HEIGHT - 40
            self._vel_y = 0
            self._on_ground = True

    def shoot(self):
        bullet = Projectile(self._rect.right, self._rect.centery, direction=1)
        self._projectiles.add(bullet)  # Add new bullet to group

    def update(self):
        self._projectiles.update()  # Update all projectiles

    def take_damage(self, amount):
        self._health -= amount
        if self._health <= 0:
            self._lives -= 1
            self._health = 100  # Reset health if a life is lost

    def is_alive(self):
        return self._lives > 0

    def get_projectiles(self):
        return self._projectiles  # Return bullet group

    def get_health(self):
        return self._health

    def get_lives(self):
        return self._lives

    def draw(self, surface):
        super().draw(surface)  # Draw the tank
        for projectile in self._projectiles:
            projectile.draw(surface)  # Draw bullets

# Enemy tank class
class Enemy(GameObject):
    def __init__(self, x, y, health=50, speed=-2):
        super().__init__(x, y, 40, 40, RED)  # Size and color
        self._health = health
        self._speed = speed

    def update(self):
        self._rect.x += self._speed  # Move enemy
        if self._rect.right < 0 or self._rect.left > WIDTH:
            self._speed *= -1  # Change direction if out of bounds

    def take_damage(self, damage):
        self._health -= damage

    def is_alive(self):
        return self._health > 0

    def draw(self, surface):
        super().draw(surface)  # Draw enemy
        pygame.draw.rect(surface, BLACK, (self._rect.x, self._rect.y - 10, 40, 5))  # Health bar background
        pygame.draw.rect(surface, GREEN, (self._rect.x, self._rect.y - 10, max(0, self._health * 0.8), 5))  # Current health

# Boss class that inherits from Enemy
class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=300, speed=-1)  # Stronger and slower
        self._rect = pygame.Rect(x, y, 100, 100)  # Bigger size
        self._color = (128, 0, 128)  # Different color

    def draw(self, surface):
        pygame.draw.rect(surface, self._color, self._rect)  # Boss rectangle
        pygame.draw.rect(surface, BLACK, (self._rect.x, self._rect.y - 10, 100, 10))  # Health bar background
        pygame.draw.rect(surface, GREEN, (self._rect.x, self._rect.y - 10, max(0, self._health * 0.33), 10))  # Health

# Main game class that controls levels, UI, logic
class Game:
    def __init__(self):
        self._level = 1  # Start at level 1
        self._score = 0
        self._tank = Tank()
        self._enemies = pygame.sprite.Group()
        self._boss = None
        self._game_over = False
        self.load_level()  # Load initial level

    def load_level(self):
        self._enemies.empty()
        self._boss = None
        if self._level == 3:
            self._boss = Boss(WIDTH - 150, HEIGHT - 120)  # Final level boss
        else:
            for _ in range(3 + self._level):  # More enemies each level
                x = random.randint(WIDTH // 2, WIDTH - 60)
                y = HEIGHT - 80
                self._enemies.add(Enemy(x, y))

    def next_level(self):
        self._level += 1
        if self._level > 3:
            self._game_over = True  # End game if levels are done
        else:
            self.load_level()

    def update(self):
        self._tank.update()
        self._enemies.update()
        if self._boss:
            self._boss.update()

        # Collision: projectile vs enemy
        for bullet in self._tank.get_projectiles():
            for enemy in self._enemies:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    enemy.take_damage(bullet.get_damage())
                    bullet.kill()
                    if not enemy.is_alive():
                        self._enemies.remove(enemy)
                        self._score += 10  # Add score

            if self._boss and bullet.get_rect().colliderect(self._boss.get_rect()):
                self._boss.take_damage(bullet.get_damage())
                bullet.kill()
                if not self._boss.is_alive():
                    self._boss = None
                    self._score += 100
                    self.next_level()

        # Collision: enemy touches tank
        for enemy in self._enemies:
            if self._tank.get_rect().colliderect(enemy.get_rect()):
                self._tank.take_damage(1)

        if self._boss and self._tank.get_rect().colliderect(self._boss.get_rect()):
            self._tank.take_damage(2)

        if not self._tank.is_alive():
            self._game_over = True

        if not self._boss and not self._enemies and self._level < 3:
            self.next_level()

    def draw_ui(self):
        # Display health, lives, score, level
        screen.blit(font.render(f"Health: {self._tank.get_health()}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Lives: {self._tank.get_lives()}", True, WHITE), (10, 40))
        screen.blit(font.render(f"Score: {self._score}", True, WHITE), (10, 70))
        screen.blit(font.render(f"Level: {self._level}", True, WHITE), (10, 100))

    def render(self):
        screen.fill((30, 30, 30))  # Clear screen
        self._tank.draw(screen)  # Draw tank
        for enemy in self._enemies:
            enemy.draw(screen)  # Draw each enemy
        if self._boss:
            self._boss.draw(screen)  # Draw boss if exists
        self.draw_ui()  # Draw stats
        pygame.display.flip()  # Update display

    def run(self):
        while not self._game_over:
            clock.tick(60)  # Maintain 60 FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self._tank.shoot()  # Shoot on spacebar

            keys = pygame.key.get_pressed()
            self._tank.move(keys)  # Move tank

            self.update()  # Update game state
            self.render()  # Render everything

        self.show_game_over()  # End screen

    def show_game_over(self):
        screen.fill(BLACK)
        text = font.render("GAME OVER - Press R to Restart", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2))
        pygame.display.flip()
        self.wait_restart()

    def wait_restart(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.__init__()  # Restart game
                    self.run()

# Start the game
if __name__ == "__main__":
    Game().run()
