import datetime
import time

import discord


def get_help_embed():
    embed = discord.Embed(title='TicTacToe help', color=discord.Color.from_rgb(64, 255, 255),
                          timestamp=datetime.datetime.utcnow())
    embed.add_field(name='**__/start [username]__**', value='**Play a match of tic tac toe!**', inline=False)
    embed.add_field(name='**/help**', value='*Gives a list with commands that you can use.*')
    embed.add_field(name='**/stop**', value='*Cancel a request or stop a running game.*')

    return embed
