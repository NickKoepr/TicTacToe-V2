import discord

from discordbot.game.game_instance import GameInstance
from utils.utils import embed_color, x_icon, o_icon, win_color
from maingame.gamehandler import *

running_games = dict()
accepted_rematch = list()


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
    """Place the player's choice on the game board.

    :param game_instance: The game instance.
    :param pos: The chosen position.
    """
    current_turn = game_instance.turn
    update_board(current_turn, pos, game_instance.board)
    has_won = player_has_won(game_instance.board)
    if has_won is not None:
        game_instance.finished = True
        game_instance.finished_layout = has_won[1]
        return
    if current_turn == Player.PLAYER_O:
        game_instance.turn = Player.PLAYER_X
    else:
        game_instance.turn = Player.PLAYER_O


def create_win_embed(game_instance: GameInstance, playerX_accepted, playerO_accepted):
    if game_instance.turn == Player.PLAYER_X:
        win_name = game_instance.playerX_name
    else:
        win_name = game_instance.playerO_name

    if playerX_accepted is None:
        playerx_emote = ''
    elif playerX_accepted:
        playerx_emote = ':white_check_mark:'
    else:
        playerx_emote = ':x:'

    if playerO_accepted is None:
        playero_emote = ''
    elif playerO_accepted:
        playero_emote = ':white_check_mark:'
    else:
        playero_emote = ':x:'

    embed = discord.Embed(
        title='TicTacToe',
        description=f'{x_icon} = {game_instance.playerX_name}\n'
                    f'{o_icon} = {game_instance.playerO_name}\n\n'
                    f'**__{win_name} has won!__**\n\n'
                    f'**Rematch?**\n'
                    f'*{game_instance.playerX_name}:* {playerx_emote}\n'
                    f'*{game_instance.playerO_name}:* {playero_emote}',
        color=win_color
    )
    return embed


def accept_request(game_instance: GameInstance, user_id: int):
    if game_instance.playerO_id != user_id:
        other_player = game_instance.playerO_id
        plO = None
        plX = True
    else:
        other_player = game_instance.playerX_id
        plO = True
        plX = None

    if other_player in accepted_rematch:
        running_games.pop(game_instance.playerX_id)
        running_games.pop(game_instance.playerO_id)
        print(running_games)
        return True
        pass
    else:
        accepted_rematch.append(user_id)
        return create_win_embed(game_instance, plX, plO)
