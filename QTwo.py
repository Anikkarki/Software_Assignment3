import pygame
import random

pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WORLD_WIDTH = 1600  # The total width of the game world (larger than screen)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Camera class to handle dynamic movement
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Shift entities according to the camera position
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        # Camera follows the player smoothly
        x = -target.rect.x + int(SCREEN_WIDTH / 2)
        y = -target.rect.y + int(SCREEN_HEIGHT / 2)
        
        # Limit scrolling to the boundaries of the world
        x = min(0, x)  # Left boundary
        x = max(-(self.width - SCREEN_WIDTH), x)  # Right boundary
        y = max(-(self.height - SCREEN_HEIGHT), y)  # Bottom boundary
        y = min(0, y)  # Top boundary
        
        self.camera = pygame.Rect(x, y, self.width, self.height)

# Player class with movement, jumping, and shooting
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((80, 40))  # Wider to resemble a tank
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - 100
        self.speed = 5
        self.jump_power = -15
        self.gravity = 1
        self.velocity_y = 0
        self.is_jumping = False
        self.health = 100
        self.lives = 3
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.jump()
        
        self.rect.y += self.velocity_y
        self.velocity_y += self.gravity
        
        # Prevent falling through the floor
        if self.rect.y >= SCREEN_HEIGHT - 100:
            self.rect.y = SCREEN_HEIGHT - 100
            self.is_jumping = False

    def jump(self):
        self.is_jumping = True
        self.velocity_y = self.jump_power

    def shoot(self):
        bullet = Projectile(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Projectile (bullet) class
# Projectile (bullet) class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))  # Smaller for bullet
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed  # Move the bullet upwards
        if self.rect.bottom < 0:  # Remove bullet if it goes off the top of the screen
            self.kill()


# Enemy class (tank-like)
class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed_increase=0):
        super().__init__()
        self.image = pygame.Surface((80, 40))  # Tank shape
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(SCREEN_WIDTH, WORLD_WIDTH)
        self.rect.y = random.randint(100, SCREEN_HEIGHT - 150)
        self.speed = random.randint(2, 5) + speed_increase
    
    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# Health collectible class
class Collectible(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WORLD_WIDTH - 20)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - 100)
    
    def update(self):
        pass

# Main game loop
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tank Side-Scrolling Game")
clock = pygame.time.Clock()

player = Player()
camera = Camera(WORLD_WIDTH, SCREEN_HEIGHT)

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
collectibles = pygame.sprite.Group()

all_sprites.add(player)

# Score, level, and health tracking
score = 0
level = 1
font = pygame.font.SysFont(None, 36)

def display_info():
    health_text = font.render(f"Health: {player.health}", True, WHITE)
    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(health_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    screen.blit(score_text, (10, 70))
    screen.blit(level_text, (10, 100))

running = True
game_over = False

# Game Loop
while running:
    clock.tick(60)
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # Shoot with 's' key
                player.shoot()

    # Spawn enemies with increasing difficulty per level
    if random.randint(1, 60) == 1:
        enemy = Enemy(speed_increase=level)  # Enemies get faster with higher levels
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Spawn collectibles
    if random.randint(1, 300) == 1:
        collectible = Collectible()
        all_sprites.add(collectible)
        collectibles.add(collectible)

    if not game_over:
        all_sprites.update()

        # Bullet-enemy collision
        for bullet in bullets:
            enemy_hits = pygame.sprite.spritecollide(bullet, enemies, True)
            if enemy_hits:
                bullet.kill()
                score += 10

        # Player-enemy collision
        enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
        if enemy_hits:
            player.health -= 1
            if player.health <= 0:
                player.lives -= 1
                player.health = 100
            if player.lives <= 0:
                game_over = True

        # Player-collectible collision
        collectible_hits = pygame.sprite.spritecollide(player, collectibles, True)
        if collectible_hits:
            player.health += 10
            if player.health > 100:
                player.health = 100

        # Level up after a certain score threshold
        if score >= 100 * level:
            level += 1

    # Update camera to follow the player
    camera.update(player)

    # Render all sprites with camera offset
    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))

    display_info()

    if game_over:
        game_over_text = font.render("Game Over! Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH//4, SCREEN_HEIGHT//2))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:  # Restart on pressing 'R'
            game_over = False
            player.lives = 3
            player.health = 100
            score = 0
            level = 1

    pygame.display.flip()

pygame.quit()
