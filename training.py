import numpy as np
import random
import datetime

from battlesnakegym.rewards import TeamRewards, GameTeamRewards
from battlesnakegym.snake_gym import BattlesnakeGym
from battlesnakegym.snake import Snake
from main_utils import process_observation, get_real_move_from_oriented, get_safe_moves_from_observation
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
    # get environment
    env = BattlesnakeGym(map_size=(11, 11), number_of_snakes=4, rewards=GameTeamRewards(), is_teammate_game=True, verbose=VERBOSE)

    # get agent and enemy
    agent_name = "agent_19052024_114840"
    agent = PPO("agent", "models/" + agent_name + ".pth")

    # set properties
    n_games = 100000
    n_history = 10000

    # keeping track
    n_k = 368834  # update these as needed
    n_steps = 3014684  # update these as needed
    learning_steps = 1472  # update these as needed
    update_iterations = 1
    best_score = -0.4326  # update these as needed
    avg_score = -1
    score_history = []

    # play all games
    for k in range(n_games):
        # reset
        observation, _, _, _ = env.reset()
        done = False
        score = 0

        while not done:
            # holder for all actions we take
            actions_to_take = []

            # get our agents action
            observation_, turns = process_observation(observation.copy(), 0)
            action, action_probs, value, _ = agent.predict(observation_)
            # process the action we took to get the action in gym coords
            actions_to_take.append(actions_dict[get_real_move_from_oriented(action, turns)])

            # get our teammates action (just us but different observation)
            observation_, turns = process_observation(observation.copy(), 1)
            action_, _, _, _ = agent.predict(observation_)
            actions_to_take.append(actions_dict[get_real_move_from_oriented(action_, turns)])

            # get the enemies actions (them and teammate)
            action_ = get_safe_moves_from_observation(observation.copy(), 2)
            actions_to_take.append(action_)
            action_ = get_safe_moves_from_observation(observation.copy(), 3)
            actions_to_take.append(action_)

            # get new state
            observation, reward, snakes_alive, info = env.step(actions_to_take)
            # done if (our agent is dead) or (only one snake alive) or (only two snakes are left and us and teammate are both either dead or alive)
            done = (snakes_alive[0] == False or np.sum(snakes_alive) <= 1 or (np.sum(snakes_alive) == 2 and snakes_alive[0] == snakes_alive[1]))

            # update and process observation for this agent
            n_steps += 1
            score += reward[0]
            observation_, _ = process_observation(observation.copy(), 0)

            # store this in memory
            agent.remember(observation_, action, action_probs, value, reward[0], done)

            # learn every now and then
            if n_steps % agent.buffer_size == 0:
                agent.learn()
                learning_steps += 1

        # end of episode, set variables
        score_history.append(score)
        avg_score = np.mean(score_history[-n_history:])  # average over previous 100 games
        if k > n_history * update_iterations:
            update_iterations += 1
            if avg_score > best_score:
                best_score = avg_score
                # get name based on timestamp
                name = "agent_" + str(datetime.datetime.now().strftime('%d%m%Y_%H%M%S'))
                label = "models/" + name + ".pth"
                # save this model
                agent.save_model(n_steps, label)
                # write info to ReadME
                with open("models/ReadME.txt", "a") as f:
                    f.write(name + ", " + str(k + n_k) + ", " + str(n_steps) + ", " + str(learning_steps) + "," + str(best_score) + "\n")
        
        print(f"episode: {k}; time steps: {n_steps}; learning steps: {learning_steps}, best score: {best_score}, average score: {avg_score}")
    
    # plot results
