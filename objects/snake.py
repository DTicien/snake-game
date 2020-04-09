import pygame


class Snake:
    n_added = 1  # Number of items to add to the snake when it lengthens

    def __init__(self, length, x_max, y_max, step):
        self.step = step
        self.length = length  # Initial length of the snake
        self.x_max = x_max
        self.y_max = y_max
        self._image_surf = pygame.image.load("images/snake_mini.png").convert()
        self.direction = "left"
        self.x = []  # x positions of the snake's items
        self.y = []  # y positions of the snake's items
        for i in range(self.length):
            self.x.append(int(x_max / 2) - (self.length - 1 - i) * self.step)
            self.y.append(int(y_max / 2))

    def update(self):
        """
        Method to update the snake position
        """

        # Update tail
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        # Update head
        if self.direction == "right":
            self.x[0] += self.step
        if self.direction == "left":
            self.x[0] -= self.step
        if self.direction == "up":
            self.y[0] -= self.step
        if self.direction == "down":
            self.y[0] += self.step

    def lengthen(self):
        """
        Method to lengthen the snake when it has eaten a raspi
        Its extended with self.n_added new items
        :return:
        """
        self.length += self.n_added
        for i in range(self.n_added):
            self.x.append(self.x[-1])
            self.y.append(self.y[-1])

    def move_right(self):
        self.direction = "right"

    def move_left(self):
        self.direction = "left"

    def move_up(self):
        self.direction = "up"

    def move_down(self):
        self.direction = "down"

    def has_eaten(self, raspi_x, raspi_y):
        """
        Method to check whether the snake has eaten the raspi or not
        :param raspi_x: x coordinate of the raspi
        :param rapsi_y: y coordinate of the raspi
        :return:
        flag_eaten: True if the snake has eaten the raspi
        """
        flag_eaten = self.x[0] == raspi_x and self.y[0] == raspi_y
        return flag_eaten

    def is_over(self, raspi_x, rapsi_y):
        """
        # Method to know if the snake is over a raspi
        :param raspi_x: x coordinate of the raspi
        :param rapsi_y: y coordinate of the raspi
        :return:
        True if the snake if over the raspi
        """
        return (raspi_x, rapsi_y) in list(zip(self.x, self.y))

    def has_lost(self):
        """
        Method to know if the player has lost
        - Either the snake touched the frame border
        - Or it cut itself
        :return:
        flag_lost: True if player has lost
        """
        # Find out if snake's head has touched the border
        flag_lost_border = (
            (self.x[0] > self.x_max - 1)
            or (self.x[0] < 0)
            or (self.y[0] > self.y_max - 1)
            or (self.y[0] < 0)
        )

        # Find out if snake's has cut itself through
        flag_lost_self_intersect = (self.x[0], self.y[0]) in list(
            zip(
                [self.x[i] for i in range(1, self.length)],
                [self.y[i] for i in range(1, self.length)],
            )
        )
        flag_lost_self_intersect = False

        flag_lost = flag_lost_border or flag_lost_self_intersect
        return flag_lost

    def render(self, display_surf):
        for x, y in zip(self.x, self.y):
            display_surf.blit(self._image_surf, (x, y))
