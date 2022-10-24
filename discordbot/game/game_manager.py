import discord

from discordbot.game.game_instance import GameInstance
from utils.utils import embed_color, x_icon, o_icon
from maingame.gamehandler import *

running_games = dict()


def create_running_game(game_instance: GameInstance):
    """Add a game instance to the running games list.

    :param game_instance: The game instance.
    """
    running_games[game_instance.playerX_id] = game_instance
    running_games[game_instance.playerO_id] = game_instance


def create_board_embed(game_instance: GameInstance):
    """Create the main game board embed.

    :param game_instance: The game instance.
    :return: Embed
    """
    if game_instance.turn == Player.PLAYER_X:
        turn_name = game_instance.playerX_name
    else:
        turn_name = game_instance.playerO_name
    embed = discord.Embed(
        title='TicTacToe',
        description=f'{x_icon} = {game_instance.playerX_name}\n'
                    f'{o_icon} = {game_instance.playerO_name}\n\n'
                    f'*{turn_name}\'s turn*',
        color=embed_color
    )
    return embed


def player_turn(game_instance: GameInstance, pos: int):
    current_turn = game_instance.turn
    update_board(current_turn, pos, game_instance.board)
    has_won = player_has_won(game_instance.board)
    if has_won is not None:
        game_instance.finished = True
        game_instance.finished_layout = has_won[1]
    if current_turn == Player.PLAYER_O:
        game_instance.turn = Player.PLAYER_X
    else:
        game_instance.turn = Player.PLAYER_O
