import pygame
import random

from core.spawner import Spawner
from entity.boss import Boss, BOSS_SIZE


class BossSpawner(Spawner):
    """Спавнер для тестового режима: размещает только одного босса Root-Kit.

    Босс появляется в комнате, наиболее удалённой от стартовой позиции игрока.
    """

    def spawn_initial(self) -> None:
        boss_room = self._find_boss_room()
        x, y = self._get_safe_spawn_pos(boss_room, BOSS_SIZE)
        boss = Boss(x, y, boss_room)
        self.world.enemies.append(boss)

    def _find_boss_room(self) -> pygame.Rect:
        player_pos = pygame.math.Vector2(self.player.pos)
        best_room: pygame.Rect | None = None
        max_dist   = -1.0

        for room in self.world.rooms:
            if room.collidepoint(player_pos):
                continue
            dist = player_pos.distance_to(pygame.math.Vector2(room.center))
            if dist > max_dist:
                max_dist  = dist
                best_room = room

        # Запасной вариант: любая не-игрецкая комната
        if best_room is None:
            candidates = [r for r in self.world.rooms
                          if not r.collidepoint(player_pos)]
            best_room  = random.choice(candidates) if candidates else self.world.rooms[0]

        return best_room
