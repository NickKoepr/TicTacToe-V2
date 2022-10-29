import discord

from discordbot.game.game_instance import GameInstance
from utils.utils import embed_color, x_icon, o_icon, win_color
from maingame.gamehandler import *

running_games = dict()
accepted_rematch = list()


def has_running_game(user_id: int):
    if user_id in running_games.keys():
        return True
    return False


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
    """Create the win embed if a game has a winner.

    :param game_instance: The game instance.
    :param playerX_accepted: True if the Player X has accepted a rematch,
    otherwise False or None if this player hasn't made a decision yet.
    :param playerO_accepted: True if the Player O has accepted a rematch,
    otherwise False or None if this player hasn't made a decision yet.
    :return: Embed
    """
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
        running_games.pop(game_instance.playerX_id)
        running_games.pop(game_instance.playerO_id)
        accepted_rematch.remove(other_player)
        print(running_games)
        return True
        pass
    else:
        # Add the player to the accepted rematch list.
        accepted_rematch.append(user_id)
        return create_win_embed(game_instance, plX, plO)


def decline_request(game_instance: GameInstance, user_id: int):
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
        plO = False
        if other_player in accepted_rematch:
            plX = True
            accepted_rematch.remove(other_player)
        else:
            plX = None

    if user_id in accepted_rematch:
        accepted_rematch.remove(user_id)

    running_games.pop(game_instance.playerO_id)
    running_games.pop(game_instance.playerX_id)
    winning_embed = create_win_embed(game_instance, plX, plO)
    print(accepted_rematch)
    print(running_games)
    description = winning_embed.description
    description += f'\n\n*{player_name} declined the rematch. Thanks for playing!*'
    winning_embed.description = description
    return winning_embed
