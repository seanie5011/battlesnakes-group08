import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from battlesnakegym import snake_gym

# plot configurations
cmap = ListedColormap(["w", "r", "g", "k"])

def plot_observation(observation: list):
    # change all food (first layer) from a 1 to a 2 (for plotting)
    # likewise change everything greater than 1 in snakes to 3
    temp = observation.copy()
    temp[:,:,0][temp[:,:,0] == 1] = 2
    temp[:,:,1:][temp[:,:,1:] > 1] = 3
    # sum everything to put all layers on one
    total_observation = np.sum(temp, axis=2)
    # plot with the color map as above (0-5 left-right)
    plt.matshow(total_observation, cmap=cmap)

def get_number_turns(observation, snake_index) -> int:
    """
    Returns how many times we must turn 90-degrees so that snake at snake_index is facing upwards.
    """
    # get this snakes particular 11x11
    # plus 1 as the zero index is food
    snake_observation = observation[:,:,snake_index + 1].copy()
    # if there are no heads or necks, nothing to do
    if not (np.any(snake_observation == 2) and np.any(snake_observation == 1)):
        return None
    
    # the head is always labelled 1 and neck always 2
    # note that the x and ys are swapped due to the nature of python indexing
    head_index = np.argwhere(snake_observation == 1).flatten()
    head_x = head_index[1]
    head_y = head_index[0]
    neck_index = np.argwhere(snake_observation == 2).flatten()
    neck_x = neck_index[1]
    neck_y = neck_index[0]

    # now checking where they are relative to each other we can figure out the orientation
    # note that we return the number of times we should rotate 90degrees to be facing up
    if (head_x == neck_x):
        if (head_y < neck_y):
            # up
            return 0
        elif (head_y > neck_y):
            # down
            return 2
    elif (head_y == neck_y):
        if (head_x < neck_x):
            # left
            return 3
        elif (head_x > neck_x):
            # right
            return 1

if __name__ == "__main__":
    # gym
    env = snake_gym.BattlesnakeGym(map_size=(11, 11), number_of_snakes=4)

    # reset and take action
    observation, _, _, _ = env.reset()
    observation, _, _, _ = env.step(env.action_space.sample())
    plot_observation(observation)

    # check if we must rotate to make snake 0 face up
    turns = get_number_turns(observation, 0)
    # rotate observation if so
    if not turns == None and turns != 0:
        observation = np.rot90(observation, turns).copy()
        plot_observation(observation)

    # close gym and plot
    env.close()
    plt.show()