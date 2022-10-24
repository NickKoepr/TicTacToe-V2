import discord

from discordbot.game.game_instance import GameInstance
from maingame.player import Player
from utils.utils import x_icon, o_icon


class game_button(discord.ui.Button):
    def __init__(self, game_instance: GameInstance, button_id: int):
        emoji = None
        label = None
        board_place = game_instance.board[button_id]
        if board_place == Player.PLAYER_O:
            emoji = o_icon
        elif board_place == Player.PLAYER_X:
            emoji = x_icon
        else:
            label = '\u2800'
        super().__init__(label=label, emoji=emoji, style=discord.ButtonStyle.grey, custom_id=f'TTTID{button_id}',
                         row=button_id // 3)

    async def callback(self, interaction: discord.Interaction):
        print(f'clicked button with id: {interaction.data["custom_id"].replace("TTTID", "")}')
        await interaction.response.defer()


class game_button_view(discord.ui.View):
    def __init__(self, game_instance: GameInstance):
        super().__init__()
        for i in range(9):
            self.add_item(game_button(game_instance, i))
