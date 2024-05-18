# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# or in the "license" file accompanying this file. This file is distributed 
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either 
# express or implied. See the License for the specific language governing 
# permissions and limitations under the License.

import numpy as np

class Rewards:
    '''
    Base class to set up rewards for the battlesnake gym
    '''
    def get_reward(self, name, snake_id, episode):
        raise NotImplemented()

class SimpleRewards(Rewards):
    '''
    Simple class to handle a fixed reward scheme
    '''
    def __init__(self):
        self.reward_dict = {"another_turn": 1,
                            "ate_food": 5,
                            "won": 100,
                            "died": -100,
                            "ate_another_snake": 50,
                            "hit_wall": -100,
                            "hit_other_snake": -100,
                            "hit_self": -100,
                            "was_eaten": -100,
                            "other_snake_hit_body": 50,
                            "forbidden_move": 0,
                            "starved": -100}

    def get_reward(self, name, snake_id, episode):
        return self.reward_dict[name]
    
class TeamRewards(Rewards):
    '''
    Simple class to handle a fixed reward scheme with teammates
    '''
    def __init__(self):
        self.reward_dict = {"another_turn": 1,
                            "ate_food": 5,
                            "ate_another_snake": 50,
                            "other_snake_hit_body": 50,
                            "won": 100,
                            "won_with_teammate": 200,
                            "died": -100,
                            "hit_wall": -100,
                            "hit_other_snake": -100,
                            "hit_self": -100,
                            "was_eaten": -100,
                            "forbidden_move": -100,
                            "starved": -100}

    def get_reward(self, name, snake_id, episode):
        return self.reward_dict[name]