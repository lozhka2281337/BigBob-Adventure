import pygame

from entity.weapon import LaserWeapon

from config import MAP_WIDTH

class Handler:
    def __init__(self, player, walls, bullets, enemies):
        self.player = player
        self.walls = walls
        self.bullets = bullets
        self.enemies = enemies

    def process_events(self, game, camera_x: float, camera_y: float) -> bool | None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.player.current_weapon_idx = (self.player.current_weapon_idx - 1) % len(self.player.inventory)
                
                if event.button == 5:
                    self.player.current_weapon_idx = (self.player.current_weapon_idx + 1) % len(self.player.inventory)

                if event.button == 1: 
                    new_bullets = self.player.shot(camera_x, camera_y)
                    if new_bullets:
                        self.bullets.extend(new_bullets)

    def process_bullets(self):
        for bullet in self.bullets[:]:
            
            if hasattr(bullet, 'is_alive') and not bullet.is_alive:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue

            hit_wall = False
            for wall in self.walls:
                if bullet.rect.colliderect(wall):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    hit_wall = True
                    break
            
            if hit_wall: continue

            if abs(bullet.pos.x) > MAP_WIDTH:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue

            for enemy in self.enemies[:]: 
                if bullet.rect.colliderect(enemy.rect):
                    if enemy in self.enemies:
                        enemy.get_damage(bullet.damage)
                        if enemy.hp <= 0: self.enemies.remove(enemy)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

    def process_player_damage(self, game):
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                self.player.get_damage()
                if self.player.hp <= 0: game.death_player()

    def process_laser_damage(self):
        weapon = self.player.inventory[self.player.current_weapon_idx]
        
        if isinstance(weapon, LaserWeapon) and weapon.is_firing:
            start_pos = self.player.rect.center
            
            end_pos = (start_pos[0] + weapon.locked_dir.x * 1500, start_pos[1] + weapon.locked_dir.y * 1500)
            
            for enemy in self.enemies[:]:
                if enemy.rect.clipline(start_pos, end_pos):
                    self.enemies.remove(enemy)
