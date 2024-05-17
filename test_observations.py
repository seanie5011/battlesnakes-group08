import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from battlesnakegym.snake_gym import BattlesnakeGym
from battlesnakegym.utils import process_observation, sum_processing

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
    env = BattlesnakeGym(map_size=(11, 11), number_of_snakes=4)

    # reset and process initial observation
    observation, _, _, _ = env.reset()
    observation, _ = process_observation(observation, 0)
    observation = sum_processing(observation)
    plt.matshow(palette[observation])  # using the palette to provide the colors

    # perform some actions
    for _ in range(5):
        # get the observation and process it
        observation, _, _, _ = env.step(env.action_space.sample())
        observation, _ = process_observation(observation, 0)
        observation = sum_processing(observation)
        plt.matshow(palette[observation])

    # close gym and plot
    env.close()
    plt.show()