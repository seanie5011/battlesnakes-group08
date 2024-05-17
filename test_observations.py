import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from battlesnakegym.snake_gym import BattlesnakeGym
from battlesnakegym.utils import process_observation

def sum_processing(observation):
    """
    Processes the observation from the gym to be a single 11x11 array.
    Assumes a 4-player 11x11 game.

    Where:
        0 denotes free space
        1 denotes food
        2 denotes player 0s head
        3 denotes player 0s body
        4 denotes player 1s head
        5 denotes player 1s body
        6 denotes player 2s head
        7 denotes player 2s body
        8 denotes player 3s head
        9 denotes player 3s body
    """
    # reshape back to (11, 11, 5)
    observation = observation.copy().reshape(11, 11, 5)
    # now process so that players values are as detailed above
    # four snakes
    for snake_index in range(4):
        # get this snakes
        temp = observation[:,:,snake_index + 1].copy()
        # set head and body
        temp[observation[:,:,snake_index + 1] == 1] = 2 + 2 * snake_index
        temp[observation[:,:,snake_index + 1] > 1] = 3 + 2 * snake_index
        # set back
        observation[:,:,snake_index + 1] = temp
    
    # sum everything to put all layers on one
    return np.sum(observation, axis=2)

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