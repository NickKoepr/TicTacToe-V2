import time

import discord

embed_color = discord.Color.from_rgb(64, 255, 255)
error_color = discord.Color.from_rgb(255, 87, 51)
win_color = discord.Color.from_rgb(212, 175, 55)
green_color = discord.Color.from_rgb(50, 205, 50)
x_icon = '<:PlayerX:1033418837728698459>'
o_icon = '<:PlayerO:1033420163497852978>'
debug_enabled = False
bot_version = '2.0'
time_started = 0


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


def debug(msg: str) -> None:
    """Place a message in the console if debug is toggled on.

    :param msg: The message.
    """
    if debug_enabled:
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print(f'[{date} DEBUG] {msg}')


def get_uptime() -> str:
    """Get the uptime from the bot.

    :return: String with the uptime from the bot.
    """
    different_time = round(time.time() - time_started)
    seconds = different_time
    minutes = (seconds // 60)
    hours = (minutes // 60)
    days = hours // 24
    return f'{days} day(s), {hours % 24} hour(s), {minutes % 60} minute(s) and {seconds % 60} second(s).'
