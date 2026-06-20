import pygame

import config as cfg

""" класс для перехода между состояниями игры """
class TransitionManager:
    def __init__(self, screen, camera):
        self.screen = screen
        self.camera = camera

        self.flash_alpha = 0   

    def trigger_transition(self):
        self.flash_alpha = 255        
        self.camera.add_shake(3.0)

    def update(self, dt):
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 50 * dt)

    def draw_flash(self): # вспышка после активации ядра
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
            flash_surf.fill((115, 10, 10))
            flash_surf.set_alpha(self.flash_alpha)
            self.screen.blit(flash_surf, (0, 0))