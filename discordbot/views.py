import discord

from discordbot.game.game_instance import GameInstance
from discordbot.game.game_manager import player_turn, create_board_embed, create_win_embed, accept_request, \
    create_running_game
from maingame.gamehandler import is_available
from maingame.player import Player
from utils.utils import x_icon, o_icon, debug
from maingame.board import create_default_board


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
            debug('Player clicked on button')
            if is_available(pos, game_instance.board):
                player_turn(game_instance, pos)
                if game_instance.finished:
                    embed = create_win_embed(game_instance, None, None)
                else:
                    embed = create_board_embed(game_instance)
                await interaction.message.edit(embed=embed,
                                               view=game_button_view(game_instance))
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
            embed = accept_request(game_instance, interaction.user.id)
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
                print(game_instance)
                await interaction.message.edit(embed=create_board_embed(game_instance),
                                               view=game_button_view(game_instance))
            else:
                await interaction.message.edit(embed=embed)

        await interaction.response.defer()


class game_button_view(discord.ui.View):
    def __init__(self, game_instance: GameInstance):
        super().__init__()
        for i in range(9):
            self.add_item(game_button(game_instance, i))
        if game_instance.finished:
            self.add_item(request_button(game_instance, 'Accept', discord.ButtonStyle.success))
            self.add_item(request_button(game_instance, 'Decline', discord.ButtonStyle.red))
