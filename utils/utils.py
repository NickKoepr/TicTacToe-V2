import discord

embed_color = discord.Color.from_rgb(64, 255, 255)
error_color = discord.Color.from_rgb(255, 87, 51)
win_color = discord.Color.from_rgb(212, 175, 55)
green_color = discord.Color.from_rgb(50, 205, 50)
x_icon = '<:Xicon:1033418837728698459>'
o_icon = '<:Oicon:1033420163497852978>'
debug_enabled = True


def check_permissions(permissions: discord.Permissions, channel) -> bool:
    """Check if the bot has all the permissions.

    :param permissions: discord.Permissions object.
    :param channel: The message channel.
    :return: True if the bot has all the permissions, otherwise False.
    """
    if permissions.embed_links and permissions.read_message_history and permissions.send_messages and \
            permissions.view_channel:
        if type(channel) == discord.VoiceChannel:
            if permissions.connect:
                return True
            return False
        return True
    return False


def get_invalid_perms_message(channel) -> str:
    """Get invalid perms message.

    :param channel: The message channel.
    :return: String.
    """

    message = "**__I don't have the right permissions!__**\n" \
              "Please give me the permissions `embed_links`, `read_message_history`, " \
              "`send_messages` and `view_channel`\n" \
              "Otherwise I will not work!\n" \
              "*(please note that the bot also needs these permissions on this channel!)*"
    if type(channel) == discord.VoiceChannel:
        message += "\n\n**__Because this is a voice channel, I also need the permission `connect`.\n" \
                   "If you give this permission, I also work in the voice channels text channels!__**"
    return message


def debug(msg):
    if debug_enabled:
        print(f'DEBUG: {msg}')
