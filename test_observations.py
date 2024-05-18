import numpy as np
import matplotlib.pyplot as plt
from battlesnakegym.snake_gym import BattlesnakeGym
from battlesnakegym.snake import Snake
from main_utils import process_observation, sum_processing, get_real_move_from_oriented

# plot configurations
palette = np.array([[255, 255, 255],  # white
                    [255,   0,   0],  # red
                    [  0, 125,   0],  # dark green
                    [  0, 255,   0],  # green
                    [  0,   0, 125],  # dark blue
                    [  0,   0, 255],  # blue
                    [125, 125,   0],  # dark yellow
                    [255, 255,   0],  # yellow
                    [125,   0, 125],  # dark purple
                    [255,   0, 255],  # purple
    ])

if __name__ == "__main__":
    # gym
    snake_positions = [(2, 2), (8, 8), (2, 8), (8, 2)]
    env = BattlesnakeGym(map_size=(11, 11), number_of_snakes=4, snake_spawn_locations=snake_positions)

    # reset and process initial observation
    observation, _, _, _ = env.reset()
    observation, _ = process_observation(observation, 0)
    observation = sum_processing(observation)
    plt.matshow(palette[observation])  # using the palette to provide the colors

    # perform some actions
    for _ in range(4):
        # get the observation and process it
        observation, _, _, _ = env.step(env.action_space.sample())
        observation, turns = process_observation(observation, 0)  # we will show the observation according to player 0 (green)
        observation = sum_processing(observation)
        plt.matshow(palette[observation])

    # close gym and plot
    env.close()
    plt.show()