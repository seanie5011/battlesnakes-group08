import typing
from copy import deepcopy


def brs(alpha: int, beta: int, depth: int, turn: str, game_state: typing.Dict,
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

    # Base case: if depth is 0, return the evaluation of the board.
    if depth <= 0:
        return evaluate(game_state, player_name)

    # Determine the moves based on the turn.
    if turn == 'MAX':
        moves = get_possible_moves(game_state, player_name)
        next_turn = 'MIN'
    else:
        moves = []
        for opponent in opponents:  # Extend this list based on the number of players.
            moves.extend(get_possible_moves(game_state, opponent))
        next_turn = 'MAX'

    best_value = float('-inf') if turn == 'MAX' else float('inf')

    # Explore each move.
    for agent_name, move in moves:
        new_state = get_state_from_move(game_state, agent_name, move)
        value = -brs(
            -beta, -alpha, depth - 1, next_turn, new_state, agent_name, [
                player_name, *[
                    opponent
                    for opponent in opponents if opponent != agent_name
                ]
            ])

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


def get_possible_moves(game_state: typing.Dict, player: str) -> list[str]:
    # This function should return a list of all possible moves for the given player.
    # returns a list like [[name, move], [name, move], etc.]
    return [[player, "up"], [player, "down"], [player, "left"],
            [player, "right"]]


def get_state_from_move(game_state: typing.Dict, player: str,
                        move: list[str]) -> typing.Dict:
    # This function should modify the game state by making the specified move.
    new_game_state = deepcopy(game_state)

    this_index = -1
    for snake in new_game_state["board"]["snakes"]:
        this_index += 1
        if snake["name"] == player:
            break
        else:
            continue
    bodyparts = new_game_state["board"]["snakes"][this_index]["body"]

    new_bodyparts = []
    for bodypart in bodyparts[0::-1]:
        new_bodyparts.insert(0, bodypart)

    moves_to_coord_change_x = {"up": 0, "down": 0, "left": -1, "right": 1}
    moves_to_coord_change_y = {"up": 1, "down": -1, "left": 0, "right": 0}
    next_x = bodyparts[0]["x"] + moves_to_coord_change_x[move]
    next_y = bodyparts[0]["y"] + moves_to_coord_change_y[move]
    new_bodyparts.insert(0, {"x": next_x, "y": next_y})

    new_game_state["board"]["snakes"][this_index]["body"] = new_bodyparts
    return new_game_state


def evaluate(game_state: typing.Dict, player: typing.AnyStr) -> int:
    """A simple evaluation function that could prioritize staying alive"""
    # Example: prioritize staying away from edges and other snakes
    this_index = -1
    for index, snake in enumerate(game_state["board"]["snakes"]):
        if snake["name"] == player:
            this_index = index
            break
        else:
            continue
    this_snake = game_state["board"]["snakes"][this_index]
    head = this_snake["body"][0]
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    score = 0

    # Prefer staying towards the center
    score += (board_width - head['x']) + (board_height - head['y'])

    return int(score)
