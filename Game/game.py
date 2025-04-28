import pygame
import time
import numpy as np
import heapq
from grid import Grid, SKY_BLUE

def detect_collisions(rect, objects):
    collisions = []
    for obj in objects:
        if rect.colliderect(obj):
            collisions.append(obj)
    return collisions


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.original_image = pygame.image.load("Game/bullet.png").convert_alpha()  # Load the original bullet image
        self.image = pygame.transform.scale(self.original_image, (50, 50))  # Scale the image
        if speed < 0:  # Flip the image if the bullet is moving left
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

class Player:
    def __init__(self, level):
        self.stand = pygame.image.load("Game/platformerheropack/medium/soldier/soldier0000.png")
        self.run = [pygame.image.load(f"Game/platformerheropack/medium/soldier/soldier00{i:02}.png") for i in range(8, 16)]
        self.jump_up = [pygame.image.load(f"Game/platformerheropack/medium/soldier/soldier00{i:02}.png") for i in range(32, 37)]
        self.jump_down = [pygame.image.load(f"Game/platformerheropack/medium/soldier/soldier00{i:02}.png") for i in [37, 38, 39, 40, 39, 38, 37]]
        self.landing_speed = 0
        self.frame = 1
        self.jump_frame = 0
        self.jump_down_frame = 0
        self.width = 115
        self.height = 77
        self.direction = "right"
        self.speed = [0, 0]
        self.rect = pygame.Rect(0, 768 - 64 - 90, 30, 63)
        self.can_jump = False
        self.level = level
        self.ground = -1
        self.touched_block_types = set()
        self.bullets = pygame.sprite.Group()  # Group to hold bullets
        self.traveled = 0
        self.clock = 0
        self.diamonds = 0
        self.slip_time = 0
    def set_enemy(self, enemy):
        self.enemy = enemy

    def draw(self, screen): 
        self.clock += 1
        if self.speed[0] == 0:
            frame = self.stand
        else:
            frame = self.run[self.frame]
        if self.can_jump == False:
            self.landing_speed = self.speed[1]
            if self.jump_frame < len(self.jump_up):  # Play jump animation frames
                frame = self.jump_up[self.jump_frame]
                if self.clock % 6 == 0:
                    self.jump_frame += 1
            else:  # Hold the last frame of the jump animation
                frame = self.jump_up[len(self.jump_up) - 1]
        elif self.jump_frame > 0:
            if self.jump_down_frame < len(self.jump_down) and self.landing_speed > 5:
                frame = self.jump_down[self.jump_down_frame]
                if self.clock % 2 == 0:
                    self.jump_down_frame += 1
            else:
                self.jump_frame = 0  # Reset jump frame when not jumping
                self.jump_down_frame = 0  # Reset jump down frame when not jumping
        image = pygame.transform.scale(frame, (self.width, self.height))
        flipped_image = pygame.transform.flip(image, True, False)

        if self.direction == "right":
            screen.blit(image, self.drawbox())
        else:
            screen.blit(flipped_image, self.drawbox())

        # Draw bullets
        for bullet in self.bullets:
            screen.blit(bullet.image, bullet.rect)

    def drawbox(self):
        return pygame.Rect(
            self.rect.x - 40,
            self.rect.y - 15,
            self.width,
            self.height,
        )

    def move(self):
        objects = self.level.tiles()

        # Check for bullet collisions with tiles
        for bullet in self.bullets:
            bullet.rect.x += bullet.speed
            collisions = detect_collisions(bullet.rect, objects)
            for tile in collisions:
                if bullet.speed > 0:
                    bullet.rect.right = tile.left
                if bullet.speed < 0:
                    bullet.rect.left = tile.right
                bullet.kill()

        # Apply gravity
        self.speed[1] += 0.15

 # Check left-right collisions
        self.rect.x += self.speed[0]
        collisions = detect_collisions(self.rect, objects)
        for tile in collisions:
            if self.speed[0] > 0:
                self.rect.right = tile.left
            if self.speed[0] < 0:
                self.rect.left = tile.right

            tile_id = self.level.get_tile(tile.x, tile.y)
            # Check if this block type (1 or 2) has been touched before
            if tile_id in {1, 2} and tile_id not in self.touched_block_types:
                self.touched_block_types.add(tile_id)  # Mark block type as touched
                if tile_id == 1:
                    self.level.grid = np.load("Game/level0.npy")
                    self.enemy = Enemy(self.level, self)
                    self.enemy.path = []
                    self.enemy.rect = pygame.Rect(210, 768 - 64 - 90, 57, 63)
                if tile_id == 2:
                    self.level.grid = np.load("Game/level2.npy")
                    self.enemy = Enemy(self.level, self)
                    self.enemy.path = []
                    self.enemy.rect = pygame.Rect(1024 - 65, 0, 57, 63)
                    
            if tile_id == 105:
                self.level.grid = np.load("Game/gameover.npy")

            if tile_id == 96:
                self.diamonds += 1
                self.level.grid[tile.y // 64][tile.x // 64] = -1



        # Check up-down collisions
        self.rect.y += self.speed[1]
        collisions = detect_collisions(self.rect, objects)
        for tile in collisions:
            if self.speed[1] > 0:
                self.rect.bottom = tile.top
                self.speed[1] = 0
                self.can_jump = True
                self.ground = self.rect.y
            if self.speed[1] < 0:
                self.rect.top = tile.bottom
                self.speed[1] = 0

            tile_id = self.level.get_tile(tile.x, tile.y)
            # Check if this block type (1 or 2) has been touched before
            if tile_id in {1, 2} and tile_id not in self.touched_block_types:
                self.touched_block_types.add(tile_id)  # Mark block type as touched
                if tile_id == 1:
                    self.level.grid = np.load("Game/level0.npy")
                    self.enemy.path = []
                    self.enemy.rect = pygame.Rect(210, 768 - 64 - 90, 57, 63)
                elif tile_id == 2:
                    self.level.grid = np.load("Game/level2.npy")
                    self.enemy.path = []
                    self.enemy.rect = pygame.Rect(1024 - 65, 0, 57, 63)

            if tile_id == 105:
                self.level.grid = np.load("Game/gameover.npy")

            if tile_id == 96:
                self.diamonds += 1
                self.level.grid[tile.y // 64][tile.x // 64] = -1

        if self.can_jump and self.rect.y != self.ground:
            self.can_jump = False

        # Keep player on screen
        if self.rect.right > self.level.width:
            self.rect.right = self.level.width
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.speed[1] = 0
            self.rect.top = 0
        if self.rect.bottom > self.level.height:
            self.rect.bottom = self.level.height

        # Update animation frame
        if self.speed[0] == 0 and self.speed[1] == 0:
            self.frame = 1
            self.traveled = 0
        else:
            self.traveled += abs(self.speed[0]) + abs(self.speed[1])
            if self.traveled >= 10:  # Change frame every 10 pixels traveled
                self.traveled = 0
                self.frame = (self.frame + 1) % len(self.run)

class Enemy:
    def __init__(self, level, player):
        bigplayer = pygame.image.load("Game/Ghost.png")
        self.width = 90
        self.height = 71.43
        self.direction = "right"
        self.image = pygame.transform.scale(bigplayer, (self.width, self.height))
        self.flipped_image = pygame.transform.flip(self.image, True, False)
        self.red_image = pygame.transform.scale(bigplayer, (self.width, self.height))
        self.red_image.fill((255, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.flipped_red_image = pygame.transform.flip(self.red_image, True, False)
        self.speed = [0, 0]
        self.rect = pygame.Rect(300, 768 - 64 - 90, 57, 63)
        self.can_jump = False
        self.level = level
        self.player = player
        self.path = []  # Store the path to be visualized
        self.health = 10  # Health points for the enemy
        self.hit_timer = 0

    def draw(self, screen):
        if pygame.time.get_ticks() - self.hit_timer < 100 and self.health > 0:  # 100 ms = 0.1 seconds
            if self.direction == "right":
                screen.blit(self.red_image, self.drawbox())
            else:
                flipped_red_image = pygame.transform.flip(self.red_image, True, False)
                screen.blit(flipped_red_image, self.drawbox())
        elif self.health > 0:
            if self.direction == "right":
                screen.blit(self.image, self.drawbox())
            else:
                screen.blit(self.flipped_image, self.drawbox())

        # # Draw path visualization
        # for step in self.path:
        #     x, y = step[1] * 64, step[0] * 64
        #     pygame.draw.rect(screen, (255, 0, 0), (x, y, 64, 64), 3)

    def drawbox(self):
        return pygame.Rect(
            self.rect.x - 15,
            self.rect.y - 15,
            self.width,
            self.height,
        )

    def a_star_path(self, start, goal):
        if start == goal:
            return [goal]
        """A* pathfinding for tiles with ID -1 only."""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path  # Return path from start to goal

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Up, Down, Left, Right
                neighbor = (current[0] + dx, current[1] + dy)

                # Check if neighbor is within grid bounds
                if 0 <= neighbor[0] < self.level.rows and 0 <= neighbor[1] < self.level.cols:
                    tile_id = self.level.get_tile(neighbor[1] * 64, neighbor[0] * 64)

                    if tile_id == -1:  # Only passable tiles with ID -1
                        tentative_g_score = g_score[current] + 1

                        if tentative_g_score < g_score.get(neighbor, float("inf")):
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                            heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []  # Return empty path if no path is found


    def move(self, player):
        start = self.level.get_tile_index((self.rect.x, self.rect.y))
        goal = self.level.get_tile_index((player.rect.x, player.rect.y))
        self.path = self.a_star_path(start, goal)

        if self.path:
            # Move smoothly along the path toward the next tile
            next_step = self.path[0]
            next_x, next_y = next_step[1] * 64 + 32, next_step[0] * 64 + 32

            if abs(next_x - self.rect.centerx) > 1:
                self.speed[0] = 1.5 if next_x > self.rect.centerx else -1.5
            else:
                self.speed[0] = 0

            if abs(next_y - self.rect.centery) > 1:
                self.speed[1] = 1.5 if next_y > self.rect.centery else -1.5
            else:
                self.speed[1] = 0

            # Apply the speed to move toward the next tile smoothly
            self.rect.x += int(self.speed[0])
            self.rect.y += int(self.speed[1])

            # If we reach the center of the next step, remove it from the path
            if self.rect.collidepoint(next_x, next_y):
                self.path.pop(0)


        # Handle collisions with player
        if self.rect.colliderect(player.rect):
            player.level.grid = np.load("Game/gameover.npy")
            player.rect = pygame.Rect(0, 768 - 64 - 90, 57, 63)
            player.direction = "right"


def main():
    pygame.init()
    level = Grid(bg_color=SKY_BLUE)
    level.grid = np.load("Game/level1.npy")
    screen = pygame.display.set_mode((level.width, level.height))
    clock = pygame.time.Clock()
    player = Player(level)
    player.enemy = Enemy(level, player)
    font = pygame.font.Font(None, 36)  # Font for diamond count
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_UP
                and player.can_jump
            ):
                player.speed[1] = -6.3
                player.can_jump = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet_speed = 5 if player.direction == "right" else -5
                    bullet = Bullet(player.rect.centerx, player.rect.centery, bullet_speed)
                    player.bullets.add(bullet)  # Add the bullet to the bullets group
            if player.enemy and player.enemy.health <= 0:
                player.enemy = None
                player.set_enemy(None)
                break
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            player.direction = "right"
            player.speed[0] = 2.7

        elif keys[pygame.K_LEFT]:
            player.direction = "left"
            player.speed[0] = -2.7

        else:
            player.speed[0] = 0


        level.draw(screen)
        player.draw(screen)
        if player.enemy:
            # Draw the enemy only if it exists
            player.enemy.draw(screen)


        #check for bullet collisions with the enemy
        for bullet in player.bullets:
            if player.enemy and bullet.rect.colliderect(player.enemy.rect):  # Check if bullet hits the enemy
                player.enemy.health -= 1  # Decrease enemy health
                player.enemy.hit_timer = pygame.time.get_ticks()
                bullet.kill()  # Remove the bullet


                # Render the diamond count text
        diamond_text = font.render(f"Diamonds: {player.diamonds}", True, (0, 0, 0))  # White text
        text_rect = diamond_text.get_rect(topright=(level.width - 10, 10))  # Position in the upper-right corner
        screen.blit(diamond_text, text_rect)
        player.move()
        if player.enemy:
            player.enemy.move(player)
        pygame.display.flip()
        clock.tick(60)


    pygame.quit()

if __name__ == "__main__":
    main()
