import pygame
from bird import Bird
from pipe import Pipe
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = 'menu'  # menu | playing | game_over
        self.bird = Bird(100, 300)
        self.pipes = [Pipe(600), Pipe(1000)]
        self.score = 0
        
    def handle_space_key(self):
        if self.state == 'menu':
            self.state = 'playing'
            pygame.time.set_timer(pygame.USEREVENT, 1500)  # Pipe generation timer
        elif self.state == 'playing':
            self.bird.jump()
        elif self.state == 'game_over':
            self.__init__(self.screen)

    def update(self):
        if self.state == 'menu':
            self._draw_menu()
            return

        # Update game objects
        self.bird.update()
        
        for pipe in self.pipes:
            pipe.update()

        # Add new pipes and remove old ones
        if pygame.time.get_ticks() % 1500 == 0:
            self.pipes.append(Pipe(800))

        self.pipes = [pipe for pipe in self.pipes if not pipe.off_screen()]

        # Collision detection
        for pipe in self.pipes:
            if (self.bird.get_rect().colliderect(pipe.get_top_rect()) or
                self.bird.get_rect().colliderect(pipe.get_bottom_rect())):
                self.state = 'game_over'

        # Check if bird hits top/bottom of screen
        if self.bird.y > 600 or self.bird.y < 0:
            self.state = 'game_over'

        # Score update
        for pipe in self.pipes:
            if not pipe.passed and pipe.x < self.bird.x:
                pipe.passed = True
                self.score += 1

        # Draw everything
        if self.state == 'playing':
            self._draw_game()
        else:  # game_over
            self._draw_game_over()

    def _draw_menu(self):
        font = pygame.font.SysFont('Arial', 48)
        title = font.render('Flappy Bird', True, (255, 255, 255))
        instruction = pygame.font.SysFont('Arial', 24).render(
            'Press SPACE to start', True, (255, 255, 255)
        )
        self.screen.blit(title, (300, 250))
        self.screen.blit(instruction, (300, 350))

    def _draw_game(self):
        # Draw bird
        pygame.draw.circle(
            self.screen, (255, 255, 0), 
            (int(self.bird.x), int(self.bird.y)), self.bird.radius
        )

        # Draw pipes
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, (0, 255, 0), pipe.get_top_rect())
            pygame.draw.rect(self.screen, (0, 255, 0), pipe.get_bottom_rect())

        # Draw score
        font = pygame.font.SysFont('Arial', 32)
        text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

    def _draw_game_over(self):
        self._draw_game()
        font = pygame.font.SysFont('Arial', 48)
        text = font.render(f'Game Over! Score: {self.score}', True, (255, 0, 0))
        self.screen.blit(text, (200, 250))