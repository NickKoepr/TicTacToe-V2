import discord

embed_color = discord.Color.from_rgb(64, 255, 255)
error_color = discord.Color.from_rgb(255, 87, 51)

def check_permissions(permissions: discord.Permissions):
    """
    Check if the bot has all the permissions.

    :param permissions: discord.Permissions object.
    :return: True if the bot has all the permissions, otherwise False.
    """
    if permissions.embed_links and permissions.read_message_history and permissions.send_messages and \
            permissions.view_channel:
        return True
    return False
