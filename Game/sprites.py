import pygame


def load_tiles(filename, grid_width, grid_height, gap_size):
    # Load the image
    image = pygame.image.load(filename)

    # Calculate the size of each sprite
    total_width, total_height = image.get_size()
    sprite_width = (total_width - (grid_width - 1) * gap_size) // grid_width
    sprite_height = (total_height - (grid_height - 1) * gap_size) // grid_height

    # Create a 1D list to hold the sprites
    sprites = [None for _ in range(grid_width * grid_height)]

    # Extract each sprite
    for i in range(grid_height):
        for j in range(grid_width):
            x = j * (sprite_width + gap_size)
            y = i * (sprite_height + gap_size)
            sprite_rect = pygame.Rect(x, y, sprite_width, sprite_height)
            sprites[i * grid_width + j] = image.subsurface(sprite_rect)
            # shrink sprites by half
            sprites[i * grid_width + j] = pygame.transform.scale(sprites[i * grid_width + j], (sprite_width // 2, sprite_height // 2))

    return sprites


TILES = load_tiles("Game/tiles.png", 11, 10, 8)
TILE_SIZE = 32
