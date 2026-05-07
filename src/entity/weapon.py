import pygame
import math
from .bullet import Bullet, Grenade
from config import (PISTOL_MAGAZINE_SIZE, PISTOL_RESERVE_AMMO, PISTOL_RELOAD_TIME, PISTOL_SHOT_DELAY,
                    SHOTGUN_MAGAZINE_SIZE, SHOTGUN_RESERVE_AMMO, SHOTGUN_RELOAD_TIME, SHOTGUN_SHOT_DELAY)


# БАЗОВЫЙ КЛАСС (Родитель) 
class Weapon:
    def __init__(self, name, damage, radius, clip, shot_delay):
        self.name = name          
        self.damage = damage
        self.radius = radius
        self.clip = clip           # максимальный размер обоймы
        self.shot_delay = shot_delay  # задержка между выстрелами (мс)
        self.last_shot_time = 0
        
        # Система патронов и перезарядки
        self.current_ammo = clip   # текущие патроны в обойме
        self.reserve_ammo = 0      # запас патронов
        self.is_reloading = False
        self.reload_start_time = 0
        self.reload_duration = 1.0  # будет переопределено в наследниках

    def can_shoot(self) -> bool:
        """Проверка, можно ли стрелять"""
        current_time = pygame.time.get_ticks()
        return (not self.is_reloading and 
                self.current_ammo > 0 and 
                current_time - self.last_shot_time >= self.shot_delay)

    def start_reload(self) -> bool:
        """Начать перезарядку"""
        if (not self.is_reloading and 
            self.current_ammo < self.clip and 
            self.reserve_ammo > 0):
            self.is_reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            return True
        return False

    def update_reload(self):
        """Обновление состояния перезарядки"""
        if self.is_reloading:
            current_time = pygame.time.get_ticks()
            if current_time - self.reload_start_time >= self.reload_duration * 1000:
                self.finish_reload()

    def finish_reload(self):
        """Завершить перезарядку"""
        needed = self.clip - self.current_ammo
        reload_amount = min(needed, self.reserve_ammo)
        self.current_ammo += reload_amount
        self.reserve_ammo -= reload_amount
        self.is_reloading = False

    def get_ammo_display(self) -> str:
        """Получить строку для отображения патронов"""
        if self.is_reloading:
            return f"RELOADING..."
        return f"{self.current_ammo} / {self.reserve_ammo}"

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        return []

    def update(self):
        self.update_reload()


# НАСЛЕДНИК: ОГНЕСТРЕЛЬНОЕ ОРУЖИЕ (Пистолет, Дробовик)
class GunWeapon(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, b_speed, b_color, spread=0, count=1, b_range=None):
        super().__init__(name, damage, radius, clip, shot_delay)
        
        self.b_speed = b_speed    
        self.b_color = b_color   
        self.spread = spread      
        self.count = count        
        self.b_range = b_range   
        
        # Настройка перезарядки в зависимости от типа оружия
        if "Scanner" in name or "пистолет" in name.lower() or name == "Scanner":
            self.reserve_ammo = 60
            self.reload_duration = 1.5
        elif "Firewall" in name or "дробовик" in name.lower() or name == "Firewall":
            self.reserve_ammo = 30
            self.reload_duration = 2.0
        else:
            self.reserve_ammo = 50
            self.reload_duration = 1.5

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        # Проверка возможности выстрела
        if not self.can_shoot():
            return [] 

        # Использовать патрон
        self.current_ammo -= 1
        self.last_shot_time = pygame.time.get_ticks()

        mx, my = pygame.mouse.get_pos()
        target_x, target_y = mx + camera_x, my + camera_y
        start_x, start_y = player_pos.x + 16, player_pos.y + 16

        bullets = []
        for i in range(self.count):
            angle = 0
            if self.count > 1:
                angle = (i - (self.count - 1) / 2) * self.spread

            b = Bullet(start_x, start_y, target_x, target_y, 
                       self.b_speed, self.b_color, self.damage, angle, self.b_range)
    
            bullets.append(b)

        return bullets


# НАСЛЕДНИК: ЛАЗЕРНОЕ ОРУЖИЕ (без патронов, работает от зарядки)
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
        
        # Лазер не использует патроны
        self.current_ammo = float('inf')
        self.reserve_ammo = float('inf')

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        current_time = pygame.time.get_ticks()
        
        if self.is_firing or self.is_charging or current_time - self.last_shot_time < self.shot_delay:
            return []

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
            
        return []

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
                
        # Лазер не использует перезарядку, но вызываем для совместимости
        super().update()


# НАСЛЕДНИК: БЛИЖНИЙ БОЙ (без патронов)
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
        
        # Ближний бой не использует патроны
        self.current_ammo = float('inf')
        self.reserve_ammo = float('inf')

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        current_time = pygame.time.get_ticks()
        
        if self.is_swinging or current_time - self.last_shot_time < self.shot_delay:
            return []

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
        
        return []

    def update(self):
        if self.is_swinging and pygame.time.get_ticks() > self.swing_timer:
            self.is_swinging = False
        super().update()


# НАСЛЕДНИК: ГРАНАТЫ (использует патроны, но не перезарядку в классическом смысле)
class GrenadeWeapon(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, throw_speed, blast_radius, fuse_time, max_range):
        super().__init__(name, damage, radius, clip, shot_delay)
        self.throw_speed = throw_speed
        self.blast_radius = blast_radius
        self.fuse_time = fuse_time
        self.max_range = max_range
        self.color = (255, 100, 150)
        
        # Гранаты имеют свои патроны (максимум clip гранат)
        self.reserve_ammo = clip
        self.current_ammo = clip
        self.reload_duration = 1.0

    def can_shoot(self) -> bool:
        current_time = pygame.time.get_ticks()
        return (self.current_ammo > 0 and 
                current_time - self.last_shot_time >= self.shot_delay)

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        if not self.can_shoot():
            return []

        self.current_ammo -= 1
        self.last_shot_time = pygame.time.get_ticks()

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

        return [grenade]