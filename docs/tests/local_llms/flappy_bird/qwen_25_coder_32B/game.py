import pygame
from bird import Bird
from pipe import Pipe

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.bird = Bird(100, 300)
        self.pipes = [Pipe(700)]
        self.score = 0
        self.state = 'menu'

    def update(self):
        if self.state == 'playing':
            self.bird.update()
            for pipe in self.pipes:
                pipe.move()
                if pipe.collide(self.bird):
                    self.state = 'game_over'
                if not pipe.passed and pipe.x < self.bird.x:
                    pipe.passed = True
                    self.score += 1
                if pipe.x + Pipe.WIDTH < 0:
                    self.pipes.remove(pipe)
            if len(self.pipes) == 0 or self.pipes[-1].x < 500:
                self.pipes.append(Pipe(700))
            if self.bird.y + 30 >= 600 or self.bird.y < 0:
                self.state = 'game_over'

    def draw(self):
        if self.state == 'menu':
            font = pygame.font.Font(None, 74)
            text = font.render('Flappy Bird', True, (0, 0, 0))
            self.screen.blit(text, (350 - text.get_width() // 2, 150))
        elif self.state == 'playing':
            self.bird.draw(self.screen)
            for pipe in self.pipes:
                pipe.draw(self.screen)
            font = pygame.font.Font(None, 36)
            text = font.render(f'Score: {self.score}', True, (0, 0, 0))
            self.screen.blit(text, (10, 10))
        elif self.state == 'game_over':
            font = pygame.font.Font(None, 74)
            text = font.render('Game Over', True, (0, 0, 0))
            self.screen.blit(text, (400 - text.get_width() // 2, 150))
            font = pygame.font.Font(None, 36)
            text = font.render(f'Score: {self.score}', True, (0, 0, 0))
            self.screen.blit(text, (400 - text.get_width() // 2, 300))

    def start(self):
        self.state = 'playing'
        self.bird = Bird(100, 300)
        self.pipes = [Pipe(700)]
        self.score = 0