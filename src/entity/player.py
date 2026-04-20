import pygame

from config import PLAYER_SPEED, PLAYER_HP, PLAYER_SIZE, PLAYER_COLOR

class Player:
    def __init__(self, x: int, y: int):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.color = PLAYER_COLOR
        self.health = PLAYER_HP
        self.invulnerable_timer = 0

    def update(self, dt: float, walls: list): 
        
        # добавил таймер для щита 
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

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
        self.rect.x = int(self.pos.x) # измененил round на git для х

        # обработка коллизий
        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.x > 0: self.rect.right = wall.left
                elif direction.x < 0: self.rect.left = wall.right
                self.pos.x = self.rect.x 

        self.pos.y += direction.y * self.speed * dt
        self.rect.y = int(self.pos.y) # сделай тоже самое только для y
        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.y > 0: self.rect.bottom = wall.top
                elif direction.y < 0: self.rect.top = wall.bottom
                self.pos.y = self.rect.y 
                
    # исправил int на float, теперь камера принимает точные дробные значения и дергания исчезли 
    def draw(self, surface, cam_x: float, cam_y: float):
        screen_x = int(self.pos.x - cam_x)
        screen_y = int(self.pos.y - cam_y)
        
        pygame.draw.rect(surface, self.color, (screen_x, screen_y, self.rect.width, self.rect.height))
        pygame.draw.rect(surface, (0, 0, 0), (screen_x + 6, screen_y + 8, 6, 6))
        pygame.draw.rect(surface, (0, 0, 0), (screen_x + 20, screen_y + 8, 6, 6))

        # работа над щитом
        if self.invulnerable_timer > 0:
            pygame.draw.circle(surface, (0, 255, 150), (screen_x + 16, screen_y + 16), 40, 3)