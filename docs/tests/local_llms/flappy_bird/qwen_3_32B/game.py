import pygame
from bird import Bird
from pipe import Pipe
class Game:
    def __init__(self):
        self.state = "MENU"
        self.bird = Bird(100, 300)
        self.pipes = [Pipe(400), Pipe(650)]
        self.score = 0
        self.font = pygame.font.Font(None, 36)

    def start(self):
        self.state = "PLAYING"
        self.bird = Bird(100, 300)
        self.pipes = [Pipe(400), Pipe(650)]
        self.score = 0

    def restart(self):
        self.start()

    def update(self):
        if self.state == "PLAYING":
            self.bird.update()
            for pipe in self.pipes:
                pipe.update()

            # Collision detection
            for pipe in self.pipes:
                if (self.bird.rect.colliderect(pipe.rect_top) or 
                    self.bird.rect.colliderect(pipe.rect_bottom)):
                    self.state = "GAME_OVER"
                    return

            # Boundary check
            if self.bird.rect.top < 0 or self.bird.rect.bottom >= 600:
                self.state = "GAME_OVER"

            # Score update
            for pipe in self.pipes:
                if not pipe.passed and self.bird.rect.x > pipe.x + pipe.width:
                    self.score += 1
                    pipe.passed = True

    def draw(self, screen):
        self.bird.draw(screen)
        for pipe in self.pipes:
            pipe.draw(screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))