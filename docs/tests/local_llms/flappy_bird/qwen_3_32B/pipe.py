import pygame
import random
class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 70
        self.gap = 150
        self.top_height = random.randint(50, 400)
        self.passed = False
        self.speed = 2

    def update(self):
        self.x -= self.speed
        if self.x + self.width < 0:
            self.reset()

    def reset(self):
        self.x = 800
        self.top_height = random.randint(50, 400)
        self.passed = False

    def draw(self, screen):
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_rect = pygame.Rect(
            self.x,
            self.top_height + self.gap,
            self.width,
            600 - (self.top_height + self.gap)
        )
        pygame.draw.rect(screen, (34, 139, 34), top_rect)
        pygame.draw.rect(screen, (34, 139, 34), bottom_rect)

    @property
    def rect_top(self):
        return pygame.Rect(self.x, 0, self.width, self.top_height)

    @property
    def rect_bottom(self):
        return pygame.Rect(
            self.x,
            self.top_height + self.gap,
            self.width,
            600 - (self.top_height + self.gap)
        )