import time

from discordbot.crossplay.crossplay_player import CpPlayer
from discordbot.game.game_instance import GameInstance
from discordbot.game.game_manager import create_running_game
from maingame.board import create_default_board
from maingame.player import Player

waiting_players = list()


def add_player(cp_player: CpPlayer):
    """Add a player to the lobby.
    If there was someone waiting in the lobby, the opponent will be returned.
    If there was nobody waiting in the lobby, the player will be added to the queue and nothing will be returned.

    :param cp_player: Cross play player information.
    :return: A CpPlayer object if there was somebody waiting in the lobby, otherwise None.
    """
    if len(waiting_players) >= 1:
        opponent = waiting_players.pop(0)
        return opponent
    waiting_players.append(cp_player)
    return None

def start_game(cp_playerX: CpPlayer, cp_playerO: CpPlayer):
    create_running_game(
        GameInstance(
            playerX_id=cp_playerX.discord_id,
            playerO_id=cp_playerO.discord_id,
            playerX_name=cp_playerX.name,
            playerO_name=cp_playerO.name,
            board=create_default_board(),
            turn=Player.PLAYER_X,
            game_messages=[
                cp_playerX.message,
                cp_playerO.message
            ],
            last_active=round(time.time())
        )
    )
