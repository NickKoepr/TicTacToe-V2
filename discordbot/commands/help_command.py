import datetime
from utils import utils

import discord


def get_help_embed():
    embed = discord.Embed(title='TicTacToe help', color=utils.embed_color,
                          timestamp=datetime.datetime.utcnow())
    embed.add_field(name='**__/start [username]__**', value='**Play a match of tic tac toe!**', inline=False)
    embed.add_field(name='**/help**', value='*Gives a list with commands that you can use.*')
    embed.add_field(name='**/stop**', value='*Cancel a request or stop a running maingame.*')

    return embed
