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
    def draw(self, surface, camera_x, camera_y, player_rect, walls):
        pass
