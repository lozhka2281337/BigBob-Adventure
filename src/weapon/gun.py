import pygame

from .weapon import Weapon
from projectile.bullet import Bullet

class Gun(Weapon):
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
