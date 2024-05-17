import numpy as np
from battlesnakegym.utils import process_observation

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

    # flip up down to be correct
    observation = np.flipud(observation)

    # reshape to 5x11x11 when done
    return observation.reshape(5, 11, 11).copy()