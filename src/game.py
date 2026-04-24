import pygame

from entity.enemy import Enemy
from entity.player import Player

from config import (WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT, 
                    SPAWN_ENEMY_EVENT, SPAWN_ENEMY_TIME, 
                    FPS, SHOT_DELAY, BLUE_WALL)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Roguelike Prototype")

        self.font = pygame.font.SysFont("Arial", 32, bold = True)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.FONT = pygame.font.SysFont("Arial", 32, bold = True)

        self.clock = pygame.time.Clock()

        self.new_game()

    def new_game(self):
        self.player = Player(0, 0)
        
        self.bullets = []
        self.health_packs = []
        self.enemies = []
        self.walls = []

        self.running = True

        """ потом убрать"""
        self.enemies.append(Enemy(100, 100))
        self.enemies.append(Enemy(-200, 100))
        self.enemies.append(Enemy(-500, 100))
        self.walls.append(pygame.Rect(100, -250, 50, 500))
        self.walls.append(pygame.Rect(-200, -250, 50, 500))
        self.walls.append(pygame.Rect(-500, -250, 50, 500))

    def process_events(self, camera_x: float, camera_y: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # 1 - лкм, 2 - колесо, 3 - пкм
                    bullet = self.player.shot(camera_x, camera_y)
                    self.bullets.append(bullet)

    def process_bullets(self):
        for bullet in self.bullets:
            for wall in self.walls:
                if bullet.rect.colliderect(wall):
                    self.bullets.remove(bullet)
                    continue

            if abs(bullet.pos.x) > MAP_WIDTH:
                self.bullets.remove(bullet)
                continue

            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):
                    self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    break

    def process_enemies(self):
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                self.player.get_damage()
                if self.player.hp <= 0: self.death_player()

    def death_player(self):
        self.screen.fill((0, 0, 0))

        death_msg = self.FONT.render("GAME OVER", True, (255, 255, 255))
        self.screen.blit(death_msg, (WIDTH//2 - 100, HEIGHT//2))
        pygame.display.flip()

        pygame.time.wait(3000)
        
        self.new_game()

    def draw_hp(self):
        pygame.draw.rect(self.screen, (50, 50, 50), (10, 10, 180, 50))
        health_text = self.FONT.render(f"HP: {self.player.hp}", True, (255, 0, 0))
        self.screen.blit(health_text, (20, 15))

        if self.player.hp <= 1:
            pygame.draw.rect(self.screen, (255, 0, 0), (0, 0, WIDTH, HEIGHT), 5)

    """ три главные функции"""

    def update(self, dt: float):
        self.player.update(dt, self.walls)

        for bullet in self.bullets:
            bullet.update(dt)

        for enemy in self.enemies:
            enemy.update(dt, self.player, self.walls)

        self.process_bullets()
        self.process_enemies()

    def draw(self, camera_x, camera_y):
        self.screen.fill("purple")

        # временная сетка
        for x in range(-2000, 2000, 50):
            pygame.draw.line(self.screen, (100, 50, 150), (x - camera_x, -2000-camera_y), (x - camera_x, 2000 - camera_y))
        for y in range(-2000, 2000, 50):
            pygame.draw.line(self.screen, (100, 50, 150), (-2000-camera_x, y - camera_y), (2000 - camera_x, y - camera_y))

        """ ентити """
        self.player.draw(self.screen, camera_x, camera_y)
        
        for bullet in self.bullets: 
            bullet.draw(self.screen, camera_x, camera_y)
        
        for enemy in self.enemies:
            enemy.draw(self.screen, camera_x, camera_y)
        
        """ стены """
        for wall in self.walls:
            screen_x = int(wall.x - camera_x)
            screen_y = int(wall.y - camera_y)
            pygame.draw.rect(self.screen, BLUE_WALL, (screen_x, screen_y, wall.width, wall.height))

        """ интерфейс """
        self.draw_hp()

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  

            camera_x = self.player.pos.x + 16 - WIDTH / 2
            camera_y = self.player.pos.y + 16 - HEIGHT / 2

            self.process_events(camera_x, camera_y)
            self.update(dt)
            self.draw(camera_x, camera_y)
