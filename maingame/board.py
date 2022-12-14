from maingame.player import Player


def create_default_board() -> list:
    """Generate a default (empty) board.

    :return: a list with the default board.
    """
    board = []
    for i in range(9):
        board.append(Player.NOTHING)
    return board
