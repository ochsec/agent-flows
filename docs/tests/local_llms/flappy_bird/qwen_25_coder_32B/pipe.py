import pygame
import random

class Pipe:
    GAP = 150
    WIDTH = 70
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = Pipe.GAP
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.Surface((Pipe.WIDTH, 600))
        self.PIPE_BOTTOM = pygame.Surface((Pipe.WIDTH, 600))
        self.PIPE_TOP.fill((34, 139, 34))
        self.PIPE_BOTTOM.fill((34, 139, 34))
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= Pipe.VEL

    def draw(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.top))
        screen.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = pygame.mask.from_surface(bird.image)
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True

        return False