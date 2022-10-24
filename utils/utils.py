import discord

embed_color = discord.Color.from_rgb(64, 255, 255)
error_color = discord.Color.from_rgb(255, 87, 51)
x_icon = '<:Xicon:1033418837728698459>'
o_icon = '<:Oicon:1033420163497852978>'

def check_permissions(permissions: discord.Permissions):
    """Check if the bot has all the permissions.

    :param permissions: discord.Permissions object.
    :return: True if the bot has all the permissions, otherwise False.
    """
    if permissions.embed_links and permissions.read_message_history and permissions.send_messages and \
            permissions.view_channel:
        return True
    return False


def get_invalid_perms_embed():
    """Get invalid perms embed.

    :return: Embed.
    """
    return discord.Embed(
        title='Invalid permissions!',
        color=discord.Color.red(),
        description='I don\'t have all the permissions that I need to function!\n I need ' \
           'the permissions `embed_links`, `read_message_history`, `send_messages`, `view_chanel`!'
    )
