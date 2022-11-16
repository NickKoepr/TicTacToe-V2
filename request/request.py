from dataclasses import dataclass


@dataclass
class Request:
    invited_name: str
    inviter_name: str
    invited_id: int
    inviter_id: int
    guild_id: int
    message_id: int
    channel_id: int
    created_at: int
