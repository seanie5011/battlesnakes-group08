import numpy as np
import random

def process_observation(_observation, current_snake_index):
    """
    Processes the observation from the gym to be oriented such that player current_snake_index is facing up.
    Assumes a 4-player 11x11 game.
    """

    observation = _observation.copy().reshape(11, 11, 5)

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

def get_safe_moves_from_observation(observation, current_snake_index):
    """
    A simple controller that simply only takes safe moves, killing enemies if it happens upon them.
    """
    # check we are even alive
    if len(np.argwhere(observation[:,:,current_snake_index + 1] == 1)) <= 0:
        return 1

    # assume all moves are valid at the start
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}
    moves_dict = {"up": 0, "down": 1, "left": 2, "right": 3}

    # fix observation
    observation = observation.reshape(11, 11, 5)

    # get our head and body
    head = np.argwhere(observation[:,:,current_snake_index + 1] == 1)[0]
    body = np.argwhere(observation[:,:,current_snake_index + 1] > 1)
    length = len(body) + 1  # +1 for head

    # Prevent the Battlesnake from moving out of bounds
    # if width is 11, then maximum x coordinate is 10
    # for this, topleft is 0,0 - note that x is index 1 and y is index 0
    board_width = observation.shape[1]
    board_height = observation.shape[0]
    if head[1] + 1 == board_width:
        is_move_safe["right"] = False
    if head[1] == 0:
        is_move_safe["left"] = False
    if head[0] == 0:
        is_move_safe["up"] = False
    if head[0] + 1 == board_height:
        is_move_safe["down"] = False

    # Prevent the Battlesnake from colliding with itself
    # check each bodypart and make sure we will not collide with it in the next move
    for bodypart in body:
        if bodypart[1] == head[1] - 1 and bodypart[0] == head[0]:  # bodypart is directly left of head, don't move left
            is_move_safe["left"] = False
        if bodypart[1] == head[1] + 1 and bodypart[0] == head[0]:  # bodypart is directly right of head, don't move right
            is_move_safe["right"] = False
        if bodypart[0] == head[0] - 1 and bodypart[1] == head[1]:  # bodypart is directly above head, don't move up
            is_move_safe["up"] = False
        if bodypart[0] == head[0] + 1 and bodypart[1] == head[1]:  # bodypart is directly below head, don't move down
            is_move_safe["down"] = False

    # 0 and 1 are teammates, 2 and 3 are teammates
    teammate_dict = {
        0: 1,
        1: 0,
        2: 3,
        3: 2
    }
    teammate_index = teammate_dict[current_snake_index]
    # keep track of which indices we have looked at
    indices = [0, 1, 2, 3]
    indices.remove(current_snake_index)
    indices.remove(teammate_index)
    
    # Prevent the Battlesnake from colliding with its teammate
    # check our teammate and make sure we do not collide with any of their bodyparts (including head) in the next move
    body_ = np.argwhere(observation[:,:,teammate_index + 1] >= 1)
    for bodypart in body_:
        if bodypart[1] == head[1] - 1 and bodypart[0] == head[0]:  # bodypart is directly left of head, don't move left
            is_move_safe["left"] = False
        if bodypart[1] == head[1] + 1 and bodypart[0] == head[0]:  # bodypart is directly right of head, don't move right
            is_move_safe["right"] = False
        if bodypart[0] == head[0] - 1 and bodypart[1] == head[1]:  # bodypart is directly above head, don't move up
            is_move_safe["up"] = False
        if bodypart[0] == head[0] + 1 and bodypart[1] == head[1]:  # bodypart is directly below head, don't move down
            is_move_safe["down"] = False

    # Prevent the Battlesnake from colliding with other Battlesnakes
    # check every opponent and make sure we do not collide with any of their bodyparts (except head if they are smaller than us) in the next move
    opponents = [np.argwhere(observation[:,:,indices.pop() + 1] >= 1), np.argwhere(observation[:,:,indices.pop() + 1] >= 1)]
    lengths = [len(opponents[0]), len(opponents[1])]
    for opponent in opponents:
        # check each opponents bodypart (including their head)
        for i, bodypart in enumerate(opponent):
            # if not looking at head and they are bigger than us
            if not (i == 0 and lengths[i] < length):
                if bodypart[1] == head[1] - 1 and bodypart[0] == head[0]:  # bodypart is directly left of head, don't move left
                    is_move_safe["left"] = False
                if bodypart[1] == head[1] + 1 and bodypart[0] == head[0]:  # bodypart is directly right of head, don't move right
                    is_move_safe["right"] = False
                if bodypart[0] == head[0] - 1 and bodypart[1] == head[1]:  # bodypart is directly above head, don't move up
                    is_move_safe["up"] = False
                if bodypart[0] == head[0] + 1 and bodypart[1] == head[1]:  # bodypart is directly below head, don't move down
                    is_move_safe["down"] = False

    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)
    
    if len(safe_moves) == 0:
        return moves_dict["down"]

    # want to get the best move
    best_move = random.choice(safe_moves)  # by default make random move
    return moves_dict[best_move]

def get_observation_from_state(game_state: dict, my_name: str, teammates_name: str, enemy_ids: list[str]):
    # create observation as 11x11 grid with 5 channels
    observation = np.zeros((11, 11, 5), dtype=np.uint8)

    # apply food
    for food_dict in game_state["board"]["food"]:
        y, x = food_dict["x"], food_dict["y"]  # indices swap for numpy array
        observation[x,y,0] = 1

    # apply each snake
    for snake in game_state["board"]["snakes"]:
        # get the index for the observation
        # we are always 0
        # teammate is always 1
        # enemies are kept constant
        if snake["name"] == my_name:
            index = 1
        elif snake["name"] == teammates_name:
            index = 2
        elif snake["id"] == enemy_ids[0]:
            index = 3
        elif snake["id"] == enemy_ids[1]:
            index = 4
        
        # now apply each snakes bodypart
        for body_index, bodypart in enumerate(snake["body"]):
            y, x = bodypart["x"], bodypart["y"]  # indices swap for numpy array
            observation[x,y,index] = body_index + 1  # head is 1, each subsequent bodypart is +1
        # make sure head is set to 1
        y, x = snake["head"]["x"], snake["head"]["y"]
        observation[x,y,index] = 1
        # make sure neck is set to 2
        y, x = snake["body"][1]["x"], snake["body"][1]["y"]
        observation[x,y,index] = 1

    # flip up down to be correct
    observation = np.flipud(observation)

    # reshape to 5x11x11 when done
    return observation.reshape(5, 11, 11).copy()