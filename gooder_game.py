
import pygame
import math
import sys

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 800, 600
HALF_HEIGHT = HEIGHT // 2
FOV = math.pi / 3
NUM_RAYS = 200
MAX_DEPTH = 600
DELTA_ANGLE = FOV / NUM_RAYS
SCALE = WIDTH // NUM_RAYS
PLAYER_SPEED = 2.5
ROT_SPEED = 0.04

WORLD_MAP = [
    "111111111111",
    "1..........1",
    "1..11......1",
    "1..........1",
    "1......11..1",
    "1..........1",
    "111111111111",
]

TILE = 64
MAP_W = len(WORLD_MAP[0]) * TILE
MAP_H = len(WORLD_MAP) * TILE

# ---------------- INIT ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

px, py = TILE * 2, TILE * 2
pa = 0


def tile_at(x, y):
    if x < 0 or y < 0 or x >= MAP_W or y >= MAP_H:
        return "1"
    return WORLD_MAP[int(y // TILE)][int(x // TILE)]


def move(dx, dy):
    global px, py
    nx, ny = px + dx, py + dy
    if tile_at(nx, py) == ".":
        px = nx
    if tile_at(px, ny) == ".":
        py = ny


def draw_floor_ceiling():
    pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, HALF_HEIGHT))
    pygame.draw.rect(screen, (70, 70, 70), (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))


def raycast():
    start_angle = pa - FOV / 2
    angle = start_angle

    for ray in range(NUM_RAYS):
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        for depth in range(1, MAX_DEPTH, 2):
            tx = px + depth * cos_a
            ty = py + depth * sin_a

            if tile_at(tx, ty) == "1":
                depth *= math.cos(pa - angle)
                wall_h = min(HEIGHT, (TILE * 300) / (depth + 0.0001))

                shade = 255 / (1 + depth * depth * 0.00001)
                color = (shade, shade, shade)

                pygame.draw.rect(
                    screen,
                    color,
                    (ray * SCALE, HALF_HEIGHT - wall_h // 2, SCALE, wall_h)
                )
                break

        angle += DELTA_ANGLE


def handle_input():
    global pa
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        pa -= ROT_SPEED
    if keys[pygame.K_RIGHT]:
        pa += ROT_SPEED

    sin_a = math.sin(pa)
    cos_a = math.cos(pa)

    if keys[pygame.K_w]:
        move(cos_a * PLAYER_SPEED, sin_a * PLAYER_SPEED)
    if keys[pygame.K_s]:
        move(-cos_a * PLAYER_SPEED, -sin_a * PLAYER_SPEED)
    if keys[pygame.K_a]:
        move(sin_a * PLAYER_SPEED, -cos_a * PLAYER_SPEED)
    if keys[pygame.K_d]:
        move(-sin_a * PLAYER_SPEED, cos_a * PLAYER_SPEED)


def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        handle_input()
        draw_floor_ceiling()
        raycast()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
