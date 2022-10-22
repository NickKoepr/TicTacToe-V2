import discord

from utils import utils
from request.request_manager import *


def get_request_embed(invited_name: str, inviter_name: str, ):
    embed = discord.Embed(
        title='TicTacToe request',
        description=f'**{invited_name}**, **{inviter_name}** invited you to a match of TicTacToe!',
        color=utils.embed_color
    )
    return embed


def get_already_invite_embed():
    embed = discord.Embed(
        title='You have already sent a request!',
        description='Type `/stop` to cancel your current request.',
        color=utils.error_color
    )
    return embed


def get_invite_bot_embed():
    embed = discord.Embed(
        title='Invalid user',
        description='You cannot play TicTacToe with a bot!',
        color=utils.error_color
    )
    return embed


def get_invited_self_embed():
    embed = discord.Embed(
        title='Invalid user',
        description='You cannot play TicTacToe with yourself :(',
        color=utils.error_color
    )
    return embed


class start_buttons_view(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='Accept', style=discord.ButtonStyle.success, custom_id='accept_match')
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        get_stats()
        requests = try_accepting_request(interaction.user.id, interaction.message.id)
        get_stats()
        if requests is not False:
            if utils.check_permissions(interaction.channel.permissions_for(interaction.guild.me)):
                accepted_request = requests[0]
                # This code only runs when the bot has the right permission.
                await interaction.message.edit(content='goedemorgen', view=None, embed=None)
                # Decline all these requests:
                for request in requests[1]:
                    embed = discord.Embed(
                        title='TicTacToe request',
                        description=f'*{request.inviter_name} declined the request.*',
                        color=utils.error_color)
                    channel = interaction.guild.get_channel(request.channel_id)
                    if channel is not None:
                        message = await channel.fetch_message(request.message_id)
                        if message is not None:
                            await message.edit(embed=embed, view=None)
            else:
                await interaction.message.edit(embed=utils.get_invalid_perms_embed(), view=None)
        await interaction.response.defer()

    @discord.ui.button(label='Decline', style=discord.ButtonStyle.danger, custom_id='decline_match')
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        get_stats()
        if decline_request(interaction.user.id, interaction.message.id):
            get_stats()
            embed = discord.Embed(
                title='TicTacToe request',
                description=f'*{interaction.user.name} declined the request.*',
                color=utils.error_color)
            await interaction.message.edit(embed=embed, view=None)
        await interaction.response.defer()
