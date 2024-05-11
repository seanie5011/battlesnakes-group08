import heapq
from copy import deepcopy
import numpy as np
from collections import deque


def brs(alpha: int, beta: int, depth: int, turn: str, game_state: dict,
        player_name: str, opponents: list[str]) -> int:
    """
    Implements the Best-Reply Search (BRS) algorithm.
    
    Args:
    alpha (int): Alpha value for alpha-beta pruning.
    beta (int): Beta value for alpha-beta pruning.
    depth (int): Current depth in the search tree.
    turn (str): Current turn, either 'MAX' or 'MIN'.
    
    Returns:
    int: The heuristic value of the node.
    """

    # if depth is 0, return the evaluation of the board
    if depth <= 0:
        return evaluate(game_state, player_name)

    # Determine the moves based on the turn
    # MAX is us
    if turn == 'MAX':
        moves = get_possible_moves(game_state, player_name)
        next_turn = 'MIN'
    # MIN are the enemies
    else:
        moves = []  # Extend this list based on the number of players
        for opponent in opponents:
            moves.extend(get_possible_moves(game_state, opponent))
        next_turn = 'MAX'

    best_value = float('-inf') if turn == 'MAX' else float('inf')

    # Explore each move
    for agent_name, move in moves:
        # get the new state and evaluate it
        new_state = get_state_from_move(game_state, agent_name, move)
        value = -brs(
            -beta, -alpha, depth - 1, next_turn, new_state, agent_name, [
                player_name, *[
                    opponent
                    for opponent in opponents if opponent != agent_name
                ]
            ])

        # set alpha or beta depending
        if turn == 'MAX':
            if value >= beta:
                return value
            if value > best_value:
                best_value = value
                alpha = max(alpha, value)
        else:
            if value <= alpha:
                return value
            if value < best_value:
                best_value = value
                beta = min(beta, value)

    return best_value


def get_possible_moves(game_state: dict, player: str) -> list[str]:
    # This function should return a list of all possible moves for the given player.
    # returns a list like [[name, move], [name, move], etc.]
    return [[player, "up"], [player, "down"], [player, "left"],
            [player, "right"]]


def get_state_from_move(game_state: dict, player: str,
                        move: list[str]) -> dict:
    # This function should modify the game state by making the specified move.
    # make sure we get a deepcopy to not modify the original
    new_game_state = deepcopy(game_state)

    # get this snakes bodyparts
    this_index = -1
    for snake in new_game_state["board"]["snakes"]:
        this_index += 1
        if snake["name"] == player:
            break
        else:
            continue
    bodyparts = new_game_state["board"]["snakes"][this_index]["body"]
    # move them all up, simulate the game moving forward
    new_bodyparts = []
    for bodypart in bodyparts[0::-1]:
        new_bodyparts.insert(0, bodypart)

    # move the head according to the action
    moves_to_coord_change_x = {"up": 0, "down": 0, "left": -1, "right": 1}
    moves_to_coord_change_y = {"up": 1, "down": -1, "left": 0, "right": 0}
    next_x = bodyparts[0]["x"] + moves_to_coord_change_x[move]
    next_y = bodyparts[0]["y"] + moves_to_coord_change_y[move]
    new_bodyparts.insert(0, {"x": next_x, "y": next_y})

    # set this in the new game state
    new_game_state["board"]["snakes"][this_index]["body"] = new_bodyparts
    return new_game_state


def evaluate(game_state: dict, player: str) -> int:
    """A simple evaluation function that could prioritize staying alive"""
    # get the current snake
    this_index = -1
    for snake in game_state["board"]["snakes"]:
        this_index += 1
        if snake["name"] == player:
            break
        else:
            continue
    this_snake = game_state["board"]["snakes"][this_index]
    # get its head
    head = this_snake["body"][0]
    tail = this_snake["body"][-1]

    # Board dimensions
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    center_x = board_width // 2
    center_y = board_height // 2

    # Calculate euclidean distance from the head to the center, manhattan was kinda scuffed??
    distance_to_center = np.sqrt(abs(center_x - head['x']) ** 2 + abs(center_y - head['y']) ** 2)

    # Inverting the distance to use it as a positive score; closer to center gives higher score
    survival_score = -distance_to_center

    food_positions = game_state['board']['food']
    closest_food = None
    closest_food_distance = float('inf')

    # Find the closest food and calculate its distance
    for food in food_positions:
        food_distance = np.sqrt((head['x'] - food['x']) ** 2 + (head['y'] - food['y']) ** 2)
        if food_distance < closest_food_distance:
            closest_food_distance = food_distance
            closest_food = food

    food_score = 0
    high_food_score = 50  # This is the reward for successfully eating food

    # Check if the closest food is reachable and if after eating it, the snake can still reach its tail
    if closest_food and head['x'] == closest_food['x'] and head['y'] == closest_food['y']:
        # Simulate eating the closest food
        simulated_game_state = deepcopy(game_state)
        simulated_snake = simulated_game_state["board"]["snakes"][this_index]
        # Simulate head moving to food position
        simulated_snake['body'].insert(0, {'x': closest_food['x'], 'y': closest_food['y']})

        # Check if the snake can still reach its tail after eating
        if can_reach_tail(simulated_game_state, simulated_snake['body'][0], tail, simulated_snake['body']):
            food_score += high_food_score
        else:
            # Apply a significant penalty if eating leads to being trapped
            food_score -= 1000

    path_score = 0
    if not can_reach_tail(game_state, head, tail, this_snake['body']):
        path_score = -10000  # Apply penalty if the snake is currently in a position where it can't reach its tail

    # Combine the scores
    return int(food_score + path_score)


def can_reach_tail(game_state, head, tail, snake_body):
    """ Check if there is a path from head to tail using A* """
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Possible movements
    open_set = []
    heapq.heappush(open_set, (0, head['x'], head['y']))  # Priority queue of open nodes
    came_from = {}  # For path reconstruction if necessary

    g_score = {(head['x'], head['y']): 0}  # Cost from start to node
    f_score = {(head['x'], head['y']): manhattan_distance(head, tail)}  # Estimated total cost from start to goal

    visited = set((part['x'], part['y']) for part in snake_body[:-1])  # Initial occupied cells, exclude tail

    while open_set:
        _, x, y = heapq.heappop(open_set)

        if (x, y) == (tail['x'], tail['y']):  # Check if reached the tail
            return True

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < game_state['board']['width'] and 0 <= ny < game_state['board']['height']:
                if (nx, ny) in visited:
                    continue
                tentative_g_score = g_score.get((x, y), float('inf')) + 1  # Assuming each move has a cost of 1

                if tentative_g_score < g_score.get((nx, ny), float('inf')):
                    came_from[(nx, ny)] = (x, y)
                    g_score[(nx, ny)] = tentative_g_score
                    f_score[(nx, ny)] = tentative_g_score + manhattan_distance({'x': nx, 'y': ny}, tail)
                    if (nx, ny) not in [i[1:] for i in open_set]:  # Check if not in open_set
                        heapq.heappush(open_set, (f_score[(nx, ny)], nx, ny))

    return False


def manhattan_distance(point1, point2):
    """Calculate the Manhattan distance between two points"""
    return abs(point1['x'] - point2['x']) + abs(point1['y'] - point2['y'])
