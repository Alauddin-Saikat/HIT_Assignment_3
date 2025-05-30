import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank War")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# Colors
WHITE, BLACK, RED, GREEN, BLUE = (255, 255, 255), (0, 0, 0), (200, 0, 0), (0, 255, 0), (0, 0, 255)
PURPLE = (128, 0, 128)

class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self._rect = pygame.Rect(x, y, width, height)
        self._color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self._color, self._rect)

    def get_rect(self):
        return self._rect

class Projectile(GameObject):
    def __init__(self, x, y, direction, speed=10, damage=20, color=RED):
        super().__init__(x, y, 10, 4, color)
        self._speed = speed * direction
        self._damage = damage
        self._direction = direction

    def update(self):
        self._rect.x += self._speed
        if self._rect.right < 0 or self._rect.left > WIDTH:
            self.kill()

    def get_damage(self):
        return self._damage

    def get_direction(self):
        return self._direction

class Tank(GameObject):
    def __init__(self):
        super().__init__(100, HEIGHT - 80, 60, 40, BLUE)
        self._health = 100
        self._lives = 3
        self._projectiles = pygame.sprite.Group()
        self._direction = 1
        self._vel_y = 0
        self._on_ground = True
        self._gravity = 0.5
        self._jump_power = -10
        self._shoot_cooldown = 0

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self._rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self._rect.x += 5
        if keys[pygame.K_UP] and self._on_ground:
            self._vel_y = self._jump_power
            self._on_ground = False

        self._vel_y += self._gravity
        self._rect.y += self._vel_y

        if self._rect.bottom >= HEIGHT - 40:
            self._rect.bottom = HEIGHT - 40
            self._vel_y = 0
            self._on_ground = True

        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1

    def shoot(self):
        if self._shoot_cooldown == 0:
            bullet = Projectile(self._rect.right, self._rect.centery, direction=1)
            self._projectiles.add(bullet)
            self._shoot_cooldown = 15

    def update(self):
        self._projectiles.update()

    def take_damage(self, amount):
        self._health -= amount
        if self._health <= 0:
            self._lives -= 1
            self._health = 100

    def is_alive(self):
        return self._lives > 0

    def get_projectiles(self):
        return self._projectiles

    def get_health(self):
        return self._health

    def get_lives(self):
        return self._lives

    def draw(self, surface):
        super().draw(surface)
        for projectile in self._projectiles:
            projectile.draw(surface)

class Enemy(GameObject):
    def __init__(self, x, y, health=50, speed=-2, can_shoot=False):
        super().__init__(x, y, 40, 40, RED)
        self._health = health
        self._speed = speed
        self._can_shoot = can_shoot
        self._projectiles = pygame.sprite.Group()
        self._shoot_timer = random.randint(60, 180)
        self._direction = -1

    def update(self):
        self._rect.x += self._speed
        
        if self._can_shoot:
            self._shoot_timer -= 1
            if self._shoot_timer <= 0:
                self.shoot()
                self._shoot_timer = random.randint(60, 180)
        
        self._projectiles.update()

    def shoot(self):
        bullet = Projectile(self._rect.left, self._rect.centery, direction=-1, color=GREEN)
        self._projectiles.add(bullet)

    def take_damage(self, damage):
        self._health -= damage

    def is_alive(self):
        return self._health > 0

    def get_projectiles(self):
        return self._projectiles

    def draw(self, surface):
        super().draw(surface)
        pygame.draw.rect(surface, BLACK, (self._rect.x, self._rect.y - 10, 40, 5))
        pygame.draw.rect(surface, GREEN, (self._rect.x, self._rect.y - 10, max(0, self._health * 0.8), 5))
        for projectile in self._projectiles:
            projectile.draw(surface)

class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=300, speed=-1, can_shoot=True)
        self._rect = pygame.Rect(x, y, 100, 100)
        self._color = PURPLE
        self._shoot_timer = 30

    def draw(self, surface):
        pygame.draw.rect(surface, self._color, self._rect)
        pygame.draw.rect(surface, BLACK, (self._rect.x, self._rect.y - 15, 100, 10))
        pygame.draw.rect(surface, GREEN, (self._rect.x, self._rect.y - 15, max(0, self._health * 0.33), 10))
        for projectile in self._projectiles:
            projectile.draw(surface)

