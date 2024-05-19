import numpy as np
import random
import datetime

from battlesnakegym.rewards import TeamRewards, GameTeamRewards
from battlesnakegym.snake_gym import BattlesnakeGym
from battlesnakegym.snake import Snake
from main_utils import process_observation, get_real_move_from_oriented
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
    agent_name = "agent_104646_19052024"
    agent = PPO("agent", "models/" + agent_name + ".pth")
    enemies = [PPO("enemy", "models/agent_104646_19052024.pth"), PPO("enemy", "models/agent_095112_19052024.pth"), PPO("enemy", "models/agent_085535_19052024.pth"), PPO("enemy", "models/agent_080324_19052024.pth"), PPO("enemy", "models/agent_071113_19052024.pth")]

    # set properties
    n_games = 100000
    n_history = 10000

    # keeping track
    n_k = 328832  # update these as needed
    n_steps = 2666329  # update these as needed
    learning_steps = 1301  # update these as needed
    update_iterations = 1

    # play all games
    for k in range(n_games):
        # reset
        observation, _, _, _ = env.reset()
        done = False
        # 20% of the time choose any of the non-best enemies
        if random.random() > 0.8 and len(enemies) > 1:
            enemy = random.choice(enemies[1:])
        # 80% of the time choose the best
        else:
            enemy = enemies[0]

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
            observation_, turns = process_observation(observation.copy(), 2)
            action_, _, _, _ = enemy.predict(observation_)
            actions_to_take.append(actions_dict[get_real_move_from_oriented(action_, turns)])
            observation_, turns = process_observation(observation.copy(), 3)
            action_, _, _, _ = enemy.predict(observation_)
            actions_to_take.append(actions_dict[get_real_move_from_oriented(action_, turns)])

            # get new state
            observation, reward, snakes_alive, info = env.step(actions_to_take)
            # done if (our agent is dead) or (only one snake alive) or (only two snakes are left and us and teammate are both either dead or alive)
            done = (snakes_alive[0] == False or np.sum(snakes_alive) <= 1 or (np.sum(snakes_alive) == 2 and snakes_alive[0] == snakes_alive[1]))

            # update and process observation for this agent
            n_steps += 1
            observation_, _ = process_observation(observation.copy(), 0)

            # store this in memory
            agent.remember(observation_, action, action_probs, value, reward[0], done)

            # learn every now and then
            if n_steps % agent.buffer_size == 0:
                agent.learn()
                learning_steps += 1

        # every so often try and update
        if k > n_history * update_iterations:
            print("   GLADIATOR TIME   ")
            update_iterations += 1

            # play 500 games against enemies
            # track how many we have won
            games_played = 0
            games_won = 0
            for _ in range(500):
                games_played += 1
                # reset
                _observation, _, _, _ = env.reset()
                _done = False
                # 20% of the time choose any of the non-best enemies
                if random.random() > 0.8 and len(enemies) > 1:
                    _enemy = random.choice(enemies[1:])
                # 80% of the time choose the best
                else:
                    _enemy = enemies[0]
                while not _done:
                    # holder for all actions we take
                    _actions_to_take = []

                    # get our agents action
                    _observation_, _turns = process_observation(_observation.copy(), 0)
                    _action, _, _, _ = agent.predict(_observation_)
                    # process the action we took to get the action in gym coords
                    _actions_to_take.append(actions_dict[get_real_move_from_oriented(_action, _turns)])

                    # get our teammates action (just us but different observation)
                    _observation_, _turns = process_observation(_observation.copy(), 1)
                    _action_, _, _, _ = agent.predict(_observation_)
                    _actions_to_take.append(actions_dict[get_real_move_from_oriented(_action_, _turns)])

                    # get the enemies actions (them and teammate)
                    _observation_, _turns = process_observation(_observation.copy(), 2)
                    _action_, _, _, _ = _enemy.predict(_observation_)
                    _actions_to_take.append(actions_dict[get_real_move_from_oriented(_action_, _turns)])
                    _observation_, _turns = process_observation(_observation.copy(), 3)
                    _action_, _, _, _ = _enemy.predict(_observation_)
                    _actions_to_take.append(actions_dict[get_real_move_from_oriented(_action_, _turns)])

                    # get new state
                    _observation, _, _snakes_alive, _ = env.step(_actions_to_take)
                    # done if (our agent is dead) or (only one snake alive) or (only two snakes are left and us and teammate are both either dead or alive)
                    _done = (_snakes_alive[0] == False or np.sum(_snakes_alive) <= 1 or (np.sum(_snakes_alive) == 2 and _snakes_alive[0] == _snakes_alive[1]))
                # if we won, count it
                if _snakes_alive[0] or _snakes_alive[1]:
                    games_won += 1
            
            # if we have won more than 30% then we update
            if games_won / games_played >= 0.3:
                print(f"   GLADIATOR SUCEEDED WITH {100.0 * games_won / games_played}% WIN RATE   ")
                # get name based on timestamp
                name = "agent_" + str(datetime.datetime.now().strftime('%H%M%S_%d%m%Y'))
                label = "models/" + name + ".pth"
                # save this model
                agent.save_model(n_steps, label)
                # add to enemies list
                # if less than 5, just append
                if len(enemies) < 5:
                    enemies.insert(0, PPO(name, label))
                # otherwise, replace at random
                else:
                    enemies.insert(0, PPO(name, label))
                    enemies.pop()
                
                # write info to ReadME
                with open("models/ReadME.txt", "a") as f:
                    f.write(name + ", " + str(k + n_k) + ", " + str(n_steps) + ", " + str(learning_steps) + "\n")
            else:
                print(f"   GLADIATOR FAILED WITH {100.0 * games_won / games_played}% WIN RATE   ")
        
        print(f"episode: {k}; time steps: {n_steps}; learning steps: {learning_steps}")
    
    # plot results
