import discord

from discordbot.game.game_instance import GameInstance
from discordbot.game.game_manager import player_turn, create_board_embed
from maingame.gamehandler import is_available
from maingame.player import Player
from utils.utils import x_icon, o_icon


class game_button(discord.ui.Button):
    def __init__(self, game_instance: GameInstance, button_id: int):
        emoji = None
        label = None
        button_style = discord.ButtonStyle.gray
        board_place = game_instance.board[button_id]
        if board_place == Player.PLAYER_O:
            emoji = o_icon
        elif board_place == Player.PLAYER_X:
            emoji = x_icon
        else:
            label = '\u2800'
        if game_instance.finished_layout is not None:
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
        print(interaction.data)
        if game_instance.turn == Player.PLAYER_X and interaction.user.id == player_x \
                or game_instance.turn == Player.PLAYER_O and interaction.user.id == player_o:
            if is_available(pos, game_instance.board):
                player_turn(game_instance, pos)
                await interaction.message.edit(embed=create_board_embed(game_instance),
                                               view=game_button_view(game_instance))
        await interaction.response.defer()


class game_button_view(discord.ui.View):
    def __init__(self, game_instance: GameInstance):
        super().__init__()
        for i in range(9):
            self.add_item(game_button(game_instance, i))
