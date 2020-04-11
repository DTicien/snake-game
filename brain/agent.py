import random
import collections

import numpy as np
import tensorflow as tf


class Agent:
    BUFFER_SIZE = 3000
    BATCH_SIZE = 200
    STATE_SIZE = 12
    DENSE_UNITS = 150
    N_HIDDEN_LAYERS = 3
    MOVE_OPTIONS = ["up", "down", "left", "right"]
    GAMMA = 0.9

    def __init__(self):
        self.epsilon = 0.5
        self.num_iterations = 0
        self.n_outputs = len(self.MOVE_OPTIONS)

        self.state_history = []

        self.state_buffer = collections.deque(maxlen=self.BUFFER_SIZE)
        self.reward_buffer = collections.deque(maxlen=self.BUFFER_SIZE)
        self.target_buffer = collections.deque(maxlen=self.BUFFER_SIZE)

        self.network = self.create_network()

    @staticmethod
    def get_state(game, output_format=None):
        state = dict()
        state["raspi_up"] = game.snake.y[0] > game.raspi.y
        state["raspi_down"] = game.snake.y[0] < game.raspi.y
        state["raspi_right"] = game.snake.x[0] < game.raspi.x
        state["raspi_left"] = game.snake.x[0] > game.raspi.x

        wall_up = (game.snake.y[0] / (game.WINDOW_WIDTH - game.SNAKE_STEP)) == 0
        wall_down = (1 - game.snake.y[0] / (game.WINDOW_WIDTH - game.SNAKE_STEP)) == 0
        wall_left = (game.snake.x[0] / (game.WINDOW_WIDTH - game.SNAKE_STEP)) == 0
        wall_right = (
            1 - (game.snake.x[0] / (game.WINDOW_WIDTH - game.SNAKE_STEP))
        ) == 0

        state["obstacle_up"] = wall_up or game.snake.is_body_up()
        state["obstacle_down"] = wall_down or game.snake.is_body_down()
        state["obstacle_left"] = wall_left or game.snake.is_body_left()
        state["obstacle_right"] = wall_right or game.snake.is_body_right()

        state["snake_moving_up"] = game.snake.direction == "up"
        state["snake_moving_down"] = game.snake.direction == "down"
        state["snake_moving_right"] = game.snake.direction == "right"
        state["snake_moving_left"] = game.snake.direction == "left"

        if output_format == "network":
            state = [float(val) for val in state.values()]
            state = np.array(state)[np.newaxis, :]

        return state

    @staticmethod
    def compute_reward(game):
        reward = (
            float(game.snake.has_lost()) * (-20)
            + float(game.snake.has_eaten(game.raspi.x, game.raspi.y)) * 10
        )
        return reward

    def compute_target(self):
        if self.num_iterations > 0:
            q_function_last_state = self.network.predict(self.state_buffer[-2])

            q_function_current_state = self.network.predict(self.state_buffer[-1])

            last_reward = self.reward_buffer[-1]

            target_last_action = last_reward + self.GAMMA * np.max(
                q_function_current_state
            )
            global_target = q_function_last_state
            global_target[0, np.argmax(q_function_last_state)] = target_last_action
        else:
            global_target = np.zeros([1, self.n_outputs])

        return global_target

    def create_network(self):
        input_layer = tf.keras.layers.Input(shape=(self.STATE_SIZE,))
        layer = input_layer

        for i_layer in range(self.N_HIDDEN_LAYERS):
            layer = tf.keras.layers.Dense(self.DENSE_UNITS, activation="relu")(layer)

        output = tf.keras.layers.Dense(
            self.n_outputs, activation=tf.keras.activations.linear
        )(layer)

        network = tf.keras.Model(inputs=input_layer, outputs=output)

        network.compile(
            loss=tf.keras.losses.MeanSquaredError(),
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
        )

        return network

    def train_network(self):
        n_epochs = 10
        if self.num_iterations > self.BATCH_SIZE:

            state_batch = np.squeeze(self.state_buffer)
            current_state_batch = state_batch[0:-1, :]

            reward_batch = np.array(self.reward_buffer)
            reward_batch = reward_batch[1:]

            next_state_batch = state_batch[1:, :]

            for i_epoch in range(n_epochs):
                target_batch = self.network.predict(current_state_batch)
                idx_action = np.argmax(target_batch, axis=1)
                target_batch[np.arange(target_batch.shape[0]), idx_action] = (
                    reward_batch
                    + self.GAMMA
                    * np.max(self.network.predict(next_state_batch), axis=1)
                )

                dataset = tf.data.Dataset.from_tensor_slices(
                    (current_state_batch, target_batch)
                )
                dataset = (
                    dataset.shuffle(200)
                    .prefetch(buffer_size=self.BATCH_SIZE)
                    .batch(self.BATCH_SIZE)
                )

                self.network.fit(dataset, verbose=False, epochs=1)

    def train_network_short_term(self):
        if self.num_iterations > 1:
            last_state = self.state_buffer[-2]
            target = self.target_buffer[-1]

            self.network.fit(x=last_state, y=target, verbose=False, epochs=1)

    def next_move(self, game):

        if random.random() > self.epsilon:
            state = self.get_state(game, output_format="network")
            q_function_output = self.network.predict(state)
            idx_max = np.argmax(q_function_output.ravel())
        else:
            idx_max = random.randint(0, self.n_outputs - 1)

        self.decrease_epsilon()
        next_move = self.MOVE_OPTIONS[idx_max]

        return next_move

    def store(self, game):
        state = Agent.get_state(game, output_format="network")
        self.state_history.append(state)
        self.state_buffer.append(state)

        reward = Agent.compute_reward(game)
        self.reward_buffer.append(reward)

        target = self.compute_target()
        self.target_buffer.append(target)

        self.num_iterations += 1

    def decrease_epsilon(self):
        self.epsilon *= 0.9995

    def summary(self, game):
        print(
            f"Iteration: {game.ind_game}\n"
            f"Epsilon: {self.epsilon}\n"
            f"Score: {game.score}\n"
        )
