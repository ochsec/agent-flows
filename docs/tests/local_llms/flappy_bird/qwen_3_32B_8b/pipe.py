import pygame
import random
class Pipe:
    WIDTH = 70
    GAP = 150
    SPEED = 3

    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, 400)
        self.passed = False
        
    def update(self):
        self.x -= self.SPEED

    def get_top_rect(self):
        return pygame.Rect(self.x, 0, self.WIDTH, self.height)

    def get_bottom_rect(self):
        bottom_y = self.height + self.GAP
        return pygame.Rect(self.x, bottom_y, self.WIDTH, 600 - bottom_y)

    def off_screen(self):
        return self.x < -self.WIDTH