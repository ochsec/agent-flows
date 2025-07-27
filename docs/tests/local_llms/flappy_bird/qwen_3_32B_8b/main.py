import pygame
import sys
from bird import Bird
from pipe import Pipe
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Flappy Bird')
    clock = pygame.time.Clock()

    game = Game(screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game.handle_space_key()

        screen.fill((135, 206, 235))  # Sky blue background
        game.update()
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()