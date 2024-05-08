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
import math

from brs import *


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "SORZWE",
        "color": "#00E4FF",  # TODO: Choose color
        "head": "smart-caterpillar",  # TODO: Choose head
        "tail": "weight",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("REPLIT")
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # We've included code to prevent your Battlesnake from moving backwards
    head = game_state["you"]["body"][0]  # Coordinates of your head
    body = game_state["you"]["body"][
        1:]  # Coordinates of each "bodypart" (bodypart after head)

    # Prevent the Battlesnake from moving out of bounds
    # if width is 11, then maximum x coordinate is 10
    # i.e bottomleft corner is (0, 0), topright is (width-1, height-1)
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    if head["x"] + 1 == board_width:
        is_move_safe["right"] = False
    if head["x"] == 0:
        is_move_safe["left"] = False
    if head["y"] == 0:
        is_move_safe["down"] = False
    if head["y"] + 1 == board_height:
        is_move_safe["up"] = False

    # Prevent the Battlesnake from colliding with itself
    # check each bodypart and make sure we will not collide with it in the next move
    for bodypart in body:
        if bodypart["x"] == head["x"] - 1 and bodypart["y"] == head[
                "y"]:  # bodypart is directly left of head, don't move left
            is_move_safe["left"] = False
        if bodypart["x"] == head["x"] + 1 and bodypart["y"] == head[
                "y"]:  # bodypart is directly right of head, don't move right
            is_move_safe["right"] = False
        if bodypart["y"] == head["y"] - 1 and bodypart["x"] == head[
                "x"]:  # bodypart is directly below head, don't move down
            is_move_safe["down"] = False
        if bodypart["y"] == head["y"] + 1 and bodypart["x"] == head[
                "x"]:  # bodypart is directly above head, don't move up
            is_move_safe["up"] = False

    # Prevent the Battlesnake from colliding with other Battlesnakes
    # check every opponent and make sure we do not collide with any of their bodyparts in the next move
    opponents = game_state['board']['snakes']
    for opponent in opponents:
        # dont do anything if it is us
        if opponent["name"] == "SORZWE":
            continue
        # check each opponents bodyparts (including their head)
        for bodypart in opponent["body"]:
            if bodypart["x"] == head["x"] - 1 and bodypart["y"] == head[
                    "y"]:  # bodypart is directly left of head, don't move left
                is_move_safe["left"] = False
            if bodypart["x"] == head["x"] + 1 and bodypart["y"] == head[
                    "y"]:  # bodypart is directly right of head, don't move right
                is_move_safe["right"] = False
            if bodypart["y"] == head["y"] - 1 and bodypart["x"] == head[
                    "x"]:  # bodypart is directly below head, don't move down
                is_move_safe["down"] = False
            if bodypart["y"] == head["y"] + 1 and bodypart["x"] == head[
                    "x"]:  # bodypart is directly above head, don't move up
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

    # Move towards food instead of random, to regain health and survive longer
    # choose whichever safe move is closest to any food
    # TODO: account for all foods, now just first one in list
    foods = game_state['board']['food']
    best_index = -1
    best_distance = math.inf
    moves_to_coord_change_x = {"up": 0, "down": 0, "left": -1, "right": 1}
    moves_to_coord_change_y = {"up": 1, "down": -1, "left": 0, "right": 0}
    for index, move in enumerate(safe_moves):
        next_x = head["x"] + moves_to_coord_change_x[move]
        next_y = head["y"] + moves_to_coord_change_y[move]

        distance = (next_x - foods[0]["x"])**2 + (next_y - foods[0]["y"])**2
        if distance < best_distance:
            best_index = index
            best_distance = distance

    # if we didnt find anything
    if best_index == -1:
        # Choose a random move from the safe ones
        next_move = random.choice(safe_moves)
    # otherwise pick best option
    else:
        next_move = safe_moves[best_index]

    print(f"MOVE {game_state['turn']}: {next_move}")

    # advance the game state using each safe move
    # check the value of that new state
    # pick the one with the highest score
    opponents = [
        snake["name"] for snake in game_state["board"]["snakes"]
        if snake["name"] != "SORZWE"
    ]

    best_move = next_move
    best_score = float('-inf')
    depth = 1  # Depth can be adjusted based on performance needs
    alpha = float('-inf')
    beta = float('inf')

    for move in safe_moves:
        new_state = get_state_from_move(game_state, "SORZWE", move)
        score = brs(alpha, beta, depth, 'MAX', new_state, "SORZWE", opponents)

        if score > best_score:
            best_score = score
            best_move = move

    return {"move": best_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
