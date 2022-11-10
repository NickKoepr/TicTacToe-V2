import discord

from request.request_manager import has_open_request, inviter_users
from request.request import Request
from discordbot.game.game_manager import has_running_game, running_games
from discordbot.game.game_instance import GameInstance
from discordbot.commands.start_command import get_decline_request_embed
from discordbot.game.game_manager import decline_request
from utils.utils import x_icon, o_icon, error_color, green_color
from request.request_manager import decline_request_inviter


def get_request_decline_embed(request: Request):
    return get_decline_request_embed(request.inviter_name)


def get_game_decline_embed(user_id: int, game_instance: GameInstance):
    match user_id:
        case game_instance.playerO_id:
            username = game_instance.playerO_name
            other_player = game_instance.playerX_name
        case _:
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


def get_stop_embed(stop_type: str):
    embed = discord.Embed(
        title=f'Your {stop_type} is cancelled',
        description=f'Your {stop_type} is cancelled successfully.',
        color=green_color
    )
    return embed


def get_nothing_cancel_embed():
    embed = discord.Embed(
        title=f'There is nothing to cancel!',
        description='You can only use the stop command when you are playing a game or if you have an open request.',
        color=error_color
    )
    return embed


def check_stop_command(user_id: int):
    if has_open_request(user_id):
        request = inviter_users[user_id]
        decline_request_inviter(user_id)
        return {
            'stop_type': 'request',
            'stop_embed': get_stop_embed('request'),
            'message_id': request.message_id,
            'channel_id': request.channel_id,
            'decline_embed': get_request_decline_embed(request)
        }
    elif has_running_game(user_id):
        game_instance: GameInstance = running_games[user_id]
        if not game_instance.finished:
            return {
                'stop_type': 'game',
                'stop_embed': get_stop_embed('game'),
                'message_id': game_instance.message_id,
                'channel_id': game_instance.channel_id,
                'decline_embed': get_game_decline_embed(user_id, game_instance),
                'game_instance': game_instance
            }
        else:
            return {
                'stop_type': 'rematch',
                'stop_embed': get_stop_embed('rematch'),
                'message_id': game_instance.message_id,
                'channel_id': game_instance.channel_id,
                'decline_embed': decline_request(game_instance, user_id),
                'game_instance': game_instance
            }
    return False
