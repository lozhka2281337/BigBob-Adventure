import pygame

from .bullet import Bullet
from config import SHOT_DELAY

class Weapon:
    def __init__(self, damage, radius, clip, shot_delay):
        self.damage = damage
        self.radius = radius
        self.shot_delay = shot_delay
        self.clip = clip     # количество патронов в обойме 

        self.last_shot_time = 0

    def shot(self, player_pos, camera_x: float, camera_y: float) -> None | Bullet:
        """
        мб стрелять через класс оружия вместо игрока, но пока так
        """
        pass


