from dataclasses import dataclass


@dataclass
class Request:
    invited_id: int
    inviter_id: int
    message_id: int
