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
from main_utils import get_observation_from_state, process_observation, get_real_move_from_oriented
from ppo.ppo import PPO

# Get RL model
model = PPO("agent0", "models/agent_19052024_114840.pth")

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
    # get our name and our teammates name
    my_name = game_state["you"]["name"]
    teammates_name = "SORZWE2" if my_name == "SORZWE" else "SORZWE"
    enemy_ids = [snake["id"] for snake in game_state["board"]["snakes"] if snake["name"] != my_name and snake["name"] != teammates_name]

    # transform board into observation
    observation = get_observation_from_state(game_state, my_name, teammates_name, enemy_ids)
    observation, turns = process_observation(observation.copy(), 0)  # this snake will always be 0
    # Run inference on RL model
    action, _, _, _ = model.predict(observation)
    move_rl = get_real_move_from_oriented(action, turns)

    print("Move " + str(game_state["turn"]) + ": " + move_rl + " for " + my_name)

    return {"move": move_rl}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
