import time

import discord

from discordbot.game.game_instance import GameInstance
from utils.utils import embed_color, x_icon, o_icon, win_color
from maingame.gamehandler import *
from database.database import update_stat, Stat
from utils.utils import debug

running_games = dict()
accepted_rematch = list()


def has_running_game(user_id: int) -> bool:
    """Check if a user has a running game.

    :param user_id: The ID of the user.
    :return: True if the player has a running game, otherwise False.
    """
    if user_id in running_games.keys():
        return True
    return False


def create_running_game(game_instance: GameInstance):
    """Add a game instance to the running games list.

    :param game_instance: The game instance.
    """
    running_games[game_instance.playerX_id] = game_instance
    running_games[game_instance.playerO_id] = game_instance
    debug(f'Created running game (num of running_games: {len(running_games)}/{round(len(running_games) / 2)}, num of '
          f'accepted_rematch: {len(accepted_rematch)})')

def create_board_embed(game_instance: GameInstance) -> discord.Embed:
    """Create the main game board embed.

    :param game_instance: The game instance.
    :return: Discord embed
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
    game_instance.last_active = int(time.time())

    debug(f'A player has chosen. (num of running_games: {len(running_games)}/{round(len(running_games) / 2)}, num of '
          f'accepted_rematch: {len(accepted_rematch)})')

    if has_won is not None:
        game_instance.finished = True
        game_instance.finished_layout = has_won[1]
        update_stat(Stat.TOTAL_GAMES)
        debug(
            f'A player has won. (num of running_games: {len(running_games)}/{round(len(running_games) / 2)}, num of '
            f'accepted_rematch: {len(accepted_rematch)})')
        return

    if board_is_full(game_instance.board):
        game_instance.finished = True
        game_instance.finished_layout = []
        debug(f'A game ended in a draw. (num of running_games: {len(running_games)}/{round(len(running_games) / 2)}, '
              f'num of accepted_rematch: {len(accepted_rematch)})')
        update_stat(Stat.TOTAL_GAMES)
        return

    game_instance.turn = Player.PLAYER_X if current_turn == Player.PLAYER_O else Player.PLAYER_O


def create_win_embed(game_instance: GameInstance, playerX_accepted, playerO_accepted) -> discord.Embed:
    """Create the win embed if a game has a winner.

    :param game_instance: The game instance.
    :param playerX_accepted: True if the Player X has accepted a rematch,
    otherwise False. None if the player has not made a decision yet.
    :param playerO_accepted: True if the Player X has accepted a rematch,
    otherwise False. None if the player has not made a decision yet.
    :return: Discord embed
    """
    if board_is_full(game_instance.board) and not game_instance.finished_layout:
        win_message = 'Draw!'
    elif game_instance.turn == Player.PLAYER_X:
        win_message = f'{game_instance.playerX_name} has won!'
    else:
        win_message = f'{game_instance.playerO_name} has won!'

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
                    f'**__{win_message}__**\n\n'
                    f'**Rematch?**\n'
                    f'*{game_instance.playerX_name}:* {playerx_emote}\n'
                    f'*{game_instance.playerO_name}:* {playero_emote}',
        color=win_color
    )
    return embed


def accept_rematch(game_instance: GameInstance, user_id: int) -> discord.Embed | bool:
    """Accept a game rematch.

    :param game_instance: The game instance.
    :param user_id: The user ID of the user that clicked on the Accepted button.
    :return: Win embed if the other player hasn't decided if he wants a rematch or not, Otherwise True.
    """

    # Set the clicked player to Accepted, and the other one to not selected.
    # (There is a chance that the other player has already accepted a rematch, but the win embed will not show this,
    # because of the new game embed)
    if game_instance.playerO_id != user_id:
        other_player = game_instance.playerO_id
        plO = None
        plX = True
    else:
        other_player = game_instance.playerX_id
        plO = True
        plX = None

    # Remove the current running game and the other player from the accepted_rematch list.
    if other_player in accepted_rematch:
        remove_game(game_instance.playerO_id, game_instance.playerX_id)
        accepted_rematch.remove(other_player)
        debug(
            f'Both players accepted a rematch. Starting new game.'
            f' (num of running_games: {len(running_games)}/{round(len(running_games) / 2)}, num of '
            f'accepted_rematch: {len(accepted_rematch)})')
        return True
    else:
        # Add the player to the accepted rematch list.
        accepted_rematch.append(user_id)
        debug(
            f'A player accepted a rematch. '
            f'(num of running_games: {len(running_games)}/{round(len(running_games) / 2)}, num of '
            f'accepted_rematch: {len(accepted_rematch)})')
        return create_win_embed(game_instance, plX, plO)


def decline_rematch(game_instance: GameInstance, user_id: int) -> discord.Embed:
    """Decline a game rematch.

    :param game_instance: The game instance.
    :param user_id: The user ID of the user that clicked on the Decline button.
    :return: the updated winning embed.
    """
    if game_instance.playerO_id != user_id:
        other_player = game_instance.playerO_id
        player_name = game_instance.playerX_name

        if other_player in accepted_rematch:
            plO = True
            accepted_rematch.remove(other_player)
        else:
            plO = None
        plX = False
    else:
        other_player = game_instance.playerX_id
        player_name = game_instance.playerO_name

        if other_player in accepted_rematch:
            plX = True
            accepted_rematch.remove(other_player)
        else:
            plX = None
        plO = False

    if user_id in accepted_rematch:
        accepted_rematch.remove(user_id)

    remove_game(game_instance.playerO_id, game_instance.playerX_id)

    winning_embed = create_win_embed(game_instance, plX, plO)

    description = winning_embed.description
    #description += f'\n\n*{player_name} declined the rematch. Thanks for playing!*'
    description += f'\n\n*🎄 {player_name} declined the rematch. Merry Christmas and a happy new year! 🎄*'
    winning_embed.description = description

    debug(f'A player declined the rematch. '
          f'(num of running_games: {len(running_games)}/{round(len(running_games) / 2)}, num of '
          f'accepted_rematch: {len(accepted_rematch)})')

    return winning_embed


def remove_game(playerO_id, playerX_id):
    """Remove a running game from the list by the playerO_id and the playerX_id.
    When the ids are not in the list, nothing will happen.

    :param playerO_id: The ID of player O.
    :param playerX_id: The ID of player X.
    """
    try:
        running_games.pop(playerO_id)
        running_games.pop(playerX_id)
    except KeyError:
        pass
    finally:
        debug('Stopped a running game. '
              f'(num of running_games: {len(running_games)}/{round(len(running_games) / 2)}, num of '
              f'accepted_rematch: {len(accepted_rematch)})')
