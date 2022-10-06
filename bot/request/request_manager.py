from request import Request

invited_users = {}
inviter_users = {}


def send_invite_to_user(invited_id: int, inviter_id: int, message_id: int):
    """
    Send an invitation to a user for a game.

    :param invided_id: The user ID of the inviter.
    :param inviter_id: The user ID of the member that's invited.
    :param message_id: The message ID of the message.
    """

    request = Request(invited_id, inviter_id, message_id)

    if invited_id in invited_users.keys():
        invited_users[invited_id].append(request)
    else:
        invited_users[invited_id] = [request]
    inviter_id[inviter_id] = request


def has_open_request(inviter_id: int):
    if inviter_id in inviter_users.keys():
        return True
    return False

