import pygame
import sys
import random

# НАСТРОЙКИ 
WIDTH, HEIGHT = 1280, 720 
FPS = 60
BLACK = (20, 20, 25)
BLUE_WALL = (100, 150, 200)

# ИГРОК 
class Player:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, 32, 32)
        self.speed = 300 
        self.color = (0, 255, 100)

    def update(self, dt, walls):
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]: direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: direction.x += 1

        if direction.magnitude() > 0:
            direction = direction.normalize()

        self.pos.x += direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
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

    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.rect(surface, self.color, offset_rect)
        pygame.draw.rect(surface, (0, 0, 0), (offset_rect.x + 6, offset_rect.y + 8, 6, 6))
        pygame.draw.rect(surface, (0, 0, 0), (offset_rect.x + 20, offset_rect.y + 8, 6, 6))

# СНАРЯДЫ 
class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, 10, 10)
        self.speed = 600 
        self.color = (255, 255, 0) 

        direction = pygame.math.Vector2(target_x - x, target_y - y)
        if direction.magnitude() > 0:
            self.direction = direction.normalize()
        else:
            self.direction = pygame.math.Vector2(1, 0)

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        self.rect.centery = round(self.pos.y)

    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.ellipse(surface, self.color, offset_rect)

# ПРЕДМЕТЫ 
class HealthPack:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.color = (255, 50, 50)

    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.rect(surface, self.color, offset_rect)
        pygame.draw.line(surface, (255, 255, 255), (offset_rect.centerx, offset_rect.top+4), (offset_rect.centerx, offset_rect.bottom-4), 3)
        pygame.draw.line(surface, (255, 255, 255), (offset_rect.left+4, offset_rect.centery), (offset_rect.right-4, offset_rect.centery), 3)

# ИИ ВРАГОВ 
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

