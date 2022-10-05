from player import Player


def update_board(player: Player, pos: int, game_layout: list):
    """
    Update the game layout with the move of the player.

    :param player: The player number that's placing.
    :param pos: The selected position.
    :param game_layout: The current game layout.
    :return: updated game after move (list)
    """
    game_layout[pos] = player


def is_available(pos: int, game_layout: list):
    """
    Checks is the given location is available.

    :param row: The chosen row.
    :param pos: The chosen position in the given row.
    :param game_layout: The current game layout.
    :return: True or False
    """
    if game_layout[pos] == Player.NOTHING:
        return True
    else:
        return False


def player_has_won(game_layout):
    """
    Checks if a player has won.

    :param game_layout: The current game layout.
    :return: The Player when someone has won the game, otherwise
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
        if game_layout[combination[0]] == Player.PLAYER_O and game_layout[combination[1]] == Player.PLAYER_O and \
                game_layout[combination[2]] \
                == Player.PLAYER_O:
            return Player.PLAYER_O

        if game_layout[combination[0]] == Player.PLAYER_X and game_layout[combination[1]] == Player.PLAYER_X and \
                game_layout[combination[2]] \
                == Player.PLAYER_X:
            return Player.PLAYER_X

        return None
