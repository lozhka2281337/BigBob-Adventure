import pygame
import sys
import random

from config import (WIDTH, HEIGHT, FPS,
                    MAP_HEIGHT, MAP_WIDTH,
                    BLACK, BLUE_WALL)

from entity.bullet import Bullet
from entity.player import Player
from entity.enemy import Enemy
from entity.items import HealthPack

import dungeon.generation_dungeon as dungeon

# ОСНОВНОЙ ЦИКЛ ИГРЫ 
def main():
    pygame.init()
    
    font = pygame.font.SysFont("Arial", 32, bold = True)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Roguelike Prototype")
    clock = pygame.time.Clock()

    walls, spawn_x, spawn_y = dungeon.generate_dungeon()

    map_rect = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)

    player = Player(spawn_x, spawn_y)
    
    bullets = []
    health_packs = []
    enemies = []

    SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1 
    pygame.time.set_timer(SPAWN_ENEMY_EVENT, 1800) 

    running = True
    last_shot_time = 0
    shot_delay = 300
    #камера теперь будет привязана к точным координатам позиции и зафиксировал время для плавной физики.
    while running:
        clock.tick(FPS)
        dt = 1.0 / FPS  

        camera_x = player.pos.x + 16 - WIDTH / 2
        camera_y = player.pos.y + 16 - HEIGHT / 2

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
                    # добавил проверку, прошло ли достаточно времени с прошлого выстрела
                    current_time = pygame.time.get_ticks()
                    if current_time - last_shot_time > shot_delay:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        world_mouse_x = mouse_x + camera_x
                        world_mouse_y = mouse_y + camera_y
                        
                        new_bullet = Bullet(player.pos.x + 16, player.pos.y + 16, world_mouse_x, world_mouse_y)
                        bullets.append(new_bullet)
                        
                        last_shot_time = current_time
       
        # ОБНОВЛЕНИЕ СОСТОЯНИЙ 
        player.update(dt, walls)

        # добавил изменеия для щита 
        for enemy in enemies[:]:
            enemy.update(dt, player, walls)
            if enemy.rect.colliderect(player.rect):
                
                if player.invulnerable_timer <= 0:
                    player.health -= 1
                    player.invulnerable_timer = 3.0            
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
        # стены теперь тоже теперь отрисовываются с привязкой к зачетной камере. 
        for wall in walls:
            screen_x = int(wall.x - camera_x)
            screen_y = int(wall.y - camera_y)
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
