from request import Request

invited_users = dict()
inviter_users = dict()


def create_invite(invited_id: int, inviter_id: int, message_id: int):
    """
    Send an invitation to a user for a game.

    :param invited_id: The user ID of the inviter.
    :param inviter_id: The user ID of the member that's invited.
    :param message_id: The message ID of the message.
    """

    request = Request(invited_id, inviter_id, message_id)

    if invited_id in invited_users.keys():
        invited_users[invited_id].append(request)
    else:
        invited_users[invited_id] = [request]

    inviter_users[inviter_id] = request


def has_open_request(inviter_id: int):
    if inviter_id in inviter_users.keys():
        return True
    return False


def try_accepting_request(invited_id: int, message_id: int):
    decline_requests = []
    if invited_id in invited_users.keys():
        all_invites = invited_users[invited_id]
        for invite in all_invites:
            if invite.message_id == message_id:
                decline_requests = all_invites
                decline_requests.remove(invite)
                for decline_request in decline_requests:
                    inviter_users.pop(decline_request.inviter_id)
                inviter_id = invite.inviter_id

                invited_users.pop(invited_id)

                if invited_id in inviter_users:
                    for inv in invited_users[inviter_users[invited_id].invited_id]:
                        if inv.inviter_id == invited_id:
                            decline_requests.append(inv)
                            all_inv = invited_users[inv.invited_id]
                            inviter_users.pop(invited_id)
                            if len(all_inv) == 1:
                                invited_users.pop(inv.invited_id)
                            else:
                                all_inv.remove(inv)

                inviter_users.pop(inviter_id)
                if inviter_id in invited_users:
                    inviter_invites = invited_users[inviter_id]
                    for inviter_invite in inviter_invites:
                        decline_requests.append(inviter_invite)
                        inviter_users.pop(inviter_invite.inviter_id)
                    invited_users.pop(inviter_id)

            return [invite, decline_requests]

    return False
