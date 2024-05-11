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
    # Collect info about all snakes
    snakes = game_state['board']['snakes']
    my_snakes = [snake for snake in snakes if snake['name'] == 'SORZWE']
    opponents = [snake for snake in snakes if snake['name'] != 'SORZWE']

    # Prevent the Battlesnake from moving out of bounds
    # if width is 11, then maximum x coordinate is 10
    # i.e bottomleft corner is (0, 0), topright is (width-1, height-1)
    # Process each of your snakes
    moves = {}
    for my_snake in my_snakes:

        head = my_snake['body'][0]
        body = my_snake['body'][1:]  # body excluding the head
        is_move_safe = {"up": True, "down": True, "left": True, "right": True}
        # Boundary collision avoidance
        board_width = game_state['board']['width']
        board_height = game_state['board']['height']
        is_move_safe = check_boundaries(head, board_width, board_height, is_move_safe)


        # Avoid colliding with yourself and your other snake
        for segment in body:
            self_collision_checks(segment, head, is_move_safe)

        # Avoid colliding with the other SORZWE snake
        for other in my_snakes:
            if other['id'] != my_snake['id']:  # Avoid checking against itself
                for segment in other['body']:
                    self_collision_checks(segment, head, is_move_safe)

        # Avoid collisions with all snakes
        for opponent in opponents:
            for segment in opponent['body']:
                self_collision_checks(segment, head, is_move_safe)

        safe_moves = [move for move, safe in is_move_safe.items() if safe]
        if not safe_moves:
            return {"move": "down"}  # Default move if no safe moves

        # want to get the best move
        best_move = random.choice(safe_moves)  # by default make random move
        best_score = float('-inf')
        depth = 2  # Depth can be adjusted based on performance needs, interestingly, having depth too deep will cause
        # too
        # much computation and cause our snake to hit boarder before managed to make calculation (praise the RL ^_^)
        alpha = float('-inf')
        beta = float('inf')

    # advance the game state using each safe move
    # check the value of that new state
    # pick the one with the highest score
        for move in safe_moves:
            new_state = get_state_from_move(game_state, "SORZWE", move)
            score = brs(alpha, beta, depth, 'MAX', new_state, "SORZWE", opponents)

            if score > best_score:
                best_score = score
                best_move = move



        print(f"MOVE {game_state['turn']}: {best_move}")

    """return {"move": best_move}"""
    return {"move": best_move}  # TODO: maybe enough? cuz each code controls 1 snake?


def self_collision_checks(segment, head, is_move_safe):
    if (segment["x"], segment["y"]) == (head["x"] - 1, head["y"]):
        is_move_safe["left"] = False
    if (segment["x"], segment["y"]) == (head["x"] + 1, head["y"]):
        is_move_safe["right"] = False
    if (segment["x"], segment["y"]) == (head["x"], head["y"] - 1):
        is_move_safe["down"] = False
    if (segment["x"], segment["y"]) == (head["x"], head["y"] + 1):
        is_move_safe["up"] = False


def check_boundaries(head, board_width, board_height, is_move_safe):
    if head["x"] + 1 == board_width:
        is_move_safe["right"] = False
    if head["x"] == 0:
        is_move_safe["left"] = False
    if head["y"] == 0:
        is_move_safe["down"] = False
    if head["y"] + 1 == board_height:
        is_move_safe["up"] = False
    return is_move_safe


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
