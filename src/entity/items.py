import pygame

from config import HEALTH_PACK_COLOR, HEALTH_PACK_SIZE, WHITE

import pygame
import math
import config as cfg

class HealthPack:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, cfg.TILE_SIZE // 2, cfg.TILE_SIZE // 2)
        self.animation_timer = 0.0

    def update(self, dt):
        self.animation_timer = (self.animation_timer + 5*dt) % (2 * math.pi)

    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pulse = math.sin(self.animation_timer) * 3

        pygame.draw.rect(surface, (15, 22, 28), offset_rect)
        
        glow_rect = offset_rect.inflate(4 + pulse, 4 + pulse)
        pygame.draw.rect(surface, cfg.COLOR_NEON_GREEN, glow_rect, 1)
        pygame.draw.rect(surface, cfg.COLOR_NEON_GREEN, offset_rect, 2)

        cx, cy = offset_rect.centerx, offset_rect.centery
        pygame.draw.rect(surface, (255, 255, 255), (cx - 1, cy - 5, 3, 11))
        pygame.draw.rect(surface, (255, 255, 255), (cx - 5, cy - 1, 11, 3))
