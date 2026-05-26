import pygame
from projectile.effects import SparkEffect 
from config import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE

class Handler:
    def __init__(self, player, world):
        self.player = player

        self.world = world
        self.walls = world.walls
        self.bullets = world.bullets
        self.enemies = world.enemies
        self.effects = world.effects
        self.grenades = world.grenades

    def process_events(self, game, camera_x: float, camera_y: float) -> bool | None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            
            # выход на esc
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # обработка колесика мышки (переключает оружие)
                if event.button == 4:
                    self.player.switch_weapon(forward=False)
                if event.button == 5:
                    self.player.switch_weapon(forward=True)
                if event.button == 1: 
                    self.player.shot(camera_x, camera_y, game.world)

    def process_elements(self, camera): 
        """Главный метод-диспетчер."""
        self._process_effects()
        self._process_grenades(camera) 
        self._process_bullets()

    def _process_effects(self):
        for effect in self.effects[:]:
            if not effect.is_alive:
                self.effects.remove(effect)

    def _process_grenades(self, camera):
        for grenade in self.grenades[:]:
            if not grenade.exploded:
                # проверка на столкновение со стеной
                for wall in self.walls:
                    if grenade.rect.colliderect(wall):
                        grenade.is_moving = False
                        break
            else: 
                grenade._grenade_is_boom(self.world, camera) 

    def _process_bullets(self):
        for bullet in self.bullets[:]:               
            if not bullet.is_alive or abs(bullet.pos.x) > MAP_WIDTH * TILE_SIZE or abs(bullet.pos.y) > MAP_HEIGHT * TILE_SIZE: 
                self.bullets.remove(bullet)
                continue

            # Столкновение со стенами
            hit_wall = False
            for wall in self.walls:
                if bullet.rect.colliderect(wall):
                    self.effects.append(SparkEffect(bullet.rect.centerx, bullet.rect.centery, bullet.color))
                    self.bullets.remove(bullet)
                    hit_wall = True
                    break
            if hit_wall: continue   

            hit_entity = False
            
            if bullet.player_bullet: 
                for enemy in self.enemies[:]: 
                    if bullet.rect.colliderect(enemy.rect):
                        enemy.get_damage(bullet.damage)              
                        push_dir = pygame.math.Vector2(bullet.direction.x, bullet.direction.y)
                        if push_dir.magnitude() > 0:
                            enemy.knockback += push_dir.normalize() * 250              
                        hit_entity = True
                        break
            else: 
                if bullet.rect.colliderect(self.player.rect):
                    self.player.get_damage(bullet.damage)
                    hit_entity = True
            
            # Удаления пули и спавна искр при любом попадании в цель
            if hit_entity and bullet in self.bullets:
                self.effects.append(SparkEffect(bullet.rect.centerx, bullet.rect.centery, bullet.color))
                self.bullets.remove(bullet)