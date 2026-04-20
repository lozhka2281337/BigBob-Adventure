import pygame
import random

class Enemy:
    def __init__(self, x, y, enemy_type="normal"):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, 32, 32)
        
        if enemy_type == "scout": 
            self.speed = 250
            self.color = (255, 255, 0)
        else: 
            self.speed = 150
            self.color = (255, 50, 50)

        self.state = "wander"
        self.wander_dir = pygame.math.Vector2(0, 0)
        self.timer = 0

    def check_los(self, target_rect, walls):
        line = (self.rect.center, target_rect.center)
        for wall in walls:
            if wall.clipline(line):
                return False
        return True 

    def update(self, dt, player, walls): 
        sees_player = self.check_los(player.rect, walls)
        self.timer -= dt

        if sees_player:
            self.state = "chase"
            direction = pygame.math.Vector2(player.rect.centerx - self.rect.centerx, 
                                            player.rect.centery - self.rect.centery)
        else:
            self.state = "wander"
            if self.timer <= 0:
                self.timer = random.uniform(1.0, 2.5) 
                self.wander_dir = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            
            direction = self.wander_dir

        if direction.magnitude() > 0:
            direction = direction.normalize()

        self.pos.x += direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.x > 0: self.rect.right = wall.left
                elif direction.x < 0: self.rect.left = wall.right
                self.pos.x = self.rect.x
                if not sees_player: self.timer = 0 

        self.pos.y += direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)
        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.y > 0: self.rect.bottom = wall.top
                elif direction.y < 0: self.rect.top = wall.bottom
                self.pos.y = self.rect.y
                if not sees_player: self.timer = 0
                
    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.rect(surface, self.color, offset_rect)
