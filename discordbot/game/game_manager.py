import discord

from discordbot.game.game_instance import GameInstance
from utils.utils import embed_color

running_games = dict()


def create_running_game(game_instance: GameInstance):
    running_games[game_instance.playerX_id] = game_instance
    running_games[game_instance.playerO_id] = game_instance


def create_board_embed(game_instance: GameInstance):
    if game_instance.turn.PLAYER_X:
        turn_name = game_instance.playerX_name
    else:
        turn_name = game_instance.playerO_name
    embed = discord.Embed(
        title='TicTacToe',
        description=f'<:Xicon:1033418837728698459> = {game_instance.playerX_name}\n'
                    f'<:Oicon:1033420163497852978> = {game_instance.playerO_name}\n\n'
                    f'*{turn_name}\'s turn*',
        color=embed_color
    )
    return embed
