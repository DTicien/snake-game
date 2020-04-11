from math import floor

import pygame
from pygame.locals import K_SPACE, K_RIGHT, K_LEFT, K_UP, K_DOWN, K_ESCAPE, QUIT

from objects.raspi import RasPi
from objects.snake import Snake
from brain.agent import Agent


class Game:
    MODE = "AGENT"
    WINDOW_WIDTH = 480
    WINDOW_HEIGHT = 480
    SNAKE_STEP = 16
    EATING_REWARD = 1
    NUM_GAMES_AGENT = 50000

    def __init__(self, ind_game=0):
        pygame.init()
        pygame.display.set_caption("My snake game!")
        self._display_surf = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.HWSURFACE
        )
        self.score = 0
        self.ind_game = ind_game
        self._running = True
        self.flag_lost = False
        self.snake = Snake(
            length=1,
            step=self.SNAKE_STEP,
            x_max=self.WINDOW_WIDTH,
            y_max=self.WINDOW_HEIGHT,
        )
        self.raspi = RasPi(
            x=self.SNAKE_STEP * (-1 + floor(self.WINDOW_WIDTH / 2 / self.SNAKE_STEP)),
            y=self.SNAKE_STEP * (floor(self.WINDOW_HEIGHT / 2 / self.SNAKE_STEP)),
        )
        if self.ind_game == 0:
            self.high_score = 0

        if self.MODE == "AGENT" and self.ind_game == 0:
            self.agent = Agent()
            self.num_games = self.NUM_GAMES_AGENT
        else:
            self.num_games = 1
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
        if self.MODE == "AGENT":
            self.agent.store(self)

        self.flag_lost = self.snake.has_lost()
        flag_snake_over_raspi = True
        if self.snake.has_eaten(self.raspi.x, self.raspi.y):
            self.score += self.EATING_REWARD
            self.snake.lengthen()
            while flag_snake_over_raspi:
                self.raspi.spawn_at_random(
                    self.WINDOW_HEIGHT, self.WINDOW_WIDTH, self.SNAKE_STEP
                )
                flag_snake_over_raspi = self.snake.is_over(self.raspi.x, self.raspi.y)
        self._running = not self.flag_lost

        if self.MODE == "AGENT":
            self.agent.train_network_short_term()

    def on_render(self):
        self._display_surf.fill((0, 0, 0))
        self.snake.render(self._display_surf)
        self.raspi.render(self._display_surf)
        self.display_message(f"Score: {self.score}", (50, 20), fontsize=16)
        self.display_message(
            f"High score: {self.high_score}", (self.WINDOW_WIDTH - 80, 20), fontsize=16
        )
        pygame.display.flip()

    @staticmethod
    def on_cleanup():
        pygame.quit()

    def on_execute(self):

        for i_games in range(self.num_games):
            while self._running:
                if self.MODE == "MANUAL":
                    self.manual_move()

                elif self.MODE == "AGENT":
                    self.agent_move()

                self.on_loop()
                self.on_render()
                self.clock.tick(60)

                if self.flag_lost:
                    self.set_high_score()
                    if self.MODE == "MANUAL":
                        self.display_message(
                            f"You lost, you big big loser! - final score: {self.score}",
                            (self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2),
                        )
                        self.display_message(
                            f"Replay: press space, Quit: press escape",
                            (self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 50),
                            fontsize=16,
                        )
                        accepted_replay = "undef"
                        while accepted_replay == "undef":
                            accepted_replay = self.propose_replay()
                    elif self.MODE == "AGENT":
                        self.agent.train_network()
                        self.agent.summary(self)
                        self.__init__(self.ind_game + 1)  # Reinit game

        Game.on_cleanup()

    def manual_move(self):
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

    def agent_move(self):
        next_move = self.agent.next_move(self)
        if next_move == "right" and self.snake.direction != "left":
            self.snake.move_right()
        if next_move == "left" and self.snake.direction != "right":
            self.snake.move_left()
        if next_move == "up" and self.snake.direction != "down":
            self.snake.move_up()
        if next_move == "down" and self.snake.direction != "up":
            self.snake.move_down()

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

    def set_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score


if __name__ == "__main__":
    theGame = Game()
    theGame.on_execute()
