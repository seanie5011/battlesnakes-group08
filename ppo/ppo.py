import os
import numpy as np
import torch
import torch.optim as optim

from .memory import Memory
from .actor import Actor
from .critic import Critic

class PPO():
    def __init__(self, label, model_save_path) -> None:
        self.label = label
        self.model_save_path = model_save_path

        # HYPERPARAMETERS
        self.gamma = 0.999  # discount factor
        self.batch_size = 32
        self.buffer_size = 20  # number of steps before update (2048)
        self.n_epochs = 4
        self.policy_clip = 0.2
        self.entropy_coef = 0.01
        self.actor_lr = 0.00005
        self.critic_lr = 0.00005
        self.actor_eps = 1e-5
        self.critic_eps = 1e-5

        # set device if gpu possible
        self.device = "cuda" if torch.cuda.is_available() else "cpu"                
        
        print(f"{label} using device {self.device}")

        # set up memory, actor, critic and optimizers
        self.actor = Actor(3).to(self.device)
        self.critic = Critic().to(self.device)
        self.memory = Memory(self.batch_size)

        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=self.actor_lr, eps=self.actor_eps)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=self.critic_lr, eps=self.critic_eps)
        
        # load model if possible
        self.load_model(model_save_path)        

    def learn(self):
        # check if memory is large enough
        if (len(self.memory.states) < self.buffer_size):
            print(f"Not enough memory to learn: {len(self.memory.states)} < {self.buffer_size}")
            return 0
        else:
            print("learning..")

        # for each epoch
        avg_loss = 0
        for _ in range(self.n_epochs):
            state_arr, action_arr, old_prob_arr, values, reward_arr, dones_arr, batches = self.memory.generate_batches()
            
            # calculate the advantage of each state by iterate from end to start
            advantage = np.zeros(len(reward_arr), dtype=np.float32)
            for t in reversed(range(len(reward_arr) - 1)):
                discounted_return_t = reward_arr[t]

                if (dones_arr[t] == False):  # dones, convention in RL
                    discounted_return_t += self.gamma * advantage[t + 1]

                advantage[t] = discounted_return_t

            advantage = advantage - values

            # normalize advantage
            advantage = (advantage - np.mean(advantage)) / (np.std(advantage) + 1e-10)

            # convert advantage and values to tensors
            advantage = torch.tensor(advantage).to(self.device)
            values = torch.tensor(values).to(self.device)

            # now each batch
            for batch in batches:
                # old policy stuff
                states = torch.tensor(state_arr[batch], dtype=torch.float).to(self.device)
                old_log_probs = torch.tensor(old_prob_arr[batch]).to(self.device)
                actions = torch.tensor(action_arr[batch]).to(self.device)
                
                # get new distribution
                dist = self.actor(states)
                critic_value = torch.squeeze(self.critic(states))

                entropy = dist.entropy().mean()

                # use probs to get actor loss
                new_log_probs = dist.log_prob(actions)
                prob_ratio = new_log_probs.exp() / old_log_probs.exp()  # put back into exponential form
                weighted_probs = advantage[batch] * prob_ratio
                weighted_clipped_probs = torch.clamp(prob_ratio, 1-self.policy_clip, 1+self.policy_clip) * advantage[batch]
                actor_loss = -torch.min(weighted_probs, weighted_clipped_probs).mean()                

                # use returns for critic loss
                returns = advantage[batch] + values[batch]
                critic_loss = (returns - critic_value)**2
                critic_loss = critic_loss.mean()

                # get total and average losses, propagate everything
                total_loss = actor_loss + 0.5 * critic_loss - self.entropy_coef * entropy
                avg_loss += total_loss.item()

                self.actor_optimizer.zero_grad()
                self.critic_optimizer.zero_grad()

                total_loss.backward()
                
                self.actor_optimizer.step()
                self.critic_optimizer.step()

        # finished learning, clear memory
        self.memory.clear_memory()
        
        # return average loss over all epochs
        return avg_loss * 1.0 / self.n_epochs

    def remember(self, state, action, probs, vals, reward, done):
        self.memory.store_memory(state, action, probs, vals, reward, done)

        # print(f"Stored memory: {type(state)}, {action}, {probs}, {vals}, {reward}, {done}")

    def predict(self, observation) -> tuple:
        # convert to tensor
        state = torch.tensor(observation, dtype=torch.float).to(self.device)

        # get distribution from actor and its corresponding value from critic
        dist = self.actor(state)
        value = self.critic(state)
        
        # sample from this and squeezing
        action = dist.sample()
        action_probs = torch.squeeze(dist.log_prob(action)).item()
        action = torch.squeeze(action).item()
        value = torch.squeeze(value).item()

        # get dist probs as list
        actor_probs = dist.probs.squeeze().tolist()

        return action, action_probs, value, actor_probs
        
    def save_model(self, curr_step) -> None: 
        data_to_save = {
            'actor': self.actor.state_dict(),
            'critic': self.critic.state_dict(),
            'curr_step': curr_step
        }

        torch.save(data_to_save, self.model_save_path)
        print(f"\n    SAVED model to {self.model_save_path}\n")

    def load_model(self, path) -> dict:
        self.model_save_path = path
        self.curr_step = 0

        # check if file exists first
        if (os.path.exists(path) == False):
            print(f"Model not found at {path}, skipping...")
            
            return
        
        saved_dict = torch.load(path, map_location=torch.device(self.device))

        self.actor.load_state_dict(saved_dict['actor'])
        self.critic.load_state_dict(saved_dict['critic'])
        self.curr_step = saved_dict['curr_step']
        
        print(f"Model loaded from {path}")