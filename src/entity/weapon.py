import pygame

from .bullet import Bullet

class Weapon:
   
    def __init__(self, name, damage, radius, clip, shot_delay, b_speed, b_color, spread=0, count=1, b_range=None):
        self.name = name          
        self.damage = damage
        self.radius = radius
        self.shot_delay = shot_delay
        self.clip = clip     

        self.b_speed = b_speed    
        self.b_color = b_color   
        self.spread = spread     
        self.count = count        
        self.b_range = b_range   
        self.last_shot_time = 0

   
    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        """
        мб стрелять через класс оружия вместо игрока, но пока так
        """
        
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.shot_delay:
            return [] 

        self.last_shot_time = current_time

       
        mx, my = pygame.mouse.get_pos()
        target_x, target_y = mx + camera_x, my + camera_y
        start_x, start_y = player_pos.x + 16, player_pos.y + 16

        bullets = []
        
       
        for i in range(self.count):
            angle = 0
            if self.count > 1:
                
                angle = (i - (self.count - 1) / 2) * self.spread

            
            b = Bullet(start_x, start_y, target_x, target_y, 
                       self.b_speed, self.b_color, angle, self.b_range)
            bullets.append(b)

        return bullets
