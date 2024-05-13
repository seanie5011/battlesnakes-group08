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
    # assume all moves are valid at the start
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # get our head and body
    my_id = game_state["you"]["id"]  # TODO: will this work?????????????
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
        if snake["id"] != my_id:  # skip self, check other snakes
            is_teammate = (snake["name"] == "SORZWE") and (snake["id"] != my_id)  # TODO mb need it later
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
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(
            f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    # get all other snakes
    opponents = []
    for snake in all_snakes:
        if snake["id"] != my_id:
            opponents.append(snake)  # TODO maybe entire object needed??

    # want to get the best move
    best_move = random.choice(safe_moves)  # by default make random move
    best_score = float('-inf')
    depth = 2  # Depth can be adjusted based on performance needs, interestingly, having depth too deep will cause too
    # much computation and cause our snake to hit boarder before managed to make calculation (praise the RL ^_^)
    alpha = float('-inf')
    beta = float('inf')
    print("check" , is_move_safe)
    # advance the game state using each safe move
    # check the value of that new state
    # pick the one with the highest score

    for move in list(safe_moves):  # Use list to copy for safe iteration
        new_state = get_state_from_move(game_state, my_id, move)
        simulated_head = new_state["you"]["body"][0]
        simulated_body = new_state["you"]["body"]
        simulated_tail = new_state["you"]["body"][-1]
        if not can_reach_tail(new_state, simulated_head, simulated_tail, simulated_body, move, is_move_safe):
            is_move_safe[move] = False
            safe_moves.remove(move)

    print("can reach tail move", is_move_safe)
    for move in safe_moves:
        score = brs(alpha, beta, depth, 'MAX', game_state, my_id, opponents, is_move_safe)

        """if score > best_score:
            best_score = score
            best_move = move"""
        best_move = random.choice(safe_moves)

    print(f"MOVE {game_state['turn']}: {best_move}")

    return {"move": best_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
