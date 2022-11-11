from discord import app_commands

from discordbot.commands.help_command import get_help_embed
from discordbot.commands.start_command import *
from discordbot.commands.stop_command import check_stop_command, get_nothing_cancel_embed
from discordbot.views import game_button_view
from request.request_manager import *
from discordbot.game.game_manager import has_running_game

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client=client)
synced = False

# Using local commands for testing instead of public commands.
guildId = '720702767211216928'


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('TicTacToe (testing)!'))
    if not synced:
        await tree.sync(guild=discord.Object(id=guildId))
    print(f'Logged in as {client.user}!')


with open('token.txt', 'r') as token_file:
    token = token_file.readline()


@tree.command(guild=discord.Object(id=guildId), name='help', description='Gives a list of commands that you can use.')
async def help_command(interaction: discord.Interaction):
    embed = get_help_embed()
    await interaction.response.send_message(embed=embed)


@tree.command(guild=discord.Object(id=guildId), name='stop', description='Cancel a request or stop a running maingame.')
async def stop_command(interaction: discord.Interaction):
    if not utils.check_permissions(interaction.channel.permissions_for(interaction.guild.me)):
        await interaction.followup.send(content=utils.get_invalid_perms_message())
        return

    # Get the stop result if a user types the stop command.
    stop_result = check_stop_command(interaction.user.id)
    if not stop_result:
        await interaction.response.send_message(embed=get_nothing_cancel_embed())
    else:
        channel_id = stop_result['channel_id']
        message_id = stop_result['message_id']
        channel = interaction.client.get_channel(channel_id)
        if channel is not None:
            try:
                message = await channel.fetch_message(message_id)
                if stop_result['stop_type'] in ['game', 'rematch']:
                    game_instance = stop_result['game_instance']
                    game_instance.stopped = True
                    game_instance.finished = True
                    if not game_instance.finished_layout:
                        game_instance.finished_layout = []
                    view = game_button_view(game_instance)
                else:
                    view = None

                await message.edit(
                    embed=stop_result['decline_embed'],
                    view=view
                )
            except discord.NotFound:
                pass
        await interaction.response.send_message(embed=stop_result['stop_embed'])


@tree.command(guild=discord.Object(id=guildId), name='start',
              description='Play a match of tic tac toe!')
@app_commands.describe(opponent='Choose a Discord member you want to play against.')
async def start_command(interaction: discord.Interaction, opponent: discord.Member):
    await interaction.response.defer(thinking=True)

    if not utils.check_permissions(interaction.channel.permissions_for(interaction.guild.me)):
        await interaction.followup.send(content=utils.get_invalid_perms_message())
        return

    if opponent.bot:
        await interaction.followup.send(embed=get_invite_bot_embed())
        return

    if interaction.user.id == opponent.id:
        await interaction.followup.send(embed=get_invited_self_embed())
        return

    if has_sent_an_invite(interaction.user.id):
        await interaction.followup.send(embed=get_already_invite_embed())
        return

    if has_running_game(interaction.user.id):
        await interaction.followup.send(embed=is_in_game(True))
        return

    if has_running_game(opponent.id):
        await interaction.followup.send(embed=is_in_game(False, opponent_name=opponent.name))
        return

    message = await interaction.followup.send(embed=get_request_embed(opponent.name, interaction.user.name),
                                              view=start_buttons_view())
    create_invite(opponent.name, interaction.user.name, opponent.id, interaction.user.id, message.id,
                  interaction.channel_id)


client.run(token)
