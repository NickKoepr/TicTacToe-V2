import discord

from request.request_manager import has_open_request, inviter_users
from request.request import Request
from discordbot.game.game_manager import has_running_game, running_games
from discordbot.game.game_instance import GameInstance
from discordbot.commands.start_command import get_decline_request_embed
from discordbot.game.game_manager import decline_request
from utils.utils import x_icon, o_icon, error_color, green_color


def request_decline_embed(request: Request):
    return get_decline_request_embed(request.inviter_name)


def game_decline_embed(user_id: int, game_instance: GameInstance):
    if user_id == game_instance.playerO_id:
        username = game_instance.playerO_name
        other_player = game_instance.playerX_name
    else:
        username = game_instance.playerX_name
        other_player = game_instance.playerO_name
    embed = discord.Embed(
        title='TicTacToe',
        description=
        f'{x_icon} = {game_instance.playerX_name}\n'
        f'{o_icon} = {game_instance.playerO_name}\n\n'
        f'**__{other_player} has won!__**\n\n'
        f'*{username} canceled the game.*',
        color=error_color
    )
    return embed


def stop_embed(stop_type: str):
    embed = discord.Embed(
        title=f'Your {stop_type} is cancelled',
        description=f'Your {stop_type} is cancelled successfully.',
        color=green_color
    )
    return embed


def cant_cancel():
    embed = discord.Embed(
        title=f'There is nothing to cancel!',
        description='You can only use the stop command when you are playing a game or if you have an open request.',
        color=error_color
    )
    return embed


def check_stop_command(user_id: int):
    if has_open_request(user_id):
        request = inviter_users[user_id]
        inviter_users.pop()
        return [request.message_id, request_decline_embed(request)]
    elif has_running_game(user_id):
        game_instance: GameInstance = running_games[user_id]
        if not game_instance.finished:
            running_games.pop(game_instance.playerX_id)
            running_games.pop(game_instance.playerO_id)
            return [game_instance.message_id, game_decline_embed(user_id, game_instance)]
        else:
            decline_request(game_instance, user_id)
            return True
    return False
