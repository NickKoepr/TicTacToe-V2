import discord
from utils import colors


def get_request_embed(invited_name: str, inviter_name: str, ):
    embed = discord.Embed(
        title='TicTacToe request',
        description=f'${invited_name}, {inviter_name} invited you to a match of Tic Tac Toe!',
        color=colors.embed_color
    )
