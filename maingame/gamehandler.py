from maingame.player import Player


def update_board(player: Player, pos: int, board: list):
    """Update the maingame layout with the move of the player.

    :param player: The player number that's placing.
    :param pos: The selected position.
    :param board: The current game board.
    :return: updated maingame after move (list)
    """
    board[pos] = player


def is_available(pos: int, board: list) -> bool:
    """Checks is the given location is available.

    :param pos: The chosen position in the given row.
    :param board: The current game board.
    :return: True or False
    """
    return True if board[pos] == Player.NOTHING else False


def player_has_won(board) -> list | None:
    """Checks if a player has won.

    :param board: The current game board.
    :return: When someone wins the game, the player and the winning combination is returned, otherwise None.
    """

    possible_combinations = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]

    for combination in possible_combinations:
        if board[combination[0]] == Player.PLAYER_O and board[combination[1]] == Player.PLAYER_O and \
                board[combination[2]] == Player.PLAYER_O:
            return [Player.PLAYER_O, combination]

        if board[combination[0]] == Player.PLAYER_X and board[combination[1]] == Player.PLAYER_X and \
                board[combination[2]] == Player.PLAYER_X:
            return [Player.PLAYER_X, combination]
    return None


def board_is_full(board: list) -> bool:
    """Check if the board is full.

    :param board: The current game board.
    :return: True when the board is full, otherwise False.
    # """
    return False if Player.NOTHING in board else True
