import pygame
from pygame.locals import K_SPACE, K_RIGHT, K_LEFT, K_UP, K_DOWN, K_ESCAPE, QUIT

from objects.raspi import RasPi
from objects.snake import Snake


class Game:
    windowWidth = 800
    windowHeight = 608
    snake_step = 16

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("My snake game!")
        self._display_surf = pygame.display.set_mode(
            (self.windowWidth, self.windowHeight), pygame.HWSURFACE
        )
        self.points = 0
        self._running = True
        self.flag_lost = False
        self.snake = Snake(
            length=4,
            step=self.snake_step,
            x_max=self.windowWidth,
            y_max=self.windowHeight,
        )
        self.raspi = RasPi(x=0, y=0)
        self.raspi.spawn_at_random(self.windowHeight, self.windowWidth, self.snake_step)
        self.snake.render(self._display_surf)
        self.clock = pygame.time.Clock()

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False
            Game.on_cleanup()
            exit()

    def on_loop(self):
        """
        Method executed for each clock tick
        """
        self.snake.update()
        self.flag_lost = self.snake.has_lost()
        flag_snake_over_raspi = True
        if self.snake.has_eaten(self.raspi.x, self.raspi.y):
            self.points += 5
            self.snake.lengthen()
            while flag_snake_over_raspi:
                self.raspi.spawn_at_random(
                    self.windowHeight, self.windowWidth, self.snake_step
                )
                flag_snake_over_raspi = self.snake.is_over(self.raspi.x, self.raspi.y)
        self._running = not self.flag_lost
        pass

    def on_render(self):
        self._display_surf.fill((0, 0, 0))
        self.snake.render(self._display_surf)
        self.raspi.render(self._display_surf)
        self.display_message(
            f"Points: {self.points}", (self.windowWidth - 50, 20), fontsize=16
        )
        pygame.display.flip()

    @staticmethod
    def on_cleanup():
        pygame.quit()

    def on_execute(self):

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)

            pygame.event.pump()
            keys = pygame.key.get_pressed()

            if keys[K_RIGHT] and self.snake.direction != "left":
                self.snake.move_right()

            if keys[K_LEFT] and self.snake.direction != "right":
                self.snake.move_left()

            if keys[K_UP] and self.snake.direction != "down":
                self.snake.move_up()

            if keys[K_DOWN] and self.snake.direction != "up":
                self.snake.move_down()

            if keys[K_ESCAPE]:
                self._running = False

            self.on_loop()
            self.on_render()
            self.clock.tick(16)

            if self.flag_lost:
                self.display_message(
                    f"You lost, you big big loser! - final score: {self.points}",
                    (self.windowWidth // 2, self.windowHeight // 2),
                )
                self.display_message(
                    f"Replay: press space, Quit: press escape",
                    (self.windowWidth // 2, self.windowHeight // 2 + 50),
                    fontsize=16,
                )
                accepted_replay = "undef"
                while accepted_replay == "undef":
                    accepted_replay = self.propose_replay()

        Game.on_cleanup()

    def display_message(self, message_string, position, fontsize=32):
        font = pygame.font.Font("freesansbold.ttf", fontsize)
        text = font.render(message_string, True, (255, 255, 255), (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = position
        self._display_surf.blit(text, text_rect)
        pygame.display.flip()

    def propose_replay(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[K_SPACE]:
            self.__init__()
            return "yes"
        elif keys[K_ESCAPE]:
            self._running = False
            return "no"
        else:
            return "undef"


if __name__ == "__main__":
    theGame = Game()
    theGame.on_execute()
