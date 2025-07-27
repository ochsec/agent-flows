import pygame
import sys
from bird import Bird
from pipe import Pipe
from game import Game

game = None

def main():
    global game
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if game.state in ["MENU", "GAME_OVER"]:
                    if game.state == "MENU":
                        game.start()
                    elif game.state == "GAME_OVER":
                        game.restart()
                else:
                    game.bird.jump()

        screen.fill((135, 206, 235))
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()