import time

from battlesnakegym.snake_gym import BattlesnakeGym
from battlesnakegym.snake import Snake
from battlesnakegym.utils import process_observation, get_real_move_from_oriented
from ppo.ppo import PPO

RENDER = 1
VERBOSE = 0
actions_dict = {
    "up": Snake.UP,
    "right": Snake.RIGHT,
    "down": Snake.DOWN,
    "left": Snake.LEFT,
}

# set up environment and agents
env = BattlesnakeGym(map_size=(11, 11), number_of_snakes=4, verbose=VERBOSE)
observation, _, _, _ = env.reset()
done = False
agents = [PPO("test_agent0", "models/test_agent0.pth"), PPO("test_agent1", "models/test_agent1.pth"), PPO("test_agent2", "models/test_agent2.pth"), PPO("test_agent3", "models/test_agent3.pth")]

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
        actions_to_take.append(actions_dict[get_real_move_from_oriented(action, turns)])

    # get new state
    observation, reward, snakes_dead_dict, info = env.step(actions_to_take)
    done = snakes_dead_dict[0]

    # rendering
    if RENDER:
        env.render()
        time.sleep(0.5)
env.close()