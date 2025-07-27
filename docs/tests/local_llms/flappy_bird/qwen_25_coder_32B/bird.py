import pygame

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.gravity = 0.5
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 255, 0))
        self.rect = pygame.Rect(self.x, self.y, 30, 30)

    def jump(self):
        self.velocity = -8

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)