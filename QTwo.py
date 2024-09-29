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