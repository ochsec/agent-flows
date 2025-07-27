import pygame

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.gravity = 0.5
        self.rect = pygame.Rect(x, y, 30, 30)

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.y = int(self.y)
        
        # Prevent falling through bottom
        if self.rect.bottom >= 600:
            self.rect.bottom = 600
            self.velocity = 0

    def jump(self):
        self.velocity = -8

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), self.rect.center, 15)