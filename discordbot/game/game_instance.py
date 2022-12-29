from dataclasses import dataclass
from maingame.player import Player


@dataclass
class GameInstance:
    playerX_id: int
    playerO_id: int
    playerX_name: str
    playerO_name: str
    board: list
    turn: Player
    game_messages: list
    last_active: int
    finished: bool = False
    finished_layout: list = None
    stopped: bool = False
