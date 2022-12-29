from dataclasses import dataclass
from discordbot.game.game_message import GameMessage

@dataclass
class CpPlayer:
    name: str
    discord_id: int
    message: GameMessage