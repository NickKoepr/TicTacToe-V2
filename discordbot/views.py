import discord

from discordbot.game.game_instance import GameInstance
from discordbot.game.game_manager import player_turn, create_board_embed, create_win_embed, accept_rematch, \
    create_running_game, decline_rematch, remove_game, accepted_rematch
from maingame.gamehandler import is_available
from maingame.player import Player
from utils import utils
from maingame.board import create_default_board


# TODO: Remember to stop the cross server games when one of the messages can't be edited (because of permissions of
# TODO non existence channels/messages/guilds.

class game_button(discord.ui.Button):
    def __init__(self, game_instance: GameInstance, button_id: int):
        emoji = None
        label = None
        button_style = discord.ButtonStyle.gray
        board_place = game_instance.board[button_id]
        if board_place == Player.PLAYER_O:
            emoji = utils.o_icon
        elif board_place == Player.PLAYER_X:
            emoji = utils.x_icon
        else:
            label = '\u2800'
        if game_instance.finished:
            finished_layout = game_instance.finished_layout
            if button_id in finished_layout:
                button_style = discord.ButtonStyle.success

        super().__init__(label=label, emoji=emoji, style=button_style, custom_id=f'{button_id}',
                         row=button_id // 3, disabled=game_instance.finished)
        self.game_instance = game_instance

    async def callback(self, interaction: discord.Interaction):
        game_instance = self.game_instance
        player_x = game_instance.playerX_id
        player_o = game_instance.playerO_id
        pos = int(interaction.data['custom_id'])

        if game_instance.turn == Player.PLAYER_X and interaction.user.id == player_x \
                or game_instance.turn == Player.PLAYER_O and interaction.user.id == player_o:
            if not game_instance.stopped and \
                    utils.check_permissions(interaction.channel.permissions_for(interaction.guild.me),
                                            interaction.channel):
                if is_available(pos, game_instance.board):
                    player_turn(game_instance, pos)

                    if game_instance.finished:
                        embed = create_win_embed(game_instance, None, None)
                    else:
                        embed = create_board_embed(game_instance)

                    view = game_button_view(game_instance)

                    await interaction.message.edit(embed=embed,
                                                   view=view)

                    other_message = await change_other_message(
                        game_instance=game_instance,
                        interaction=interaction,
                        embed=embed,
                        view=view
                    )
                    # TODO stop a game when the message is deleted.
            else:
                await invalid_perms(game_instance, interaction)
        await interaction.response.defer()


class request_button(discord.ui.Button):
    def __init__(self, game_instance: GameInstance, button_type: str, style: discord.ButtonStyle):
        super().__init__(label=button_type, style=style, custom_id=f'{button_type}',
                         row=4)
        self.game_instance = game_instance
        self.button_type = button_type

    async def callback(self, interaction: discord.Interaction):
        game_instance = self.game_instance

        if game_instance.playerO_id == interaction.user.id or game_instance.playerX_id == interaction.user.id:
            if not game_instance.stopped and \
                    utils.check_permissions(interaction.channel.permissions_for(interaction.guild.me),
                                            interaction.channel):

                if self.button_type == 'Accept':
                    if interaction.user.id not in accepted_rematch:
                        embed = accept_rematch(game_instance, interaction.user.id)
                        if embed is True:
                            game_instance.playerX_id, game_instance.playerO_id = \
                                game_instance.playerO_id, game_instance.playerX_id

                            game_instance.playerX_name, game_instance.playerO_name = \
                                game_instance.playerO_name, game_instance.playerX_name

                            game_instance.finished = False
                            game_instance.finished_layout = []
                            game_instance.turn = Player.PLAYER_X
                            game_instance.board = create_default_board()
                            create_running_game(game_instance)

                            new_embed = create_board_embed(game_instance)
                            view = game_button_view(game_instance)

                            await interaction.message.edit(embed=new_embed,
                                                           view=view)

                            other_message = await change_other_message(
                                game_instance=game_instance,
                                interaction=interaction,
                                embed=new_embed,
                                view=view
                            )
                            # TODO stop the running game when the bot wasn't able to change the other message.

                        else:
                            await interaction.message.edit(embed=embed)
                            other_message = await change_other_message(
                                game_instance=game_instance,
                                interaction=interaction,
                                embed=embed
                            )
                            # TODO stop the running game when the bot wasn't able to change the other message.
                elif self.button_type == 'Decline':
                    embed = decline_rematch(game_instance, interaction.user.id)
                    game_instance.stopped = True
                    view = game_button_view(game_instance)
                    await interaction.message.edit(embed=embed,
                                                   view=view)
                    other_message = await change_other_message(
                        game_instance=game_instance,
                        interaction=interaction,
                        embed=embed,
                        view=view
                    )
                    # TODO stop the running game when the bot wasn't able to change the other message.
            else:
                await invalid_perms(game_instance, interaction)
        await interaction.response.defer()


class game_button_view(discord.ui.View):
    def __init__(self, game_instance: GameInstance):
        super().__init__()
        self.timeout = None
        for i in range(9):
            self.add_item(game_button(game_instance, i))
        if game_instance.finished and not game_instance.stopped:
            self.add_item(request_button(game_instance, 'Accept', discord.ButtonStyle.success))
            self.add_item(request_button(game_instance, 'Decline', discord.ButtonStyle.red))


async def invalid_perms(game_instance: GameInstance, interaction: discord.Interaction):
    """Stop the game and try to edit the game message if the bot has not the right permissions.

    :param game_instance: game instance
    :param interaction: interaction
    """
    game_instance.stopped = True
    remove_game(game_instance.playerO_id, game_instance.playerX_id)
    try:
        await interaction.message.edit(content=utils.get_invalid_perms_message(
            interaction.channel), view=None, embed=None)
    except discord.errors.Forbidden:
        pass


async def change_other_message(game_instance: GameInstance, interaction: discord.Interaction, embed: discord.Embed,
                               view: discord.ui.View | bool | None = False) -> None | bool:
    """Change a message other than the clicked message (used for games with more than one message).

    :param game_instance: The game instance.
    :param interaction: The interaction.
    :param embed: The embed to change to.
    :param view: The view to change to, or None for no view. Don't specify this value if you don't want to change
    the current view.
    :return: False when no message(s) is/are edited, None when the bot can't edit (one of) the message(s) and True if
    the message(s) is/are changed.
    """
    if len(game_instance.game_messages) > 1:
        for game_message in game_instance.game_messages:
            if game_message.message_id != interaction.message.id:
                message = await utils.check_for_message(
                    client=interaction.client,
                    guild_id=game_message.guild_id,
                    channel_id=game_message.channel_id,
                    message_id=game_message.message_id
                )
                if message is not None:
                    if view == False:
                        await message.edit(embed=embed)
                        return True
                    else:
                        await message.edit(view=view, embed=embed)
                        return True
                return None
    return False
