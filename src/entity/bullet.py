import pygame

from config import BULLET_COLOR, BULLET_SIZE, BULLET_SPEED

class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
        self.speed = BULLET_SPEED 
        self.color = BULLET_COLOR 

        self.direction = pygame.math.Vector2(target_x - x, target_y - y)
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        else:
            self.direction = pygame.math.Vector2(1, 0)

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        self.rect.centery = round(self.pos.y)

    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.ellipse(surface, self.color, offset_rect)