# ГЕНЕРАЦИЯ УРОВНЯ 
def generate_dungeon():
    TILE_SIZE = 40
    COLS, ROWS = 80, 60 
    
    grid = [[1 for _ in range(COLS)] for _ in range(ROWS)] 
    rooms = []
    
    for _ in range(15):
        w = random.randint(10, 18) 
        h = random.randint(10, 18) 
        x = random.randint(2, COLS - w - 2)
        y = random.randint(2, ROWS - h - 2)
        
        new_room = pygame.Rect(x, y, w, h)
        
        failed = False
        for other_room in rooms:
            if new_room.colliderect(other_room.inflate(4, 4)): 
                failed = True
                break
                
        if not failed:
            for i in range(y, y + h):
                for j in range(x, x + w):
                    grid[i][j] = 0
            
            if len(rooms) > 0:
                prev_room = rooms[-1]
                c1_x, c1_y = new_room.centerx, new_room.centery
                c2_x, c2_y = prev_room.centerx, prev_room.centery
                
                def dig_wide_tunnel(start, end, fixed, horizontal=True):
                    for val in range(min(start, end), max(start, end) + 1):
                        if horizontal:
                            grid[fixed][val] = 0
                            if fixed + 1 < ROWS: grid[fixed + 1][val] = 0
                            if fixed - 1 >= 0: grid[fixed - 1][val] = 0
                        else:
                            grid[val][fixed] = 0
                            if fixed + 1 < COLS: grid[val][fixed + 1] = 0
                            if fixed - 1 >= 0: grid[val][fixed - 1] = 0

                if random.randint(0, 1) == 1:
                    dig_wide_tunnel(c1_x, c2_x, c1_y, True)
                    dig_wide_tunnel(c1_y, c2_y, c2_x, False)
                else:
                    dig_wide_tunnel(c1_y, c2_y, c1_x, False)
                    dig_wide_tunnel(c1_x, c2_x, c2_y, True)
                    
            rooms.append(new_room)
            
    walls = []
    for i in range(ROWS):
        for j in range(COLS):
            if grid[i][j] == 1:
                walls.append(pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                
    start_x = rooms[0].centerx * TILE_SIZE
    start_y = rooms[0].centery * TILE_SIZE
    
    return walls, start_x, start_y

# ОСНОВНОЙ ЦИКЛ ИГРЫ 
def main():
    pygame.init()
    
    font = pygame.font.SysFont("Arial", 32, bold = True)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Roguelike Prototype")
    clock = pygame.time.Clock()

    walls, spawn_x, spawn_y = generate_dungeon()

    MAP_WIDTH = 3200  
    MAP_HEIGHT = 2400
    map_rect = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)

    player = Player(spawn_x, spawn_y)
    player.health = 5
    
    bullets = []
    health_packs = []
    enemies = []

    SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1 
    pygame.time.set_timer(SPAWN_ENEMY_EVENT, 1000) 

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  

        camera_x = player.rect.centerx - WIDTH // 2
        camera_y = player.rect.centery - HEIGHT // 2

        # ОБРАБОТКА СОБЫТИЙ 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            if event.type == SPAWN_ENEMY_EVENT:
                for _ in range(10):
                    spawn_x = random.randint(100, MAP_WIDTH - 100)
                    spawn_y = random.randint(100, MAP_HEIGHT - 100)
                    
                    dist = pygame.math.Vector2(spawn_x - player.rect.centerx, 
                                               spawn_y - player.rect.centery).magnitude()
                    if dist < 800:
                        continue 
                    
                    spawn_rect = pygame.Rect(spawn_x, spawn_y, 32, 32)
                    in_wall = False
                    for wall in walls:
                        if spawn_rect.colliderect(wall):
                            in_wall = True
                            break
                            
                    if in_wall:
                        continue 
                        
                    e_type = random.choice(["normal", "normal", "scout"])
                    enemies.append(Enemy(spawn_x, spawn_y, e_type))
                    break 

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_mouse_x = mouse_x + camera_x
                    world_mouse_y = mouse_y + camera_y
                    new_bullet = Bullet(player.rect.centerx, player.rect.centery, world_mouse_x, world_mouse_y)
                    bullets.append(new_bullet)
       
        # ОБНОВЛЕНИЕ СОСТОЯНИЙ 
        player.update(dt, walls)

        for enemy in enemies[:]:
            enemy.update(dt, player, walls)
            if enemy.rect.colliderect(player.rect):
                player.health -= 1
                enemies.remove(enemy)
                if player.health <= 0:
                    screen.fill((0, 0, 0))
                    death_msg = font.render("GAME OVER", True, (255, 255, 255))
                    screen.blit(death_msg, (WIDTH//2 - 100, HEIGHT//2))
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    running = False

        for bullet in bullets[:]:
            bullet.update(dt)
            hit_wall = False
            
            for wall in walls:
                if bullet.rect.colliderect(wall):
                    hit_wall = True
                    break 
            
            if hit_wall or not map_rect.colliderect(bullet.rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                continue 
            
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if random.random() < 0.2:
                        health_packs.append(HealthPack(enemy.rect.x, enemy.rect.y))
                    
                    if enemy in enemies:
                        enemies.remove(enemy) 
                    if bullet in bullets:
                        bullets.remove(bullet) 
                    break 

        for hp in health_packs[:]:
            if player.rect.colliderect(hp.rect):
                if player.health < 5:
                    player.health += 1
                    health_packs.remove(hp)

        # ОТРИСОВКА
        screen.fill(BLACK)
        
        for wall in walls:
            screen_x = round(wall.x - camera_x)
            screen_y = round(wall.y - camera_y)
            pygame.draw.rect(screen, BLUE_WALL, (screen_x, screen_y, wall.width, wall.height))

        for hp in health_packs:
            hp.draw(screen, camera_x, camera_y)

        for enemy in enemies:
            enemy.draw(screen, camera_x, camera_y)
            
        player.draw(screen, camera_x, camera_y)
        
        for bullet in bullets:
            bullet.draw(screen, camera_x, camera_y)

        pygame.draw.rect(screen, (50, 50, 50), (10, 10, 180, 50))
        health_text = font.render(f"HP: {player.health}", True, (255, 0, 0))
        screen.blit(health_text, (20, 15))
        
        if player.health <= 1:
             pygame.draw.rect(screen, (255, 0, 0), (0, 0, WIDTH, HEIGHT), 5)
            
        pygame.display.flip()

    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    main()
