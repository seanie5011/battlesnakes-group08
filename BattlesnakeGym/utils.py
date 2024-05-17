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
import gymnasium as gym
import math

def is_coord_in(coord, array):
    for a in array:
        if a[0] == coord[0] and a[1] == coord[1]:
            return True
    return False

def get_random_coordinates(map_size, n, excluding=[]):
    '''
    Helper function to get n number of random coordinates based on the map
    Parameters:
    ----------
    map_size, (int, int)
        Size of the map with possible coordinates
    
    n, int
        number of coordinates to get

    excluding: [(int, int)]
        A list of coordinates to not include in the randomly generated coordinates
    '''
    coordinates_indexes = []
    coordinates = []
    count = 0
    for i in range(map_size[0]):
        for j in range(map_size[1]):
            if is_coord_in(coord=(i, j), array=excluding):
                continue
            coordinates.append((i, j))
            coordinates_indexes.append(count)
            count += 1

    indexes = np.random.choice(coordinates_indexes, n, replace=False)
    random_coordinates = np.array(coordinates)[indexes]
    return random_coordinates

def generate_coordinate_list_from_binary_map(map_image):
    '''
    Helper function to convert binary maps into a list of coordinates
    '''
    coordinate_list = []
    for i in range(map_image.shape[0]):
        for j in range(map_image.shape[1]):
            if map_image[i][j] > 0:
                coordinate_list.append((i, j))
    return coordinate_list

class MultiAgentActionSpace(list):
    '''
    Code taken from https://github.com/koulanurag/ma-gym/blob/master/ma_gym/envs/utils/action_space.py
    '''
    def __init__(self, agents_action_space):
        for x in agents_action_space:
            assert isinstance(x, gym.spaces.space.Space)

        super(MultiAgentActionSpace, self).__init__(agents_action_space)
        self._agents_action_space = agents_action_space
        self.n = len(self._agents_action_space)

    def sample(self):
        """ samples action for each agent from uniform distribution"""
        return [agent_action_space.sample() for agent_action_space in self._agents_action_space]

def get_distance(point1, point2):
    return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def process_observation(_observation, current_snake_index):
    """
    Processes the observation from the gym to be a single 11x11 array.
    Assumes a 4-player 11x11 game.

    Where:
        0 denotes free space
        1 denotes food
        2 denotes player 0s head
        3 denotes player 0s body
        4 denotes player 1s head
        5 denotes player 1s body
        6 denotes player 2s head
        7 denotes player 2s body
        8 denotes player 3s head
        9 denotes player 3s body
    
    oriented such that player current_snake_index 
    """

    observation = _observation.copy()

    # get this snakes particular 11x11
    # plus 1 as the zero index is food
    snake_observation = observation[:,:,current_snake_index + 1].copy()
    # check if we might need to turn this (orientation, always want to orient up)
    # if there are no heads or necks, nothing to do
    turns = 0
    if np.any(snake_observation == 2) and np.any(snake_observation == 1):
        # the head is always labelled 1 and neck always 2
        # note that the x and ys are swapped due to the nature of python indexing
        head_index = np.argwhere(snake_observation == 1).flatten()
        head_x = head_index[1]
        head_y = head_index[0]
        neck_index = np.argwhere(snake_observation == 2).flatten()
        neck_x = neck_index[1]
        neck_y = neck_index[0]

        # now checking where they are relative to each other we can figure out the orientation
        # note that we return the number of times we should rotate 90degrees to be facing up
        if (head_x == neck_x):
            if (head_y < neck_y):
                # up
                turns = 0
            elif (head_y > neck_y):
                # down
                turns = 2
        elif (head_y == neck_y):
            if (head_x < neck_x):
                # left
                turns = 3
            elif (head_x > neck_x):
                # right
                turns = 1
        
        observation = np.rot90(observation, turns).copy()
    
    # # now process so that players values are as detailed above
    # # four snakes
    # for snake_index in range(4):
    #     # get this snakes
    #     temp = observation[:,:,snake_index + 1].copy()
    #     # set head and body
    #     temp[observation[:,:,snake_index + 1] == 1] = 2 + 2 * snake_index
    #     temp[observation[:,:,snake_index + 1] > 1] = 3 + 2 * snake_index
    #     # set back
    #     observation[:,:,snake_index + 1] = temp
    
    # # sum everything to put all layers on one
    # return np.sum(observation, axis=2), turns
    return observation.reshape(5, 11, 11), turns

def get_real_move_from_oriented(move: int, turns: int) -> str:
    """
    Returns a move in real space depending on the number of turns taken.

    Inputs:
        move (int): 0, 1 or 2 - forward, left, right
        turns (int): how many times the observation was rotated 90-degrees
    Outputs:
        str: "up", "down", "left", or "right"
    """
    # all moves we can take
    moves = ["up", "right", "down", "left"]

    # conversion from move (input) to index
    move_conversion = {
        0: 0,
        1: -1,
        2: 1,
    }
    # use this with number of turns to get index in list
    move_index = (move_conversion[move] + turns) % len(moves)
    return moves[move_index]