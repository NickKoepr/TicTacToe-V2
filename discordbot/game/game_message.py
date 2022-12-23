from dataclasses import dataclass


@dataclass
class GameMessage:
    guild_id: int
    channel_id: int
    message_id: int

