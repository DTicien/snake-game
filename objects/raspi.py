import random
from math import floor

import pygame


class RasPi:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._image_surf = pygame.image.load("images/raspi.png").convert()

    def spawn_at_random(self, window_height, window_width, snake_step):
        """
        Update the position of the raspi randomly within the game frame
        :param window_height: height of the window frame
        :param window_width: width of the window frame
        :param snake_step: Step used by the snake to move
        """
        self.x = floor(random.randint(0, window_width) / snake_step) * snake_step
        self.y = floor(random.randint(0, window_height) / snake_step) * snake_step

    def render(self, display_surf):
        display_surf.blit(self._image_surf, (self.x, self.y))
