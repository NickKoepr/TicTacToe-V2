import discord
from utils import colors


def get_request_embed(invited_name: str, inviter_name: str, ):
    embed = discord.Embed(
        title='TicTacToe request',
        description=f'{invited_name}, {inviter_name} invited you to a match of TicTacToe!',
        color=colors.embed_color
    )
    return embed


def get_already_invite_embed():
    embed = discord.Embed(
        title='You have already sent a request!',
        description='Type `/stop` to cancel your current request.',
        color=colors.error_color
    )
    return embed


def get_invite_bot_embed():
    embed = discord.Embed(
        title='Invalid user',
        description='You cannot play TicTacToe with a bot!',
        color=colors.error_color
    )
    return embed


def get_invited_self_embed():
    embed = discord.Embed(
        title='Invalid user',
        description='You cannot play TicTacToe with yourself :(',
        color=colors.error_color
    )
    return embed


class start_buttons_view(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='Accept', style=discord.ButtonStyle.success, custom_id='accept_match')
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.edit(content='test', embed=None, view=None)

    @discord.ui.button(label='Decline', style=discord.ButtonStyle.danger, custom_id='decline_match')
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.edit(content='test', embed=None, view=None)
