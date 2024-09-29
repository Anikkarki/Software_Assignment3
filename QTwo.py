import pygame
pygame.init()

# Player class with movement, jumping, shooting
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 300
        self.speed = 5
        self.jump_power = -10
        self.health = 100
        self.lives = 3

   def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_SPACE]:
            self.jump()
    
    def jump(self):
        self.rect.y += self.jump_power