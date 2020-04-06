import time
import random
from math import floor

import pygame
from pygame.locals import *


class Snake:
    x = []  # x positions of the snake's items
    y = []  # y positions of the snake's items
    direction = ''
    length = 4  # Initial length of the snake
    n_added = 3  # Number of items to add to the snake when it lengthens

    def __init__(self, length, x_max, y_max, step):
        self.step = step
        self.length = length
        self.x_max = x_max
        self.y_max = y_max
        self._image_surf = pygame.image.load("images/snake_mini.png").convert()
        self.direction = 'left'
        for i in range(self.length):
            self.x.append(int(x_max / 2) - (self.length - 1 - i) * self.step)
            self.y.append(int(y_max / 2))

    def update(self):

        # Update tail
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        # Update head
        if self.direction == 'right':
            self.x[0] += self.step
        if self.direction == 'left':
            self.x[0] -= self.step
        if self.direction == 'up':
            self.y[0] -= self.step
        if self.direction == 'down':
            self.y[0] += self.step

        return self.has_lost()

    def lengthen(self):
        self.length += self.n_added
        for i in range(self.n_added):
            self.x.append(self.x[-1])
            self.y.append(self.y[-1])

    def move_right(self):
        self.direction = 'right'

    def move_left(self):
        self.direction = 'left'

    def move_up(self):
        self.direction = 'up'

    def move_down(self):
        self.direction = 'down'

    def has_eaten(self, raspi_x, raspi_y):
        flag_eaten = self.x[0] == raspi_x and self.y[0] == raspi_y
        return flag_eaten

    # Method to know if the snake is over a raspi
    def is_over(self, raspi_x, rapsi_y):
        return (raspi_x, rapsi_y) in list(zip(self.x, self.y))

    def has_lost(self):
        # Lost if snake's head has touched the border
        flag_lost_border = (self.x[0] > self.x_max - 1) or (self.x[0] < 0) or (self.y[0] > self.y_max - 1) or (
                self.y[0] < 0)

        flag_lost_self_intersect = (self.x[0], self.y[0]) in list(
            zip([self.x[i] for i in range(1, self.length)], [self.y[i] for i in range(1, self.length)]))

        flag_lost = flag_lost_border or flag_lost_self_intersect
        return flag_lost

    def render(self, display_surf):
        for x, y in zip(self.x, self.y):
            display_surf.blit(self._image_surf, (x, y))


class RasPi:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._image_surf = pygame.image.load("images/raspi.png").convert()

    def render(self, display_surf):
        display_surf.blit(self._image_surf, (self.x, self.y))


class App:
    windowWidth = 800
    windowHeight = 608
    snake = 0
    snake_step = 16
    lost = False

    def __init__(self):

        pygame.init()
        pygame.display.set_caption('My snake game!')
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        self._running = True
        self.snake = Snake(length=4,
                           step=self.snake_step,
                           x_max=self.windowWidth,
                           y_max=self.windowHeight)
        self.raspi = RasPi(x=96,
                           y=96)
        self.snake.render(self._display_surf)
        self.clock = pygame.time.Clock()

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        self.lost = self.snake.update()
        flag_snake_over_raspi = True
        if self.snake.has_eaten(self.raspi.x, self.raspi.y):
            self.snake.lengthen()
            while flag_snake_over_raspi:
                self.raspi.x = floor(random.randint(0, self.windowHeight) / self.snake_step) * self.snake_step
                self.raspi.y = floor(random.randint(0, self.windowHeight) / self.snake_step) * self.snake_step
                flag_snake_over_raspi = self.snake.is_over(self.raspi.x, self.raspi.y)
        self._running = not self.lost
        pass

    def on_render(self):
        self._display_surf.fill((0, 0, 0))
        self.snake.render(self._display_surf)
        self.raspi.render(self._display_surf)
        pygame.display.flip()

    @staticmethod
    def on_cleanup():
        pygame.quit()

    def on_execute(self):

        while self._running:
            pygame.event.pump()
            keys = pygame.key.get_pressed()

            if keys[K_RIGHT]:
                self.snake.move_right()

            if keys[K_LEFT]:
                self.snake.move_left()

            if keys[K_UP]:
                self.snake.move_up()

            if keys[K_DOWN]:
                self.snake.move_down()

            if keys[K_SPACE]:
                self.snake.lengthen()

            if keys[K_ESCAPE]:
                self._running = False

            self.on_loop()
            self.on_render()
            self.clock.tick(16)
        if self.lost:
            self.display_loser_message()
            time.sleep(5)
        App.on_cleanup()

    def display_loser_message(self):
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render('You lost, you big big loser!', True, (255, 255, 255), (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.windowWidth // 2, self.windowHeight // 2)
        self._display_surf.blit(text, text_rect)
        pygame.display.flip()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
