import time
import numpy as np

from battlesnakegym.snake_gym import BattlesnakeGym
from battlesnakegym.snake import Snake
from battlesnakegym.utils import process_observation, get_real_move_from_oriented
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
env = BattlesnakeGym(map_size=(11, 11), number_of_snakes=4, verbose=VERBOSE)
observation, _, _, _ = env.reset()
done = False
agents = [PPO("agent0", "models/agent0.pth"), PPO("agent1", "models/agent1.pth"), PPO("agent2", "models/agent2.pth"), PPO("agent3", "models/agent3.pth")]

# rendering
if RENDER:
    env.render()
    time.sleep(0.5)

while not done:
    # holders
    actions_to_take = []
    for i, agent in enumerate(agents):
        # get agents action
        observation, turns = process_observation(observation.copy(), i)
        action, _, _, _ = agent.predict(observation)
        # process the action we took to get the action in gym coords
        print(f"agent: {i}; action: {action}; turns: {turns}; real: {get_real_move_from_oriented(action, turns)}; dict: {actions_dict[get_real_move_from_oriented(action, turns)]}")
        actions_to_take.append(actions_dict[get_real_move_from_oriented(action, turns)])

    # get new state
    observation, reward, snakes_alive, info = env.step(actions_to_take)
    done = (np.sum(snakes_alive) <= 1)  # if 1 or less snakes are alive, done

    # rendering
    if RENDER:
        env.render()
        time.sleep(0.5)
env.close()