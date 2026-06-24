import math
import pygame

import config as cfg


class BossArena:
    def __init__(self, world):  
        self.world = world 
        self.center_x = cfg.MAP_WIDTH // 2
        self.center_y = cfg.MAP_HEIGHT // 2
        self.arena_radius = min(cfg.MAP_WIDTH, cfg.MAP_HEIGHT) // 2 - 2

    def create_arena(self):
        self.world.matrix = [[1 for _ in range(cfg.MAP_WIDTH)] for _ in range(cfg.MAP_HEIGHT)]

        for y in range(cfg.MAP_HEIGHT):
            for x in range(cfg.MAP_WIDTH):
                dx = x - self.center_x
                dy = y - self.center_y
                if math.hypot(dx, dy) < self.arena_radius:
                    self.world.matrix[y][x] = 0

        column_tile_offsets = [(-4, -3), (4, -3), (-4, 3), (4, 3)]
        for ox, oy in column_tile_offsets:
            cx = self.center_x + ox
            cy = self.center_y + oy
            
            if 0 <= cy < cfg.MAP_HEIGHT - 1 and 0 <= cx < cfg.MAP_WIDTH - 1:
                self.world.matrix[cy][cx] = 1
                self.world.matrix[cy][cx+1] = 1
                self.world.matrix[cy+1][cx] = 1
                self.world.matrix[cy+1][cx+1] = 1

        for y in range(cfg.MAP_HEIGHT):
            for x in range(cfg.MAP_WIDTH):
                if self.world.matrix[y][x] == 1:
                    is_visible_wall = False
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < cfg.MAP_HEIGHT and 0 <= nx < cfg.MAP_WIDTH:
                            if self.world.matrix[ny][nx] == 0:
                                is_visible_wall = True
                                break
                    if is_visible_wall:
                        rect = pygame.Rect(x * cfg.TILE_SIZE, y * cfg.TILE_SIZE, cfg.TILE_SIZE, cfg.TILE_SIZE)
                        self.world.walls.append(rect)