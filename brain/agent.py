import collections

import numpy as np
import tensorflow as tf


class Agent:
    BUFFER_SIZE = 32
    STATE_SIZE = 4
    DENSE_UNITS = 64
    N_HIDDEN_LAYERS = 3
    MOVE_OPTIONS = ["up", "down", "left", "right"]
    GAMMA = 0.9

    def __init__(self):
        self.num_iterations = 0
        self.n_outputs = len(self.MOVE_OPTIONS)

        self.state_history = []

        self.state_buffer = collections.deque(maxlen=self.BUFFER_SIZE)
        self.reward_buffer = collections.deque(maxlen=self.BUFFER_SIZE)
        self.cost_buffer = collections.deque(maxlen=self.BUFFER_SIZE)

        self.network = self.create_network()

    @staticmethod
    def get_state(game, output_format=None):
        state = dict()
        state["raspi_down"] = game.snake.y[0] < game.raspi.y
        state["raspi_right"] = game.snake.x[0] < game.raspi.x
        state["wall_distance_down"] = (
            game.WINDOW_HEIGHT - game.snake.y[0]
        ) / game.WINDOW_HEIGHT
        state["wall_distance_right"] = (
            game.WINDOW_WIDTH - game.snake.x[0]
        ) / game.WINDOW_WIDTH

        if output_format == "network":
            state = [float(val) for val in state.values()]
            state = np.array(state)[np.newaxis, :]

        return state

    @staticmethod
    def compute_reward(game):
        reward = (
            float(game.snake.has_lost()) * (-1)
            + float(game.snake.has_eaten(game.raspi.x, game.raspi.y)) * 1
        )
        return reward

    def compute_cost(self):
        if self.num_iterations > 1:
            q_function_last_state = self.network.predict(
                np.array(self.state_buffer[-2])[np.newaxis, :]
            )
            q_function_current_state = self.network.predict(
                np.array(self.state_buffer[-1])[np.newaxis, :]
            )

            last_reward = self.reward_buffer[-2]

            cost = q_function_last_state - (
                last_reward + self.GAMMA * np.max(q_function_current_state)
            )
        else:
            cost = 0

        return cost

    def create_network(self):
        input_layer = tf.keras.layers.Input(shape=(self.STATE_SIZE,))
        layer = input_layer

        for i_layer in range(self.N_HIDDEN_LAYERS - 1):
            layer = tf.keras.layers.Dense(self.DENSE_UNITS, activation="relu")(layer)

        layer = tf.keras.layers.Dense(
            self.n_outputs, activation=tf.keras.activations.softmax
        )(layer)
        output = tf.keras.layers.Softmax()(layer)

        network = tf.keras.Model(inputs=input_layer, outputs=output)

        return network

    def train_network(self):
        """
        Work In Progress
        if self.num_iterations > self.BUFFER_SIZE:
            input_batch = np.squeeze(np.array(self.state_buffer))
        """

    def next_move(self, game):
        state = self.get_state(game, output_format="network")
        q_function_output = self.network.predict(state)
        idx_max = np.argmax(q_function_output.ravel())

        next_move = self.MOVE_OPTIONS[idx_max]
        return next_move

    def store(self, game):
        state = Agent.get_state(game, output_format="network")
        reward = Agent.compute_reward(game)
        cost = self.compute_cost()

        self.state_history.append(state)
        self.state_buffer.append(state)
        self.reward_buffer.append(reward)
        self.cost_buffer.append(cost)

        self.num_iterations += 1
