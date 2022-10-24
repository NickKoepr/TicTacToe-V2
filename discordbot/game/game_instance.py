from dataclasses import dataclass
from maingame.player import Player


@dataclass
class GameInstance:
    playerX_id: int
    playerO_id: int
    playerX_name: int
    playerO_name: int
    board: list
    turn: Player
    message_id: int
    channel_id: int
    finished: bool
    finished_layout: list = None
