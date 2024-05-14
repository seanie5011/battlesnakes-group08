import heapq
from copy import deepcopy
import numpy as np
from collections import deque


def brs(alpha: int, beta: int, depth: int, turn: str, game_state: dict,
        player_id: str, opponents: list, is_move_safe: dict) -> int:
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
        return evaluate(game_state, player_id, is_move_safe)

    # Determine the moves based on the turn
    # MAX is us
    if turn == 'MAX':
        moves = get_possible_moves(game_state, player_id, is_move_safe)
        next_turn = 'MIN'
    # MIN are the enemies
    else:
        moves = []  # Extend this list based on the number of players

        for opponent in opponents:
            # TODO: pass only the enemies here, am i right tho?
            if opponent["name"] != "SORZWE":
                moves.extend(get_possible_moves(game_state, player_id, is_move_safe))
        next_turn = 'MAX'

    best_value = float('-inf') if turn == 'MAX' else float('inf')

    # Explore each move
    for agent_id, move in moves:
        # get the new state and evaluate it
        new_state, _ = get_state_from_move(game_state, agent_id, move)
        filtered_opponents = [opponent for opponent in opponents if opponent['id'] != agent_id]

        value = -brs(
            -beta, -alpha, depth - 1, next_turn, new_state, agent_id, filtered_opponents, is_move_safe)

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


def get_possible_moves(game_state: dict, playerid: str, is_move_safe: dict) -> list:
    # This function should return a list of all possible moves for the given player.
    # returns a list like [[name, move], [name, move], etc.]

    # Filter the directions based on the is_move_safe dictionary
    return [[playerid, "up"], [playerid, "down"], [playerid, "left"],
            [playerid, "right"]]


def get_state_from_move(game_state, player_id, move):
    new_game_state = deepcopy(game_state)
    direction_map = {"up": (0, 1), "down": (0, -1), "left": (-1, 0), "right": (1, 0)}

    snake_index = next(i for i, snake in enumerate(new_game_state["board"]["snakes"]) if snake["id"] == player_id)
    snake = new_game_state["board"]["snakes"][snake_index]
    head = snake["body"][0]
    dx, dy = direction_map[move]
    new_head = {'x': head['x'] + dx, 'y': head['y'] + dy}

    # Check if the new head position is on a food item
    if any(food['x'] == new_head['x'] and food['y'] == new_head['y'] for food in new_game_state['board']['food']):
        # If the snake eats food, it grows: new head is added but the tail remains
        new_body = [new_head] + snake["body"]
        # Remove the eaten food from the board
        new_game_state['board']['food'] = [food for food in new_game_state['board']['food'] if not (food['x'] == new_head['x'] and food['y'] == new_head['y'])]
    else:
        # If the snake does not eat, move the head and drop the tail
        new_body = [new_head] + snake["body"][:-1]

    new_game_state["board"]["snakes"][snake_index]["body"] = new_body
    return new_game_state, snake_index


def evaluate(game_state: dict, player_id: str, is_move_safe: dict) -> int:
    """A simple evaluation function that could prioritize staying alive"""

    # viable_moves = simulate_moves_and_check_reachability(game_state, player_id, is_move_safe)
    viable_moves = [move for move, is_safe in is_move_safe.items() if is_safe]
    this_index = -1
    for snake in game_state["board"]["snakes"]:
        this_index += 1
        if snake["id"] == player_id:
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
    # Check if the closest food is reachable and if after eating it, the snake can still reach its tail
    for move in viable_moves:

        new_state,_ = get_state_from_move(game_state, player_id, move)
        snake = next(s for s in new_state["board"]["snakes"] if s["id"] == player_id)
        new_head = snake["body"][0]
        new_tail = snake["body"][-1]
        new_body = snake["body"][1:-1]
        if closest_food and new_head['x'] == closest_food['x'] and new_head['y'] == closest_food['y']:
            food_score += 20

    # Combine the scores
    return int(food_score)


def manhattan_distance(a, b):
    return abs(a['x'] - b['x']) + abs(a['y'] - b['y'])


def can_reach_tail(game_state, head, tail, snake_body, move, is_move_safe):
    def reconstruct_path(came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    start_x, start_y = head['x'], head['y']
    target_x, target_y = tail['x'], tail['y']

    open_set = []
    heapq.heappush(open_set, (0, start_x, start_y))
    came_from = {}
    g_score = {(start_x, start_y): 0}
    f_score = {(start_x, start_y): manhattan_distance(head, tail)}
    visited = set((part['x'], part['y']) for part in snake_body[1:-1])  # Exclude tail for body check

    while open_set:
        _, x, y = heapq.heappop(open_set)
        if (x, y) == (target_x, target_y):
            # Path found, reconstruct it
            path = reconstruct_path(came_from, (x, y))
            print(path)
            return True

        visited.add((x, y))

        for move in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + move[0], y + move[1]
            if 0 <= nx < game_state['board']['width'] and 0 <= ny < game_state['board']['height'] \
                    and (nx, ny) not in visited:
                tentative_g_score = g_score.get((x, y), float('inf')) + 1
                if tentative_g_score < g_score.get((nx, ny), float('inf')):
                    came_from[(nx, ny)] = (x, y)
                    g_score[(nx, ny)] = tentative_g_score
                    f_score[(nx, ny)] = tentative_g_score + manhattan_distance({'x': nx, 'y': ny}, tail)
                    heapq.heappush(open_set, (f_score[(nx, ny)], nx, ny))

    return False



def simulate_moves_and_check_reachability(game_state, player_id, is_move_safe):
    safe_moves = [move for move, is_safe in is_move_safe.items() if is_safe]
    viable_moves = []

    for move in safe_moves:
        # Simulate the move
        new_state,_ = get_state_from_move(game_state, player_id, move)

        # Get the snake's new head position after the move
        snake = next(s for s in new_state["board"]["snakes"] if s["id"] == player_id)
        new_head = snake["body"][0]
        tail = snake["body"][-1]

        # Check if the snake can reach its tail after this move
        if can_reach_tail(new_state, new_head, tail, snake["body"], move, is_move_safe):
            viable_moves.append(move)

    return viable_moves
