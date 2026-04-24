import pygame
import math

from .bullet import Bullet
from .weapon import Weapon

from config import PLAYER_SPEED, PLAYER_HP, PLAYER_SIZE, PLAYER_COLOR

class Player:
    def __init__(self, x: int, y: int):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.color = PLAYER_COLOR
        self.hp = PLAYER_HP

        self.invulnerable_timer = 0 # таймер для щита бессмертия, появляющийся после получения урона

        self.gun = Weapon(50, 20, 4, 5)

    def shot(self, camera_x: int, camera_y: int) -> Bullet:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        world_mouse_x = mouse_x + camera_x
        world_mouse_y = mouse_y + camera_y

        return Bullet(self.pos.x + 16, self.pos.y + 16, world_mouse_x, world_mouse_y)
        
    def get_damage(self):
        if self.invulnerable_timer <= 0: 
            self.hp -= 1
            self.invulnerable_timer = 3.0

    def movement(self, direction: pygame.math.Vector2, dt: float, walls: list):
        """ двигаем игрока:
        1) нормализация
        2) двигаем по x - проверяем на коллизии
        3) двигаем по y - проверяем на коллизии  
        """

        if direction.magnitude() > 0:
            direction = direction.normalize()

        self.pos.x += direction.x * self.speed * dt
        self.rect.x = int(self.pos.x)

        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.x > 0: self.rect.right = wall.left
                elif direction.x < 0: self.rect.left = wall.right
                self.pos.x = float(self.rect.x) 

        self.pos.y += direction.y * self.speed * dt
        self.rect.y = int(self.pos.y) 

        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.y > 0: self.rect.bottom = wall.top
                elif direction.y < 0: self.rect.top = wall.bottom         
                self.pos.y = float(self.rect.y)

    def update(self, dt: float, walls: list): 
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]: direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: direction.x += 1

        self.movement(direction, dt, walls)

        # обновление таймера для щита бессмертия
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt


    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        screen_x = float(self.pos.x - cam_x)
        screen_y = float(self.pos.y - cam_y)
        
        pygame.draw.rect(surface, self.color, (screen_x, screen_y, self.rect.width, self.rect.height))
        pygame.draw.rect(surface, (0, 0, 0), (screen_x + 6, screen_y + 8, 6, 6))
        pygame.draw.rect(surface, (0, 0, 0), (screen_x + 20, screen_y + 8, 6, 6))

        if self.invulnerable_timer > 0: self.draw_shield(surface, screen_x, screen_y)

    def draw_shield(self, surface: pygame.Surface, screen_x: float, screen_y: float):
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 5  
        radius = 40 + int(pulse)
        pygame.draw.circle(surface, (0, 255, 150), (screen_x + 16, screen_y + 16), radius, 3)
        pygame.draw.circle(surface, (0, 255, 150), (screen_x + 16, screen_y + 16), radius + 4, 1)
