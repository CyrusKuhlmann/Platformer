import pygame
from sprites import TILES, TILE_SIZE
import numpy as np

BLACK = (0, 0, 0)
SKY_BLUE = (130, 186, 223)


class Grid:
    def __init__(self, rows=12, cols=16, bg_color=BLACK):
        self.rows = rows
        self.cols = cols
        self.bg_color = bg_color
        self.grid = np.full((rows, cols), -1)

    @property
    def width(self):
        return self.cols * TILE_SIZE

    @property
    def height(self):
        return self.rows * TILE_SIZE

    def tiles(self):
        objects = []
        for i, row in enumerate(self.grid):
            for j, tile_index in enumerate(row):
                if tile_index >= 0:
                    objects.append(
                        pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE,
                                    TILE_SIZE))
        return objects

    def draw(self, screen, offset_x=0):
        screen.fill(self.bg_color)
        for i, row in enumerate(self.grid):
            for j, tile_index in enumerate(row):
                if tile_index >= 0:
                    x = j * TILE_SIZE - offset_x  # Apply the x-offset for panning
                    y = i * TILE_SIZE
                    screen.blit(TILES[tile_index], (x, y))

    def get_tile_index(self, pos):
        return pos[1] // 64, pos[0] // 64

    def get_tile(self, x, y):
        r, c = self.get_tile_index((x, y))
        return self.grid[r][c]
