import random
from math import floor

import pygame


class RasPi:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._image_surf = pygame.image.load("images/raspi.png").convert()

    def spawn_at_random(self, x_min, x_max, y_min, y_max, step):
        """
        Update the position of the raspi randomly within the game frame
        :param window_height: height of the window frame
        :param window_width: width of the window frame
        :param SNAKE_STEP: Step used by the snake to move
        """
        self.x = floor(random.randint(x_min, x_max) / step) * step
        self.y = floor(random.randint(y_min, y_max) / step) * step

    def render(self, display_surf):
        display_surf.blit(self._image_surf, (self.x, self.y))
