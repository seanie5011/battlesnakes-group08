import heapq
from copy import deepcopy
import numpy as np


def brs(alpha: float, beta: float, depth: int, turn: str, game_state: dict,
        player_name: str, opponents: list, is_move_safe: dict) -> int:

    if depth <= 0:
        if turn == "MAX":

            return evaluate(game_state, player_name)
        else:

            return - evaluate(game_state, player_name)
    # Determine the moves based on the turn
    # MAX is us
    if turn == 'MAX':
        moves = compute_possible_moves(game_state, player_name)
        next_turn = 'MIN'
    # MIN are the enemies
    else:
        moves = []
        for opponent in opponents:
            if opponent["name"] == player_name:
                continue
            moves.extend(
                compute_possible_moves(game_state, opponent["name"]))
        next_turn = 'MAX'

    # Explore each move
    for agent_name, move in moves:

        new_state, _ = get_state_from_move(game_state, agent_name, move)
        filtered_opponents = [
            snake for snake in new_state["board"]["snakes"]
            if snake['name'] != agent_name
        ]

        value = -brs(-beta, -alpha, depth - 1, next_turn, new_state,
                     agent_name, filtered_opponents, is_move_safe)

        if value >= beta:
            print(f"beta done {value}")
            return value
        alpha = max(alpha, value)
    print(f"alpha done {alpha}")
    return alpha


def get_possible_moves(game_state: dict, player_name: str, is_move_safe: dict) -> list:
    snake = next(s for s in game_state["board"]["snakes"] if s["name"] == player_name)
    head = snake["body"][0]
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]
    opponents = []
    for snake in game_state['board']['snakes']:
        if snake["name"] != player_name:
            opponents.append(snake)
    # Define potential movement directions
    direction_map = {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0)
    }

    # Start with all theoretically possible moves
    possible_moves = []
    for move, (dx, dy) in direction_map.items():
        new_x = head['x'] + dx
        new_y = head['y'] + dy
        # Check if the move is within bounds
        if 0 <= new_x < board_width and 0 <= new_y < board_height:
            possible_moves.append([player_name, move])

    return possible_moves


def get_state_from_move(game_state, player_name, move):
    new_game_state = game_state
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

    # If the snake does not eat, move the head and drop the tail
    new_body = [new_head] + snake["body"][:-1]

    new_game_state["board"]["snakes"][snake_index]["body"] = new_body
    return new_game_state, snake_index


def evaluate(game_state: dict, player_name: str) -> int:
    """Evaluate the state of the game and calculate a heuristic based on strategic priorities."""
    this_snake = next(snake for snake in game_state["board"]["snakes"] if snake["name"] == player_name)
    this_head = this_snake["body"][0]

    # Components of the heuristic
    food_score = calculate_food_score(game_state, this_head)
    separation_score = calculate_separation_score(game_state, this_head, player_name)

    # Combine the scores into a total heuristic value
    # Adjust the weighting factors according to your strategy's needs
    total_score = food_score + separation_score
    return total_score


def calculate_separation_score(game_state, head, player_name):
    """Calculate a score that penalizes being too close to other snakes."""
    penalty_score = 0
    min_safe_distance = 2  # Define a minimum safe distance

    for snake in game_state["board"]["snakes"]:
        if snake["name"] != player_name:
            other_head = snake["body"][0]
            distance = manhattan_distance(head, other_head)
            if distance < min_safe_distance:
                penalty_score -= 20 / (distance + 0.1)  # Penalize close distances more heavily

    return penalty_score


def calculate_food_score(game_state, head):
    """Calculate a score based on the distance to the closest food, considering the risk."""
    closest_food_score = 0
    min_distance = float('inf')
    for food in game_state['board']['food']:
        food_distance = manhattan_distance(food, head)
        # Calculate risk based on proximity of other snakes to this food
        risk_factor = 1
        for snake in game_state['board']['snakes']:
            if snake['body'][0] != head:  # Don't consider our own head
                distance_to_food = manhattan_distance(food, snake['body'][0])
                if distance_to_food < food_distance:
                    risk_factor += 1.5  # Increase the risk if other snakes are closer

        food_score = 100 / (0.000001 + food_distance * risk_factor)  # Adjust food score by risk
        if food_score > closest_food_score:
            closest_food_score = food_score

    return closest_food_score


def manhattan_distance(a, b):
    return abs(a['x'] - b['x']) + abs(a['y'] - b['y'])


