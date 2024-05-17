import numpy as np
import matplotlib.pyplot as plt

from battlesnakegym.snake_gym import BattlesnakeGym
from battlesnakegym.snake import Snake
from battlesnakegym.utils import process_observation, get_real_move_from_oriented
from ppo.ppo import PPO

RENDER = 0
VERBOSE = 0
actions_dict = {
    "up": Snake.UP,
    "right": Snake.RIGHT,
    "down": Snake.DOWN,
    "left": Snake.LEFT,
}

if __name__ == "__main__":
    # get environment and agent
    env = BattlesnakeGym(map_size=(11, 11), number_of_snakes=4, verbose=VERBOSE)
    agents = [PPO("agent0", "models/agent0.pth"), PPO("agent1", "models/agent1.pth"), PPO("agent2", "models/agent2.pth"), PPO("agent3", "models/agent3.pth")]

    # set properties
    n_games = 1000

    # keeping track
    learning_steps = np.zeros((4,))
    n_steps = np.zeros((4,))
    best_score = np.full((4,), -100.0)
    avg_score = np.full((4,), -100.0)
    score_history = [[], [], [], []]

    # play all games
    for k in range(n_games):
        # reset
        observation, _, _, _ = env.reset()
        done = False
        score = np.zeros((4,))

        while not done:
            # holders
            action_list = []
            action_probs_list = []
            value_list = []
            actions_to_take = []
            for i, agent in enumerate(agents):
                # get agents action
                observation, turns = process_observation(observation.copy(), i)
                action, action_probs, value, _ = agent.predict(observation)
                # add above to lists
                action_list.append(action)
                action_probs_list.append(action_probs)
                value_list.append(value)
                # process the action we took to get the action in gym coords
                actions_to_take.append(actions_dict[get_real_move_from_oriented(action, turns)])

            # get new state
            observation, reward, snakes_alive, info = env.step(actions_to_take)
            done = (np.sum(snakes_alive) <= 1)  # if 1 or less snakes are alive, done

            # for every agent
            for i, agent in enumerate(agents):
                # update and process observation for this agent
                n_steps[i] += 1
                score[i] += reward[i]
                observation, _ = process_observation(observation.copy(), i)

                # store this in memory
                agent.remember(observation, action_list[i], action_probs_list[i], value_list[i], reward[i], done)

                # learn every now and then
                if n_steps[i] % agent.buffer_size == 0:
                    agent.learn()
                    learning_steps[i] += 1

        # for every agent
        for i, agent in enumerate(agents):
            # end of episode, set variables
            score_history[i].append(score[i])
            avg_score[i] = np.mean(score_history[i][-100:])  # average over previous 100 games
            if avg_score[i] > best_score[i] and (k > 100 or k == 1):
                best_score[i] = avg_score[i]
                agent.save_model(n_steps[i])
        
            print(f"agent: {agent.label}; episode: {k}; score: {score[i]}; avg score: {avg_score[i]}; time steps: {n_steps[i]}; learning steps: {learning_steps[i]}")
    
    # plot results
