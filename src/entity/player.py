import pygame

from config import PLAYER_SPEED, PLAYER_HP, PLAYER_SIZE, PLAYER_COLOR

class Player:
    def __init__(self, x: int, y: int):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.color = PLAYER_COLOR
        self.health = PLAYER_HP

    def update(self, dt: int, walls: list):
        # отслеживание клавиш 
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]: direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: direction.x += 1

        # двигаем игрока
        if direction.magnitude() > 0:
            direction = direction.normalize()

        self.pos.x += direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)

        # обработка коллизий
        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.x > 0: self.rect.right = wall.left
                elif direction.x < 0: self.rect.left = wall.right
                self.pos.x = self.rect.x 

        self.pos.y += direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)
        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.y > 0: self.rect.bottom = wall.top
                elif direction.y < 0: self.rect.top = wall.bottom
                self.pos.y = self.rect.y 

    def draw(self, surface, cam_x: int, cam_y: int):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.rect(surface, self.color, offset_rect)
        pygame.draw.rect(surface, (0, 0, 0), (offset_rect.x + 6, offset_rect.y + 8, 6, 6))
        pygame.draw.rect(surface, (0, 0, 0), (offset_rect.x + 20, offset_rect.y + 8, 6, 6))
