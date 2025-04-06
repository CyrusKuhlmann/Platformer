import os
import pygame
import numpy as np
from sprites import TILES
from grid import Grid, SKY_BLUE

PICK_TILE = 1
DRAW_LEVEL = 2


def main(filename):
    pygame.init()
    level = Grid(bg_color=SKY_BLUE)
    if os.path.exists(filename):
      level.grid = np.load(filename, allow_pickle = True)
    picker = Grid()
    picker.grid.flat[:len(TILES)] = np.arange(len(TILES))

    screen = pygame.display.set_mode((level.width, level.height))
    clock = pygame.time.Clock()

    running = True
    current_tile = 47
    mode = DRAW_LEVEL
    level.draw(screen)
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif mode == PICK_TILE:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    print(screen.get_at(event.pos))
                    r, c = level.get_tile_index(event.pos)
                    current_tile = picker.grid[r][c]
                    mode = DRAW_LEVEL
            elif mode == DRAW_LEVEL:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    r, c = level.get_tile_index(event.pos)
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        level.grid[r][c] = -1
                    else:
                        level.grid[r][c] = current_tile
                    np.save(filename, level.grid)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    mode = PICK_TILE
            else:
                raise Exception("Invalid mode")

        if mode == DRAW_LEVEL:
            level.draw(screen)
        elif mode == PICK_TILE:
            picker.draw(screen)
        else:
            raise Exception("Invalid mode")
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
