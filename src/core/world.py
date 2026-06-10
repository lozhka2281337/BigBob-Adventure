import config as cfg

class World:
    def __init__(self):
        self.mod = cfg.NORMAL_MOD

        self.enemies = []
        self.bullets = []
        self.grenades = []
        self.effects = []
        self.walls = []
<<<<<<< HEAD
        self.items = []
=======
        self.pings = []
>>>>>>> feature/stels-mode

        # матрица карты
        self.matrix = []