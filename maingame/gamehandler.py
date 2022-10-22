from player import Player


def update_board(player: Player, pos: int, board: list):
    """
    Update the maingame layout with the move of the player.

    :param player: The player number that's placing.
    :param pos: The selected position.
    :param board: The current game board.
    :return: updated maingame after move (list)
    """
    board[pos] = player


def is_available(pos: int, board: list):
    """
    Checks is the given location is available.

    :param row: The chosen row.
    :param pos: The chosen position in the given row.
    :param board: The current game board.
    :return: True or False
    """
    if board[pos] == Player.NOTHING:
        return True
    else:
        return False


def player_has_won(board):
    """
    Checks if a player has won.

    :param board: The current game board.
    :return: The Player when someone has won the maingame, otherwise
    """

    possible_combinations = [[0, 1, 2],
                             [3, 4, 5],
                             [6, 7, 8],
                             [0, 3, 6],
                             [1, 4, 7],
                             [2, 5, 8],
                             [0, 4, 8],
                             [2, 4, 6]]

    for combination in possible_combinations:
        if board[combination[0]] == Player.PLAYER_O and board[combination[1]] == Player.PLAYER_O and \
                board[combination[2]] \
                == Player.PLAYER_O:
            return Player.PLAYER_O

        if board[combination[0]] == Player.PLAYER_X and board[combination[1]] == Player.PLAYER_X and \
                board[combination[2]] \
                == Player.PLAYER_X:
            return Player.PLAYER_X

        return None