def euclidean_distance(a, b):
    return np.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2)


def can_reach_tail(game_state, head, tail):
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
                    f_score[(nx, ny)] = tentative_g_score + manhattan_distance(
                        {
                            'x': nx,
                            'y': ny
                        }, tail)
                    heapq.heappush(open_set, (f_score[(nx, ny)], nx, ny))

    return False


def compute_possible_moves(game_state, player_name):
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    direction_map = {
        "up": (0, 1),
        "down": (0, -1),
        "left": (-1, 0),
        "right": (1, 0)
    }

    my_snake = next((snake for snake in game_state['board']['snakes'] if snake['name'] == player_name), None)

    head = my_snake["body"][0]  # Coordinates of your head
    body = my_snake["body"][1:-1]  # TODO: (bodypart after head, tail not needed??)
    all_snakes = game_state['board']['snakes']
    # Prevent the Battlesnake from moving out of bounds
    # if width is 11, then maximum x coordinate is 10
    # i.e bottomleft corner is (0, 0), topright is (width-1, height-1)
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    tail = game_state["you"]["body"][-1]

    if head["x"] + 1 == board_width:
        is_move_safe["right"] = False
    if head["x"] == 0:
        is_move_safe["left"] = False
    if head["y"] == 0:
        is_move_safe["down"] = False
    if head["y"] + 1 == board_height:
        is_move_safe["up"] = False

    # Self-collision avoidance
    for bodypart in body:
        if (bodypart["x"], bodypart["y"]) == (head["x"] - 1, head["y"]):
            is_move_safe["left"] = False
        if (bodypart["x"], bodypart["y"]) == (head["x"] + 1, head["y"]):
            is_move_safe["right"] = False
        if (bodypart["x"], bodypart["y"]) == (head["x"], head["y"] - 1):
            is_move_safe["down"] = False
        if (bodypart["x"], bodypart["y"]) == (head["x"], head["y"] + 1):
            is_move_safe["up"] = False

    # Avoid collisions with all snakes, including another "SORZWE"
    for snake in all_snakes:
        if snake["name"] == player_name:
            continue
        for bodypart in snake["body"]:
            if (bodypart["x"], bodypart["y"]) == (head["x"] - 1, head["y"]):
                is_move_safe["left"] = False
            if (bodypart["x"], bodypart["y"]) == (head["x"] + 1, head["y"]):
                is_move_safe["right"] = False
            if (bodypart["x"], bodypart["y"]) == (head["x"], head["y"] - 1):
                is_move_safe["down"] = False
            if (bodypart["x"], bodypart["y"]) == (head["x"], head["y"] + 1):
                is_move_safe["up"] = False

    non_traversable = set()
    for snake in all_snakes:
        other_snake_head = snake["body"][0]
        if snake["name"] != player_name:
            non_traversable.add((other_snake_head['x'] + 1, other_snake_head['y']))
            non_traversable.add((other_snake_head['x'] - 1, other_snake_head['y']))
            non_traversable.add((other_snake_head['x'], other_snake_head['y'] + 1))
            non_traversable.add((other_snake_head['x'], other_snake_head['y'] - 1))

    possible_moves = {
        "up": (head['x'], head['y'] + 1),
        "down": (head['x'], head['y'] - 1),
        "left": (head['x'] - 1, head['y']),
        "right": (head['x'] + 1, head['y'])
    }

    for direction, (x, y) in possible_moves.items():
        if (x, y) in non_traversable:
            is_move_safe[direction] = False

    possible_moves = []
    for direction, (dx, dy) in direction_map.items():
        new_x = head['x'] + dx
        new_y = head['y'] + dy
        if 0 <= new_x < board_width and 0 <= new_y < board_height:
            possible_moves.append(direction)

    valid_safe_moves = []
    for direction in possible_moves:
        if is_move_safe.get(direction, True):  # Ensure the direction is still considered safe
            new_state, _ = get_state_from_move(deepcopy(game_state), player_name, direction)
            simulated_head = new_state["you"]["body"][0]
            simulated_tail = new_state["you"]["body"][-1]
            if can_reach_tail(new_state, simulated_head, simulated_tail):
                valid_safe_moves.append([player_name, direction])

    if not valid_safe_moves:
        if possible_moves:
            fallback_possible_moves = []
            for move in possible_moves:
                fallback_possible_moves.append([player_name, move])
            return fallback_possible_moves
        else:
            return [player_name, "down"]

    return valid_safe_moves
