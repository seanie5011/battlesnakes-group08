import time
import numpy as np

from battlesnakegym.rewards import TeamRewards
from battlesnakegym.snake_gym import BattlesnakeGym
from battlesnakegym.snake import Snake
from main_utils import process_observation, get_real_move_from_oriented, get_safe_moves_from_observation
from ppo.ppo import PPO

RENDER = 1
VERBOSE = 0
actions_dict = {
    "up": Snake.UP,
    "down": Snake.DOWN,
    "left": Snake.LEFT,
    "right": Snake.RIGHT,
}

# set up environment and agents
env = BattlesnakeGym(map_size=(11, 11), number_of_snakes=4, rewards=TeamRewards(), is_teammate_game=True, verbose=VERBOSE)
observation, _, _, _ = env.reset()
done = False
agent = PPO("agent0", "models/agent_104646_19052024.pth")
enemy = PPO("agent1", "models/agent_104646_19052024.pth")

# rendering
if RENDER:
    env.render()
    time.sleep(0.5)

while not done:
    # holder for all actions we take
    actions_to_take = []

    # get our agents action
    observation_, turns = process_observation(observation.copy(), 0)
    get_safe_moves_from_observation(observation_)
    action, _, _, _ = agent.predict(observation_)
    # process the action we took to get the action in gym coords
    actions_to_take.append(actions_dict[get_real_move_from_oriented(action, turns)])
    print(f"agent a; turns {turns}; action: {action}; result: {get_real_move_from_oriented(action, turns)}; took: {actions_dict[get_real_move_from_oriented(action, turns)]}")

    # get our teammates action (just us but different observation)
    observation_, turns = process_observation(observation.copy(), 1)
    action, _, _, _ = agent.predict(observation_)
    actions_to_take.append(actions_dict[get_real_move_from_oriented(action, turns)])
    print(f"agent b; turns {turns}; action: {action}; result: {get_real_move_from_oriented(action, turns)}; took: {actions_dict[get_real_move_from_oriented(action, turns)]}")

    # get the enemies actions (them and teammate)
    observation_, turns = process_observation(observation.copy(), 2)
    action, _, _, _ = enemy.predict(observation_)
    actions_to_take.append(actions_dict[get_real_move_from_oriented(action, turns)])
    print(f"agent c; turns {turns}; action: {action}; result: {get_real_move_from_oriented(action, turns)}; took: {actions_dict[get_real_move_from_oriented(action, turns)]}")
    observation_, turns = process_observation(observation.copy(), 3)
    action, _, _, _ = enemy.predict(observation_)
    actions_to_take.append(actions_dict[get_real_move_from_oriented(action, turns)])
    print(f"agent d; turns {turns}; action: {action}; result: {get_real_move_from_oriented(action, turns)}; took: {actions_dict[get_real_move_from_oriented(action, turns)]}")

    # get new state
    observation, reward, snakes_alive, info = env.step(actions_to_take)
    # done if (only one snake alive) or (only two snakes are left and us and teammate are both either dead or alive)
    done = (np.sum(snakes_alive) <= 1 or (np.sum(snakes_alive) == 2 and snakes_alive[0] == snakes_alive[1]))

    # rendering
    if RENDER:
        env.render()
        time.sleep(0.5)
env.close()