class Game:
    def __init__(self):
        self._level = 1
        self._score = 0
        self._tank = Tank()
        self._enemies = pygame.sprite.Group()
        self._boss = None
        self._game_over = False
        self._won_game = False
        self._show_instructions = True
        self._level_complete = False
        self._enemies_killed = 0
        self._enemy_spawn_timer = 0
        self.load_level()

    def show_instructions(self):
        while self._show_instructions:
            screen.fill(BLACK)
            
            title = font.render("TANK WAR - INSTRUCTIONS", True, WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
            
            instructions = [
                "CONTROLS:",
                "- LEFT/RIGHT ARROW KEYS: Move Tank",
                "- UP ARROW KEY: Jump",
                "- SPACEBAR: Shoot",
                "",
                "LEVELS:",
                "- Level 1: Kill 20 enemies (some can shoot)",
                "- Level 2: Kill 20 enemies (more can shoot)",
                "- Level 3: Kill 20 enemies then defeat the boss",
                "",
                "COMBAT:",
                "- Enemy bullets can be destroyed by your bullets",
                "- Avoid enemy contact to prevent damage",
                "",
                "Press SPACE to start the game"
            ]
            
            y_pos = 120
            for line in instructions:
                if line.startswith("-"):
                    text = small_font.render(line, True, WHITE)
                else:
                    text = font.render(line, True, GREEN if "CONTROLS" in line else 
                                     BLUE if "LEVELS" in line else RED)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, y_pos))
                y_pos += 40 if line.startswith("-") else 50
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self._show_instructions = False

    def load_level(self):
        self._enemies.empty()
        self._boss = None
        self._level_complete = False
        self._enemies_killed = 0
        self._enemy_spawn_timer = 0

    def spawn_enemy(self):
        if self._enemy_spawn_timer <= 0:
            x = random.randint(WIDTH // 2, WIDTH - 60)
            y = HEIGHT - 80
            
            # Determine enemy type based on level
            if self._level == 1:
                can_shoot = random.random() < 0.3  # 30% chance to shoot in level 1
            elif self._level == 2:
                can_shoot = random.random() < 0.7  # 70% chance to shoot in level 2
            else:  # level 3
                can_shoot = True  # All enemies shoot in level 3
            
            self._enemies.add(Enemy(x, y, can_shoot=can_shoot))
            self._enemy_spawn_timer = random.randint(30, 90)  # Spawn delay
        else:
            self._enemy_spawn_timer -= 1

    def show_level_complete(self):
        screen.fill(BLACK)
        text = font.render(f"Level {self._level} Complete! Press ENTER to continue", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False
                    self._level += 1
                    if self._level <= 3:
                        self.load_level()
                    else:
                        self._won_game = True
                        self._game_over = True

    def update(self):
        if self._level_complete:
            return

        # Spawn new enemies continuously
        self.spawn_enemy()

        self._tank.update()
        self._enemies.update()
        
        if self._boss:
            self._boss.update()

        # Player bullets vs enemies
        for bullet in self._tank._projectiles:
            for enemy in self._enemies:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    enemy.take_damage(bullet.get_damage())
                    bullet.kill()
                    if not enemy.is_alive():
                        self._enemies.remove(enemy)
                        self._score += 10
                        self._enemies_killed += 1

            # Player bullets vs boss
            if self._boss and bullet.get_rect().colliderect(self._boss.get_rect()):
                self._boss.take_damage(bullet.get_damage())
                bullet.kill()
                if not self._boss.is_alive():
                    self._boss = None
                    self._score += 100
                    self._level_complete = True

            # Player bullets vs enemy bullets
            for enemy in self._enemies:
                for enemy_bullet in enemy._projectiles:
                    if bullet.get_rect().colliderect(enemy_bullet.get_rect()):
                        bullet.kill()
                        enemy_bullet.kill()

        # Enemy bullets vs player
        for enemy in self._enemies:
            for bullet in enemy._projectiles:
                if bullet.get_rect().colliderect(self._tank.get_rect()):
                    self._tank.take_damage(bullet.get_damage())
                    bullet.kill()

        # Boss bullets vs player
        if self._boss:
            for bullet in self._boss._projectiles:
                if bullet.get_rect().colliderect(self._tank.get_rect()):
                    self._tank.take_damage(bullet.get_damage())
                    bullet.kill()

        # Enemy contact damage
        for enemy in self._enemies:
            if self._tank.get_rect().colliderect(enemy.get_rect()):
                self._tank.take_damage(1)

        if self._boss and self._tank.get_rect().colliderect(self._boss.get_rect()):
            self._tank.take_damage(2)

        # Level completion conditions
        if self._level < 3 and self._enemies_killed >= 20:
            self._level_complete = True
        elif self._level == 3:
            if self._enemies_killed >= 20 and not self._boss:
                self._boss = Boss(WIDTH - 150, HEIGHT - 120)
            elif self._boss and not self._boss.is_alive():
                self._level_complete = True
        
        if not self._tank.is_alive():
            self._game_over = True

    def draw_ui(self):
        screen.blit(font.render(f"Health: {self._tank.get_health()}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Lives: {self._tank.get_lives()}", True, WHITE), (10, 40))
        screen.blit(font.render(f"Score: {self._score}", True, WHITE), (10, 70))
        screen.blit(font.render(f"Level: {self._level}", True, WHITE), (10, 100))
        screen.blit(font.render(f"Killed: {self._enemies_killed}/20", True, WHITE), (10, 130))
        
        if self._level == 3 and self._enemies_killed >= 20 and not self._boss:
            screen.blit(font.render("BOSS INCOMING!", True, RED), (WIDTH - 200, 10))

    def render(self):
        screen.fill((30, 30, 30))
        
        # Draw ground
        pygame.draw.rect(screen, (100, 100, 100), (0, HEIGHT - 40, WIDTH, 40))
        
        self._tank.draw(screen)
        for enemy in self._enemies:
            enemy.draw(screen)
        if self._boss:
            self._boss.draw(screen)
        
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        self.show_instructions()
        
        while not self._game_over:
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self._tank.shoot()

            keys = pygame.key.get_pressed()
            self._tank.move(keys)

            self.update()
            self.render()
            
            if self._level_complete:
                self.show_level_complete()

        self.show_game_over()

    def show_game_over(self):
        screen.fill(BLACK)
        if self._won_game:
            text = font.render("CONGRATULATIONS! You Won!", True, GREEN)
            score_text = font.render(f"Final Score: {self._score}", True, WHITE)
            restart = font.render("Press R to Restart", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 50))
        else:
            text = font.render("GAME OVER", True, RED)
            score_text = font.render(f"Score: {self._score}", True, WHITE)
            restart = font.render("Press R to Restart", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        self.wait_restart()

    def wait_restart(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.__init__()
                    self.run()

if __name__ == "__main__":
    Game().run()