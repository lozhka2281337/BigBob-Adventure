import pygame

from config import HEALTH_PACK_COLOR, HEALTH_PACK_SIZE, WHITE

class HealthPack:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, HEALTH_PACK_SIZE, HEALTH_PACK_SIZE)
        self.color = HEALTH_PACK_COLOR

    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.rect(surface, self.color, offset_rect)
        pygame.draw.line(surface, WHITE, (offset_rect.centerx, offset_rect.top+4), (offset_rect.centerx, offset_rect.bottom-4), 3)
        pygame.draw.line(surface, WHITE, (offset_rect.left+4, offset_rect.centery), (offset_rect.right-4, offset_rect.centery), 3)
