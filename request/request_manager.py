from request.request import Request

invited_users = dict()
inviter_users = dict()


# TEST CODE - IGNORE!
from dataclasses import dataclass


# @dataclass
# class Request:
#     invited_name: str
#     inviter_name: str
#     invited_id: int
#     inviter_id: int
#     message_id: int
#     channel_id: int

# TEST CODE - IGNORE!
def get_stats():
    print(f'INVITED USERS:{invited_users}')
    print(f'INVITER USERS:{inviter_users}')


def create_invite(invited_name: str, inviter_name: str, invited_id: int, inviter_id: int, message_id: int,
                  channel_id: int):
    """
    Send an invitation to a user for a maingame.

    :param inviter_name: The name of the inviter.
    :param invited_name: The name of the person that's invited.
    :param invited_id: The user ID of the invited member.
    :param inviter_id: The user ID of the inviter.
    :param message_id: The message ID of the message.
    :param channel_id: The channel ID of the channel.
    """

    request = Request(invited_name, inviter_name, invited_id, inviter_id, message_id, channel_id)

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
    """
    Try accepting an invite request with the invited_id and the message_id.

    :param invited_id: The user ID of the invited member.
    :param message_id: The message ID of the message.
    :return: False when there is no request to accept, otherwise return a list with the accepted request as the first
    element and a list with declined requests as a second element.
    """

    decline_requests = []
    if invited_id in invited_users.keys():
        # Get all the invites that the user received (invited_id)
        all_invites = invited_users[invited_id]
        for invite in all_invites:
            if invite.message_id == message_id:
                # Add all the invites to decline_requests, but without the accepted invite.
                decline_requests = all_invites
                decline_requests.remove(invite)
                # Go over all the requests, and take the inviter_id. Then remove all the inviters out of the
                # inviter dict.
                for decline_request in decline_requests:
                    inviter_users.pop(decline_request.inviter_id)
                inviter_id = invite.inviter_id
                invited_users.pop(invited_id)

                # Check if the invited person has sent a maingame request to a player.
                if invited_id in inviter_users:
                    # Go over all invites and check if the invited id is equal to the inviter_id.
                    for inv in invited_users[inviter_users[invited_id].invited_id]:
                        if inv.inviter_id == invited_id:
                            # When true, add the request to the decline_requests.
                            decline_requests.append(inv)
                            all_inv = invited_users[inv.invited_id]
                            inviter_users.pop(invited_id)
                            if len(all_inv) == 1:
                                invited_users.pop(inv.invited_id)
                            else:
                                all_inv.remove(inv)

                # Remove the inviter from the inviter_list.
                inviter_users.pop(inviter_id)
                # If the invited_users list contains inviter_id, remove the inviter_id from that list.
                if inviter_id in invited_users:
                    inviter_invites = invited_users[inviter_id]
                    for inviter_invite in inviter_invites:
                        decline_requests.append(inviter_invite)
                        inviter_users.pop(inviter_invite.inviter_id)
                    invited_users.pop(inviter_id)

                return [invite, decline_requests]
    return False


def decline_request_invited(invited_id: int, message_id: int):
    """Decline a request based on the inviter id.

    :param invited_id: The user ID of the invited member.
    :param message_id: The message ID.
    :return: True if the invite is cancelled, otherwise False.
    """

    if invited_id in invited_users.keys():
        invites = invited_users[invited_id]
        for request in invites:
            if request.message_id == message_id and request.invited_id == invited_id:
                if len(invited_users[invited_id]) == 1:
                    invited_users.pop(invited_id)
                else:
                    invited_users[invited_id].remove(request)
                inviter_users.pop(request.inviter_id)
                return True
    return False


def decline_request_inviter(inviter_id: int):
    """Decline a request based on the inviter id.

    :param inviter_id: The user ID of the inviter.
    :return: True if the invite is cancelled, otherwise False.
    """
    if inviter_id in inviter_users.keys():
        request = inviter_users[inviter_id]
        invited_id = request.invited_id
        if len(invited_users[invited_id]) == 1:
            invited_users.pop(invited_id)
        else:
            invited_users[invited_id].remove(request)
        inviter_users.pop(inviter_id)
        return True
    return False


def has_sent_an_invite(inviter_id: int):
    """
    Return False when the given member ID has an open invite request, otherwise return True.

    :param inviter_id: The user ID of the inviter.
    :return: True or False
    """
    if inviter_id in inviter_users.keys():
        return True
    else:
        return False

# TEST CODE - IGNORE!
# create_invite('h', 'h', 1, 2, 1, 1)
# create_invite('h', 'h', 2, 1, 2, 1)
# create_invite('h', 'h', 2, 3, 3, 1)
# create_invite('h', 'h', 1, 4, 4, 1)
# create_invite('h', 'h', 1, 5, 5, 1)
# create_invite('h', 'h', 3, 6, 9, 1)
# create_invite('h', 'h', 3, 7, 8, 1)
# create_invite('h', 'h', 6, 10, 10, 1)
# create_invite('h', 'h', 6, 11, 11, 1)
# print(invited_users)
# print(inviter_users)
# print(decline_request_inviter(4))
# print()
# print(invited_users)
# print(inviter_users)
