import heapq
from copy import deepcopy
import numpy as np


def brs(alpha: float, beta: float, depth: int, turn: str, game_state: dict,
        player_name: str, opponents: list, is_move_safe: dict) -> int:
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
        return evaluate(game_state, player_name, is_move_safe)

    # Determine the moves based on the turn
    # MAX is us
    if turn == 'MAX':
        moves = get_possible_moves(game_state, player_name, is_move_safe)
        next_turn = 'MIN'
    # MIN are the enemies
    else:
        moves = []  # Extend this list based on the number of players
        for opponent in opponents:
            if opponent["name"] != player_name:
                # if opponent["name"] != "SORZWE" and opponent["name"] != "SORZWE2":
                moves.extend(
                    get_possible_moves(game_state, opponent["name"], is_move_safe))
        next_turn = 'MAX'

    best_value = float('-inf') if turn == 'MAX' else float('inf')

    # Explore each move
    for agent_name, move in moves:
        print(f"Trying Move: {move} for {agent_name}, Alpha: {alpha}, Beta: {beta}")

        # get the new state and evaluate it
        new_state, _ = get_state_from_move(game_state, agent_name, move)
        filtered_opponents = [
            opponent for opponent in opponents
            if opponent['name'] != agent_name
        ]

        value = -brs(-beta, -alpha, depth - 1, next_turn, new_state,
                     agent_name, filtered_opponents, is_move_safe)

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


def get_possible_moves(game_state: dict, player_name: str,
                       is_move_safe: dict) -> list:
    # This function should return a list of all possible moves for the given player.
    # returns a list like [[name, move], [name, move], etc.]

    # Filter the directions based on the is_move_safe dictionary
    return [[player_name, "up"], [player_name, "down"], [player_name, "left"],
            [player_name, "right"]]


def get_state_from_move(game_state, player_name, move):
    new_game_state = deepcopy(game_state)
    direction_map = {
        "up": (0, 1),
        "down": (0, -1),
        "left": (-1, 0),
        "right": (1, 0)
    }

    snake_index = next(
        i for i, snake in enumerate(new_game_state["board"]["snakes"])
        if snake["name"] == player_name)
    snake = new_game_state["board"]["snakes"][snake_index]
    head = snake["body"][0]
    dx, dy = direction_map[move]
    new_head = {'x': head['x'] + dx, 'y': head['y'] + dy}

    # Check if the new head position is on a food item
    if any(food['x'] == new_head['x'] and food['y'] == new_head['y']
           for food in new_game_state['board']['food']):
        # If the snake eats food, it grows: new head is added but the tail remains
        new_body = [new_head] + snake["body"]
        # Remove the eaten food from the board
        new_game_state['board']['food'] = [
            food for food in new_game_state['board']['food']
            if not (food['x'] == new_head['x'] and food['y'] == new_head['y'])
        ]
    else:
        # If the snake does not eat, move the head and drop the tail
        new_body = [new_head] + snake["body"][:-1]

    new_game_state["board"]["snakes"][snake_index]["body"] = new_body
    return new_game_state, snake_index


def evaluate(game_state: dict, player_name: str, is_move_safe: dict) -> int:
    """Evaluate the state of the game and calculate a heuristic based on strategic priorities."""
    # Find the player's snake
    this_snake = next(snake for snake in game_state["board"]["snakes"] if snake["name"] == player_name)
    this_head = this_snake["body"][0]

    # Heuristic components
    food_score, food_location = calculate_food_score(game_state, this_head)
    separation_score = 0

    # Evaluate against all other snakes
    for snake in game_state["board"]["snakes"]:
        if snake["name"] != player_name:
            other_head = snake["body"][0]
            separation_score += calculate_separation_score(this_head, other_head)
            if food_location and manhattan_distance(food_location, other_head) > 5:
                separation_score += food_score
    # You can adjust the influence of separation_score by changing its weighting factor
    total_score = food_score + separation_score
    print(
        f"Evaluating for {player_name}: Food Score = {food_score}, Separation Score = {separation_score}, Total Score = {total_score}")

    return int(total_score)


def calculate_food_score(game_state, head):
    """Calculate a score based on the distance to the closest food.
    Closer food will have a higher score."""
    min_distance = float('inf')
    closest_food_score = 0
    food_location = None
    for food in game_state['board']['food']:
        food_distance = manhattan_distance(food, head)
        if food_distance < min_distance:
            min_distance = food_distance
            # Higher score for closer food
            closest_food_score = 100 / (1 + food_distance)  # Using inverse to ensure closer food gets higher score
            food_location = food
    return closest_food_score, food_location


def calculate_separation_score(head_one, head_two):
    """Calculate a score that rewards distance between two heads."""
    distance = manhattan_distance(head_one, head_two)
    if distance < 5:
        return distance * 20  # Reward for each unit of distance between the snakes
    else:
        return 100


def manhattan_distance(a, b):
    return abs(a['x'] - b['x']) + abs(a['y'] - b['y'])

def euclidean_distance(a, b):
    return np.sqrt((a["x"] - b["x"])**2 + (a["y"] - b["y"])**2)


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

    # Initialize visited set with all snake bodies except the tail of the current snake
    visited = set()
    for snake in game_state["board"]["snakes"]:
        body_parts = snake["body"][:-1]  # mb good mb bad to exclude tail
        if snake["name"] == game_state["you"]["name"]:
            body_parts = snake["body"][:-1]  # mb good mb bad to exclude tail
        for part in body_parts:
            visited.add((part['x'], part['y']))

    while open_set:
        _, x, y = heapq.heappop(open_set)
        if (x, y) == (target_x, target_y):
            # Path found, reconstruct it
            path = reconstruct_path(came_from, (x, y))
            return True

        visited.add((x, y))

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < game_state['board']['width'] and 0 <= ny < game_state['board']['height'] \
                    and (nx, ny) not in visited:
                tentative_g_score = g_score.get((x, y), float('inf')) + 1
                if tentative_g_score < g_score.get((nx, ny), float('inf')):
                    came_from[(nx, ny)] = (x, y)
                    g_score[(nx, ny)] = tentative_g_score
                    f_score[(nx, ny)] = tentative_g_score + manhattan_distance({'x': nx, 'y': ny}, tail)
                    heapq.heappush(open_set, (f_score[(nx, ny)], nx, ny))

    return False


def simulate_moves_and_check_reachability(game_state, player_name,
                                          is_move_safe):
    safe_moves = [move for move, is_safe in is_move_safe.items() if is_safe]
    viable_moves = []

    for move in safe_moves:
        # Simulate the move
        new_state, _ = get_state_from_move(game_state, player_name, move)

        # Get the snake's new head position after the move
        snake = next(s for s in new_state["board"]["snakes"]
                     if s["name"] == player_name)
        new_head = snake["body"][0]
        tail = snake["body"][-1]

        # Check if the snake can reach its tail after this move
        if can_reach_tail(new_state, new_head, tail, snake["body"], move,
                          is_move_safe):
            viable_moves.append(move)

    return viable_moves
