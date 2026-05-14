import pygame
import math
from .bullet import Bullet, Grenade

# БАЗОВЫЙ КЛАСС (Родитель) 
class Weapon:
    def __init__(self, name, damage, radius, clip, shot_delay):
        self.name = name          
        self.damage = damage
        self.radius = radius
        self.clip = clip     
        self.shot_delay = shot_delay
        self.last_shot_time = 0

    def shot(self, player_pos, camera_x: float, camera_y: float, world) -> None:
        pass
    def update(self):
        pass
    def process_damage(self, enemies, player_rect, walls):
        pass


# НАСЛЕДНИК: ОГНЕСТРЕЛЬНОЕ ОРУЖИЕ (Пистолет, Дробовик)
class GunWeapon(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, b_speed, b_color, spread=0, count=1, b_range=None):
        super().__init__(name, damage, radius, clip, shot_delay)
        
        self.b_speed = b_speed    
        self.b_color = b_color   
        self.spread = spread      
        self.count = count        
        self.b_range = b_range   

    def shot(self, player_pos, camera_x: float, camera_y: float, world) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.shot_delay:
            return 

        self.last_shot_time = current_time

        mx, my = pygame.mouse.get_pos()
        target_x, target_y = mx + camera_x, my + camera_y
        start_x, start_y = player_pos.x + 16, player_pos.y + 16

        for i in range(self.count):
            angle = 0
            if self.count > 1:
                angle = (i - (self.count - 1) / 2) * self.spread

            b = Bullet(start_x, start_y, target_x, target_y, 
                       self.b_speed, self.b_color, self.damage, angle, self.b_range, True)
    
            world.bullets.append(b) 


# НАСЛЕДНИК: ЛАЗЕРНОЕ ОРУЖИЕ 
class LaserWeapon(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, duration, beam_width, color, charge_time=400):
        super().__init__(name, damage, radius, clip, shot_delay)
        
        self.duration = duration      
        self.beam_width = beam_width  
        self.color = color            
        self.charge_time = charge_time 
        
        self.is_charging = False
        self.is_firing = False
        self.active_timer = 0
        
        self.locked_dir = pygame.math.Vector2(0, 0)

    def shot(self, player_pos, camera_x: float, camera_y: float, world) -> None:
        current_time = pygame.time.get_ticks()
        
        if self.is_firing or self.is_charging or current_time - self.last_shot_time < self.shot_delay:
            return

        self.last_shot_time = current_time
        
        self.is_charging = True
        self.active_timer = current_time + self.charge_time
        
        mx, my = pygame.mouse.get_pos()
        target_world = (mx + camera_x, my + camera_y)
        start_center = (player_pos.x + 16, player_pos.y + 16)
        dir_vec = pygame.math.Vector2(target_world[0] - start_center[0], target_world[1] - start_center[1])
        
        if dir_vec.magnitude() > 0:
            self.locked_dir = dir_vec.normalize()
        else:
            self.locked_dir = pygame.math.Vector2(1, 0)

    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.is_charging:
            if current_time > self.active_timer:
                self.is_charging = False
                self.is_firing = True
                self.active_timer = current_time + self.duration 
                
        elif self.is_firing:
            if current_time > self.active_timer:
                self.is_firing = False

    def get_laser_end_pos(self, start_pos, walls):
        max_end = pygame.math.Vector2(
            start_pos[0] + self.locked_dir.x * 1500, 
            start_pos[1] + self.locked_dir.y * 1500
        )
        final_point = max_end
        min_dist = 1500
        start_v = pygame.math.Vector2(start_pos)

        for wall in walls:
            intersect = wall.clipline(start_pos, max_end)
            if intersect:
                hit_point = pygame.math.Vector2(intersect[0])
                dist = start_v.distance_to(hit_point)
                if dist < min_dist:
                    min_dist = dist
                    final_point = hit_point
        return final_point

    def process_damage(self, enemies, player_rect, walls):
        if self.is_firing:
            start_pos = player_rect.center
            end_pos = self.get_laser_end_pos(start_pos, walls)

            for enemy in enemies[:]:
                if enemy.rect.clipline(start_pos, end_pos):
                    enemy.get_damage(self.damage) 
                    
                    enemy.knockback += self.locked_dir * 30 
                    
                    if enemy.hp <= 0: enemies.remove(enemy)


# НАСЛЕДНИК: БЛИЖНИЙ БОЙ (USB-Katana)
class MeleeWeapon(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, reach, arc_degrees, color):
        super().__init__(name, damage, radius, clip, shot_delay)
        self.reach = reach
        self.arc_degrees = arc_degrees
        self.color = color
        
        self.is_swinging = False
        self.swing_duration = 200
        self.swing_timer = 0
        self.locked_angle = 0
        self.hit_enemies = [] 

    def shot(self, player_pos, camera_x: float, camera_y: float, world) -> None:
        current_time = pygame.time.get_ticks()
        
        if self.is_swinging or current_time - self.last_shot_time < self.shot_delay:
            return

        self.last_shot_time = current_time
        
        self.is_swinging = True
        self.swing_timer = current_time + self.swing_duration
        self.hit_enemies = []
        
        mx, my = pygame.mouse.get_pos()
        target_world_x, target_world_y = mx + camera_x, my + camera_y
        start_center_x, start_center_y = player_pos.x + 16, player_pos.y + 16
        
        dx = target_world_x - start_center_x
        dy = target_world_y - start_center_y
        self.locked_angle = math.degrees(math.atan2(dy, dx))

    def update(self):
        if self.is_swinging and pygame.time.get_ticks() > self.swing_timer:
            self.is_swinging = False

    def process_damage(self, enemies, player_rect, walls):
        if self.is_swinging:
            start_pos = pygame.math.Vector2(player_rect.center)

            for enemy in enemies[:]:
                if enemy in self.hit_enemies: continue
                
                enemy_pos = pygame.math.Vector2(enemy.rect.center)
                dist = start_pos.distance_to(enemy_pos)
                
                if dist <= self.reach + 16:
                    dx = enemy_pos.x - start_pos.x
                    dy = enemy_pos.y - start_pos.y
                    
                    angle_to_enemy = math.degrees(math.atan2(dy, dx))
                    angle_diff = (angle_to_enemy - self.locked_angle + 180) % 360 - 180
                    
                    if abs(angle_diff) <= self.arc_degrees / 2:
                        enemy.get_damage(150) 
                        
                        push_dir = enemy_pos - start_pos
                        if push_dir.magnitude() > 0:
                            enemy.knockback += push_dir.normalize() * 1200
                        
                        if enemy.hp <= 0: enemies.remove(enemy)
                        self.hit_enemies.append(enemy)


# НАСЛЕДНИК: ГРАНАТЫ (Zip-Bomb)
class GrenadeWeapon(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, throw_speed, blast_radius, fuse_time, max_range):
        super().__init__(name, damage, radius, clip, shot_delay)
        self.throw_speed = throw_speed
        self.blast_radius = blast_radius
        self.fuse_time = fuse_time
        self.max_range = max_range
        self.color = (255, 100, 150) 

    def shot(self, player_pos, camera_x: float, camera_y: float, world) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.shot_delay:
            return

        self.last_shot_time = current_time

        mx, my = pygame.mouse.get_pos()
        target_x, target_y = mx + camera_x, my + camera_y
        start_x, start_y = player_pos.x + 16, player_pos.y + 16

        grenade = Grenade(
            start_x, start_y, 
            target_x, target_y, 
            self.throw_speed, 
            self.color, 
            self.blast_radius, 
            self.fuse_time, 
            self.max_range
        )

        world.grenades.append(grenade) 