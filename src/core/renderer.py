import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, SURFACE_COLOR


class Renderer:
    def __init__(self, screen, player, world):
        self.screen = screen
        self.player = player

        self.walls = world.walls
        self.bullets = world.bullets
        self.effects = world.effects
        self.grenades = world.grenades
        self.enemies = world.enemies
        self.matrix = world.matrix

        self.FONT = pygame.font.SysFont("Arial", 32, bold=True)
        self.map_surface = pygame.Surface((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE), pygame.SRCALPHA)


        #Загружаем спрайт для пола
        floor_lvl1 = pygame.image.load("assets/FloorLvl1.png").convert_alpha()
        self.floor_lvl1 = pygame.transform.scale(floor_lvl1, (TILE_SIZE, TILE_SIZE))

        #Загружаем спрайт для стен
        wall_lvl1 = pygame.image.load("assets/WallLvl1.png").convert_alpha()
        self.wall_lvl1 = pygame.transform.scale(wall_lvl1, (TILE_SIZE, TILE_SIZE))

        # Загружаем спрайт для отображения HP
        self.hp_sprite = pygame.image.load("assets/Hp.png").convert_alpha()
        self.hp_width = self.hp_sprite.get_width()

        self.init_map_surface()

    def init_map_surface(self):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.matrix[y][x] == 0:
                    self.map_surface.blit(self.floor_lvl1, (x * TILE_SIZE, y * TILE_SIZE))

        """ стены """
        for wall in self.walls:
            self.map_surface.blit(self.wall_lvl1, (wall.x, wall.y))

    def draw_hp(self):
        """Рисуем столько спрайтов HP, сколько здоровья у игрока"""
        margin_x = 10  # отступ слева
        margin_y = 10  # отступ сверху
        spacing = 5  # расстояние между иконками

        for i in range(self.player.hp):
            x = margin_x + i * (self.hp_width + spacing)
            y = margin_y
            self.screen.blit(self.hp_sprite, (x, y))


    def draw_death_screen(self):
        self.screen.fill((0, 0, 0))

        death_msg = self.FONT.render("GAME OVER", True, (255, 255, 255))
        self.screen.blit(death_msg, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        pygame.display.flip()

        pygame.time.wait(3000)

    def draw_weapon_hud(self):
        start_x = SCREEN_WIDTH - 220
        start_y = SCREEN_HEIGHT - 80

        for i in range(len(self.player.inventory.weapons)):
            weapon = self.player.inventory.weapons[i]
            is_active = (i == self.player.inventory.current_idx)
            offset_y = (i - self.player.inventory.current_idx) * -35
            w_color = getattr(weapon, 'b_color', getattr(weapon, 'color', (255, 255, 255)))

            if is_active:
                text_surf = self.FONT.render(f"> {weapon.name}", True, w_color)
            else:
                text_surf = self.FONT.render(weapon.name, True, (120, 120, 120))
                text_surf.set_alpha(150)
            self.screen.blit(text_surf, (start_x, start_y + offset_y))

    def draw_weapon(self, camera_x, camera_y):
        weapon = self.player.inventory.get_current()
        if hasattr(weapon, 'draw'):
            weapon.draw(self.screen, camera_x, camera_y, self.player.rect, self.walls)

    def draw(self, camera_x, camera_y):
        """ карта """
        self.screen.fill(SURFACE_COLOR)
        self.screen.blit(self.map_surface, (-camera_x, -camera_y))

        """ ентити """
        self.player.draw(self.screen, camera_x, camera_y)

        """ атака оружия игрока """
        self.draw_weapon(camera_x, camera_y)

        for bullet in self.bullets:
            bullet.draw(self.screen, camera_x, camera_y)

        for grenade in self.grenades:
            grenade.draw(self.screen, camera_x, camera_y)

        for effect in self.effects:
            effect.draw(self.screen, camera_x, camera_y)

        for enemy in self.enemies:
            enemy.draw(self.screen, camera_x, camera_y)

        """ интерфейс """
        self.draw_hp()
        self.draw_weapon_hud()

        pygame.display.flip()