import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from battlesnakegym import snake_gym
from battlesnakegym import snake

# plot configurations
cmap = ListedColormap(["w", "k", "r", "b", "y", "g"])

def plot_observation(observation):
    # change all food (first layer) from a 1 to a 2 (for plotting)
    temp = observation.copy()
    temp[:,:,0][temp[:,:,0] == 1] = 2
    # sum everything to put all layers on one
    total_observation = np.sum(temp, axis=2)
    # plot with the color map as above (0-5 left-right)
    plt.matshow(total_observation, cmap=cmap)

if __name__ == "__main__":
    # gym
    env = snake_gym.BattlesnakeGym(map_size=(11, 11), number_of_snakes=4)

    # reset and take action
    observation, _, _, _ = env.reset()
    observation, _, _, _ = env.step([snake.Snake.UP, snake.Snake.UP, snake.Snake.UP, snake.Snake.UP])
    plot_observation(observation)

    # flip it
    observation = np.rot90(observation, 2).copy()
    plot_observation(observation)

    # close gym and plot
    env.close()
    plt.show()