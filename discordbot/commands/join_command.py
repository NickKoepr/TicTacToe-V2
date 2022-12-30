import discord
from utils.utils import embed_color


def create_lobby_embed():
    embed = discord.Embed(
        title='TicTacToe cross server game',
        description='You are in the lobby!\nWaiting for a opponent...',
        color=embed_color
    )
    return embed
