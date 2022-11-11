import discord

from maingame.player import Player
from utils import utils
from request.request_manager import *
from maingame import board
from discordbot.game.game_instance import GameInstance
from discordbot.game.game_manager import create_board_embed, create_running_game
from discordbot.views import game_button_view


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


def get_decline_request_embed(name: str):
    embed = discord.Embed(
        title='TicTacToe request',
        description=f'*{name} declined the request.*',
        color=utils.error_color)
    return embed


def is_in_game(himself: bool, opponent_name: str = 'NA'):
    if himself:
        title = 'You are currently in a running game!'
        description = 'Type `/stop` to cancel your current request.'
    else:
        title = f'{opponent_name} is already in a game!'
        description = 'You have to wait for this game to end!'
    embed = discord.Embed(
        title=title,
        description=description,
        color=utils.error_color
    )
    return embed


class start_buttons_view(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='Accept', style=discord.ButtonStyle.success, custom_id='accept_match')
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        requests = try_accepting_request(interaction.user.id, interaction.message.id)
        if requests is not False:
            if utils.check_permissions(interaction.channel.permissions_for(interaction.guild.me)):
                accepted_request = requests[0]
                # This code only runs when the bot has the right permission.
                game_instance = GameInstance(
                    playerX_id=accepted_request.invited_id,
                    playerO_id=accepted_request.inviter_id,
                    playerX_name=accepted_request.invited_name,
                    playerO_name=accepted_request.inviter_name,
                    board=board.create_default_board(),
                    turn=Player.PLAYER_X,
                    message_id=accepted_request.message_id,
                    channel_id=accepted_request.channel_id
                )
                create_running_game(game_instance)
                await interaction.message.edit(embed=create_board_embed(game_instance),
                                               view=game_button_view(game_instance))
                # Decline all these requests:
                for request in requests[1]:
                    embed = get_decline_request_embed(request.invited_name)
                    channel = interaction.guild.get_channel(request.channel_id)
                    if channel is not None:
                        message = await channel.fetch_message(request.message_id)
                        if message is not None:
                            await message.edit(embed=embed, view=None)
            else:
                try:
                    await interaction.message.edit(content=utils.get_invalid_perms_message(), view=None, embed=None)
                except discord.errors.Forbidden:
                    pass
        await interaction.response.defer()

    @discord.ui.button(label='Decline', style=discord.ButtonStyle.danger, custom_id='decline_match')
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if decline_request_invited(interaction.user.id, interaction.message.id):
            embed = discord.Embed(
                title='TicTacToe request',
                description=f'*{interaction.user.name} declined the request.*',
                color=utils.error_color)
            await interaction.message.edit(embed=embed, view=None)
        await interaction.response.defer()
