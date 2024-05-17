import time
import numpy as np

from battlesnakegym import snake_gym

RENDER = 0
VERBOSE = 0

env = snake_gym.BattlesnakeGym(map_size=(11, 11), number_of_snakes=4, verbose=VERBOSE)

# run for number of episodes
episodes = 10  # for completely random games on a 11x11 map with 4 snakes, each snake only moves 3.7 times before death
start_time = time.time()
total_score = 0
total_steps = 0
print(f"Starting timer for {episodes} episodes...")
for episode in range(0, episodes):
    # reset
    observation, _, _, _ = env.reset()
    done = False
    score = 0
    steps = 0

    # rendering
    if RENDER:
        env.render()
        time.sleep(0.5)

    print("Starting training...")
    while not done:
        # get action and check environment
        action = env.action_space.sample()
        observation, reward, snakes_alive, info = env.step(action)
        score += reward[0]
        done = (np.sum(snakes_alive) <= 1)  # if 1 or less snakes are alive, done
        steps += 1

        # rendering
        if RENDER:
            env.render()
            time.sleep(0.5)
        
        # debugging
        # print(f"action space: {env.action_space}")
        # print(f"action chosen: {action}")
        # print(f"observation space: {env.observation_space}")
        # print(f"observation {observation}")
        # print(f"reward given: {reward}")
        # print(f"snakes dead message {snakes_dead_dict}")
    print(f"Episode: {episode + 1}; Score: {score}")
    total_score += score
    total_steps += steps

print(f"Training finished, {episodes} episodes took {time.time() - start_time:0.3f} seconds for an average of {(time.time() - start_time) / episodes:0.3f} seconds per episode, {total_steps / episodes:0.3f} steps per episode and {total_score / episodes:0.3f} score per episode.")

env.close()