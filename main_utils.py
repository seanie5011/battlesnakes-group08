import numpy as np

def process_observation(_observation, current_snake_index):
    """
    Processes the observation from the gym to be oriented such that player current_snake_index is facing up.
    Assumes a 4-player 11x11 game.
    """

    observation = _observation.copy()

    # get this snakes particular 11x11
    # plus 1 as the zero index is food
    snake_observation = observation[:,:,current_snake_index + 1].copy()
    # check if we might need to turn this (orientation, always want to orient up)
    # if there are no heads or necks, nothing to do
    turns = 0
    if np.any(snake_observation == 2) and np.any(snake_observation == 1):
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
                turns = 0
            elif (head_y > neck_y):
                # down
                turns = 2
        elif (head_y == neck_y):
            if (head_x < neck_x):
                # left
                turns = 3
            elif (head_x > neck_x):
                # right
                turns = 1
        
        # only turn if needed
        if turns != 0:
            observation = np.rot90(observation, turns).copy()
    
    # now reorganise so that this snake is at index 1, its teammate at index 2, enemies at index 3 and 4
    # if we are snake 0, dont do anything
    if not current_snake_index == 0:
        # keep track of which indices we have looked at
        indices = [0, 1, 2, 3]
        # know whos teammates with who
        teammate_dict = {
            0: 1,
            1: 0,
            2: 3,
            3: 2
        }  # 0 and 1 are teammates, 2 and 3 are teammates
        # use a temporary dictionary for now
        temp = observation.copy()
        temp[:,:,1] = observation[:,:,current_snake_index + 1]  # set us to index 0
        indices.remove(current_snake_index)
        temp[:,:,2] = observation[:,:,teammate_dict[current_snake_index] + 1]  # set teammate to index 1
        indices.remove(teammate_dict[current_snake_index])
        temp[:,:,3] = observation[:,:,indices.pop(0) + 1]  # will be either 0 or 2
        temp[:,:,4] = observation[:,:,indices.pop(0) + 1]  # will be either 1 or 3
        # set the observation
        observation = temp.copy()
    
    return observation.reshape(5, 11, 11), turns

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

def get_real_move_from_oriented(move: int, turns: int) -> str:
    """
    Returns a move in real space depending on the number of turns taken.

    Inputs:
        move (int): 0, 1 or 2 - forward, left, right
        turns (int): how many times the observation was rotated 90-degrees
    Outputs:
        str: "up", "down", "left", or "right"
    """
    # all moves we can take
    moves = ["up", "right", "down", "left"]

    # conversion from move (input) to index
    move_conversion = {
        0: 0,
        1: -1,
        2: 1,
    }
    # use this with number of turns to get index in list
    move_index = (move_conversion[move] + turns) % len(moves)
    return moves[move_index]