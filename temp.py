import numpy as np
import matplotlib.pyplot as plt
from battlesnakegym.utils import process_observation, sum_processing

# example game state, taken from 4v4 online
game_state = {'game': {'id': '9c0eacd4-08d2-4d95-8031-8f74ddb414ee', 'ruleset': {'name': 'standard', 'version': 'v1.2.3', 'settings': {'foodSpawnChance': 15, 'minimumFood': 1, 'hazardDamagePerTurn': 0, 'hazardMap': '', 'hazardMapAuthor': '', 'royale': {'shrinkEveryNTurns': 0}, 'squad': {'allowBodyCollisions': False, 'sharedElimination': False, 'sharedHealth': False, 'sharedLength': False}}}, 'map': 'standard', 'timeout': 500, 'source': 'custom'}, 'turn': 94, 'board': {'height': 11, 'width': 11, 'snakes': [{'id': 'gs_tCJhwkBvVCycc4dB7x9fQHvC', 'name': 'SORZWE', 'latency': '108', 'health': 98, 'body': [{'x': 1, 'y': 1}, {'x': 0, 'y': 1}, {'x': 0, 'y': 0}, {'x': 1, 'y': 0}, {'x': 2, 'y': 0}, {'x': 2, 'y': 1}, {'x': 3, 'y': 1}], 'head': {'x': 1, 'y': 1}, 'length': 7, 'shout': '', 'squad': '', 'customizations': {'color': '#00e4ff', 'head': 'smart-caterpillar', 'tail': 'weight'}}, {'id': 'gs_VgvhG9TW4dgJC34VqkyS3KyS', 'name': 'SORZWE2', 'latency': '108', 'health': 94, 'body': [{'x': 0, 'y': 6}, {'x': 0, 'y': 5}, {'x': 0, 'y': 4}, {'x': 0, 'y': 3}, {'x': 0, 'y': 2}, {'x': 1, 'y': 2}, {'x': 1, 'y': 3}, {'x': 1, 'y': 4}], 'head': {'x': 0, 'y': 6}, 'length': 8, 'shout': '', 'squad': '', 'customizations': {'color': '#00e4ff', 'head': 'smart-caterpillar', 'tail': 'weight'}}], 'food': [{'x': 10, 'y': 8}, {'x': 9, 'y': 4}, {'x': 9, 'y': 7}, {'x': 10, 'y': 2}, {'x': 9, 'y': 1}, {'x': 10, 'y': 3}, {'x': 9, 'y': 6}, {'x': 5, 'y': 2}, {'x': 5, 'y': 0}], 'hazards': []}, 'you': {'id': 'gs_VgvhG9TW4dgJC34VqkyS3KyS', 'name': 'SORZWE2', 'latency': '108', 'health': 94, 'body': [{'x': 0, 'y': 6}, {'x': 0, 'y': 5}, {'x': 0, 'y': 4}, {'x': 0, 'y': 3}, {'x': 0, 'y': 2}, {'x': 1, 'y': 2}, {'x': 1, 'y': 3}, {'x': 1, 'y': 4}], 'head': {'x': 0, 'y': 6}, 'length': 8, 'shout': '', 'squad': '', 'customizations': {'color': '#00e4ff', 'head': 'smart-caterpillar', 'tail': 'weight'}}}

if __name__ == "__main__":
    # figure out who we are and who teammate is, use ids for enemies as they might have same name
    my_name = game_state["you"]["name"]
    teammates_name = "SORZWE2" if my_name == "SORZWE" else "SORZWE"
    enemy_ids = [snake["id"] for snake in game_state["board"]["snakes"] if snake["name"] != my_name and snake["name"] != teammates_name]

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
    
    # print("food")
    # print(observation[:,:,0])
    # print(f"me: {my_name}")
    # print(observation[:,:,1])
    # print(f"teammate: {teammates_name}")
    # print(observation[:,:,2])
    # print(f"enemy 0: {enemy_ids[0]}")
    # print(observation[:,:,3])
    # print(f"enemy 1: {enemy_ids[1]}")
    # print(observation[:,:,4])

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
    observation, turns = process_observation(observation, 1)
    print(f"turns: {turns}")
    observation = sum_processing(observation)
    plt.matshow(palette[observation])  # using the palette to provide the colors
    plt.show()