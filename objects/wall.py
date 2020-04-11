import pygame


class Wall:
    def __init__(
        self, header_size, window_height, window_width, thickness, color=(255, 255, 255)
    ):
        self.x_min = 0
        self.x_max = window_width - thickness

        self.y_min = header_size
        self.y_max = window_height - thickness

        self.x_min_inside = self.x_min + thickness
        self.x_max_inside = self.x_max

        self.y_min_inside = self.y_min + thickness
        self.y_max_inside = self.y_max

        self.thickness = thickness
        self.color = color

    def render(self, display_surf):

        # Vertical walls
        pygame.draw.rect(
            display_surf,
            self.color,
            (self.x_min, self.y_min, self.thickness, self.y_max - self.y_min),
        )
        pygame.draw.rect(
            display_surf,
            self.color,
            (self.x_max, self.y_min, self.thickness, self.y_max - self.y_min),
        )

        # Horizontal walls
        pygame.draw.rect(
            display_surf,
            self.color,
            (self.x_min, self.y_min, self.x_max - self.x_min, self.thickness),
        )
        pygame.draw.rect(
            display_surf,
            self.color,
            (
                self.x_min,
                self.y_max,
                self.x_max - self.x_min + self.thickness,
                self.thickness,
            ),
        )
