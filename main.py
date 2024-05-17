# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing
from brs import *


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "SORZWE",
        "color": "#00E4FF",
        "head": "smart-caterpillar",
        "tail": "weight",
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    # print(game_state)
    # assume all moves are valid at the start
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # get our name and our teammates name
    my_name = game_state["you"]["name"]
    my_length = len(game_state["you"]["body"])
    teammates_name = "SORZWE2" if my_name == "SORZWE" else "SORZWE"

    # get our head and body
    my_id = game_state["you"]["id"]
    head = game_state["you"]["body"][0]  # Coordinates of your head
    body = game_state["you"]["body"][1:-1]  # TODO: (bodypart after head, tail not needed??)
    all_snakes = game_state['board']['snakes']
    # Prevent the Battlesnake from moving out of bounds
    # if width is 11, then maximum x coordinate is 10
    # i.e bottomleft corner is (0, 0), topright is (width-1, height-1)
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    tail = game_state["you"]["body"][-1]

    if head["x"] + 1 == board_width:
        is_move_safe["right"] = False
    if head["x"] == 0:
        is_move_safe["left"] = False
    if head["y"] == 0:
        is_move_safe["down"] = False
    if head["y"] + 1 == board_height:
        is_move_safe["up"] = False

    # Self-collision avoidance
    for bodypart in body:
        if (bodypart["x"], bodypart["y"]) == (head["x"] - 1, head["y"]):
            is_move_safe["left"] = False
        if (bodypart["x"], bodypart["y"]) == (head["x"] + 1, head["y"]):
            is_move_safe["right"] = False
        if (bodypart["x"], bodypart["y"]) == (head["x"], head["y"] - 1):
            is_move_safe["down"] = False
        if (bodypart["x"], bodypart["y"]) == (head["x"], head["y"] + 1):
            is_move_safe["up"] = False

    # Avoid collisions with all snakes, including another "SORZWE"
    for snake in all_snakes:
        if snake["name"] == my_name:
            continue
        is_teammate = (snake["name"] == "SORZWE") or (snake["name"] == "SORZWE2")
        for bodypart in snake["body"]:
            if (bodypart["x"], bodypart["y"]) == (head["x"] - 1, head["y"]):
                is_move_safe["left"] = False
            if (bodypart["x"], bodypart["y"]) == (head["x"] + 1, head["y"]):
                is_move_safe["right"] = False
            if (bodypart["x"], bodypart["y"]) == (head["x"], head["y"] - 1):
                is_move_safe["down"] = False
            if (bodypart["x"], bodypart["y"]) == (head["x"], head["y"] + 1):
                is_move_safe["up"] = False

    # Are there any safe moves left?
    safe_moves_back_up = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves_back_up.append(move)

    # TODO: if tree depth and heuristic can work properly, we wont need this then
    non_traversable = set()
    for snake in all_snakes:
        other_snake_head = snake["body"][0]
        if snake["name"] == teammates_name or (snake["name"] != my_name and len(snake["body"]) >= my_length):
            non_traversable.add((other_snake_head['x'] + 1, other_snake_head['y']))
            non_traversable.add((other_snake_head['x'] - 1, other_snake_head['y']))
            non_traversable.add((other_snake_head['x'], other_snake_head['y'] + 1))
            non_traversable.add((other_snake_head['x'], other_snake_head['y'] - 1))

    possible_moves = {
        "up": (head['x'], head['y'] + 1),
        "down": (head['x'], head['y'] - 1),
        "left": (head['x'] - 1, head['y']),
        "right": (head['x'] + 1, head['y'])
    }

    for direction, (x, y) in possible_moves.items():
        if (x, y) in non_traversable:
            is_move_safe[direction] = False

    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    # Fallback strategy if no moves are safe
    if len(safe_moves) == 0:
        if safe_moves_back_up:
            chosen_move = random.choice(safe_moves_back_up)
            print(f"MOVE {game_state['turn']}: No safe moves detected! Fallback to backup move: {chosen_move}")
            return {"move": chosen_move}
        else:
            print(f"MOVE {game_state['turn']}: No moves available! Defaulting to 'down'")
            return {"move": "down"}

    # get all other snakes
    opponents = []
    for snake in all_snakes:
        # if snake["name"] == teammates_name or snake["name"] != my_name:
        if snake["name"] != my_name:
            opponents.append(snake)  # TODO maybe entire object needed??

    # Determine valid safe moves where the snake can still reach its tail
    valid_safe_moves = []
    # print("safe moves: ", safe_moves)
    for move in safe_moves:
        new_state, snake_index = get_state_from_move(game_state, my_name, move)
        simulated_head = new_state["board"]["snakes"][snake_index]["body"][0]
        simulated_body = new_state["board"]["snakes"][snake_index]["body"]
        simulated_tail = new_state["board"]["snakes"][snake_index]["body"][-1]
        if can_reach_tail(new_state, simulated_head, simulated_tail):
            valid_safe_moves.append(move)

    """print("Valid safe moves:", valid_safe_moves)
    x = simulate_moves_and_check_reachability(game_state, my_name)
    print("Valid safe moves again: ", x, "++++++++++++++++++++++++++++++++++++")"""
    # Evaluate each valid safe move using BRS
    best_move = random.choice(valid_safe_moves) if valid_safe_moves else random.choice(safe_moves) \
        if safe_moves else random.choice(safe_moves_back_up)
    best_score = -np.inf
    depth = 3  # Adjust depth based on performance needs
    alpha = -np.inf
    beta = np.inf

    for move in valid_safe_moves:
        new_state, _ = get_state_from_move(game_state, my_name, move)
        score = brs(alpha, beta, depth, 'MAX', new_state, my_name, opponents, is_move_safe)
        # print("getting score ??????? ", score)
        if score > best_score:
            # print("getting score update", score)
            best_score = score
            best_move = move

    print("Move " + str(game_state["turn"]) + ": " + best_move + " for " + my_name)
    return {"move": best_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
