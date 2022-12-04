import discord

from maingame.player import Player
from utils import utils
from request.request_manager import *
from maingame import board
from discordbot.game.game_instance import GameInstance
from discordbot.game.game_manager import create_board_embed, create_running_game
from discordbot.views import game_button_view


def get_request_embed(invited_name: str, inviter_name: str) -> discord.Embed:
    """Return the request embed.

    :param invited_name: The name of the invited player.
    :param inviter_name: The name of the player who has sent the invite.
    :return: Discord embed
    """
    embed = discord.Embed(
        title='TicTacToe request',
        description=f'**{invited_name}**, **{inviter_name}** invited you to a match of TicTacToe!',
        color=utils.embed_color
    )
    return embed


def get_already_invite_embed() -> discord.Embed:
    """Return the already sent a request embed.

    :return: Discord embed
    """
    embed = discord.Embed(
        title='You have already sent a request!',
        description='Type `/stop` to cancel your current request.',
        color=utils.error_color
    )
    return embed


def get_invite_bot_embed() -> discord.Embed:
    """Return the invalid user embed for a bot.

    :return: Discord embed
    """
    embed = discord.Embed(
        title='Invalid user',
        description='You cannot play TicTacToe with a bot!',
        color=utils.error_color
    )
    return embed


def get_invited_self_embed():
    """Return the invalid user embed for the user itself.

    :return: Discord embed
    """
    embed = discord.Embed(
        title='Invalid user',
        description='You cannot play TicTacToe with yourself :(',
        color=utils.error_color
    )
    return embed


def get_decline_request_embed(name: str) -> discord.Embed:
    """Return the decline request embed.

    :param name: The name of the user that declined the request.
    :return: Discord embed
    """
    embed = discord.Embed(
        title='TicTacToe request',
        description=f'*{name} declined the request.*',
        color=utils.error_color)
    return embed


def is_in_game(himself: bool, opponent_name: str = 'NA') -> discord.Embed:
    """Return the is already in a game embed.

    :param himself: True if the user was sending the command for himself.
    :param opponent_name: The name of the opponent if himself is False.
    :return: Discord embed
    """
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
        self.timeout = None

    @discord.ui.button(label='Accept', style=discord.ButtonStyle.success, custom_id='accept_match')
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        requests = try_accepting_request(interaction.user.id, interaction.message.id)
        if requests is not False:
            if utils.check_permissions(interaction.channel.permissions_for(interaction.guild.me), interaction.channel):
                accepted_request = requests[0]
                # This code only runs when the bot has the right permission.
                game_instance = GameInstance(
                    playerX_id=accepted_request.invited_id,
                    playerO_id=accepted_request.inviter_id,
                    playerX_name=accepted_request.invited_name,
                    playerO_name=accepted_request.inviter_name,
                    board=board.create_default_board(),
                    turn=Player.PLAYER_X,
                    guild_id=accepted_request.guild_id,
                    message_id=accepted_request.message_id,
                    channel_id=accepted_request.channel_id,
                    last_active=int(time.time())
                )
                create_running_game(game_instance)
                await interaction.message.edit(embed=create_board_embed(game_instance),
                                               view=game_button_view(game_instance))
                # Decline all these requests:
                for request in requests[1]:
                    embed = get_decline_request_embed(request.invited_name)
                    guild = interaction.client.get_guild(request.guild_id)
                    if guild is not None:
                        channel = guild.get_channel(request.channel_id)
                        if channel is not None:
                            try:
                                message = await channel.fetch_message(request.message_id)
                                await message.edit(embed=embed, view=None)
                            except discord.errors.HTTPException:
                                pass

            else:
                try:
                    await interaction.message.edit(content=utils.get_invalid_perms_message(interaction.channel),
                                                   view=None, embed=None)
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
