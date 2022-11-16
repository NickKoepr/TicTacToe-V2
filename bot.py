import sqlite3
import threading
import asyncio

from discord import app_commands

from database.database import get_stats
from discordbot.commands.help_command import get_help_embed
from discordbot.commands.start_command import *
from discordbot.commands.stop_command import check_stop_command, get_nothing_cancel_embed
from discordbot.game.game_manager import has_running_game, running_games
from discordbot.views import game_button_view
from request.request_manager import *

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client=client)
synced = False

# Using local commands for testing instead of public commands.
guildId = '720702767211216928'


def console():
    connection = sqlite3.connect('tictactoe.db')
    cursor = connection.cursor()
    while True:
        user_input = input().strip().lower()
        match user_input:
            case 'help':
                print('TicTacToe console commands\n'
                      'stats - Get different stats from the bot.\n'
                      'stop - Shut down the Discord bot.\n'
                      'debug - Turn the debug messages on or off.')
            case 'stats':
                stats = get_stats(cursor)
                print(f'TicTacToe Discord bot stats:\n'
                      f'Bot version: {utils.bot_version}\n'
                      f'Latency: {round(client.latency * 1000)}ms\n'
                      f'Bot uptime: {utils.get_uptime()}\n'
                      f'Active games: {len(running_games)}\n'
                      f'Active requests: {len(inviter_users)}\n'
                      f'Current server count: {len(client.guilds)}\n'
                      f'Total commands send: {stats["total_commands"]}\n'
                      f'- Total start commands sent: {stats["start_command"]}\n'
                      f'- Total help commands sent: {stats["help_command"]}\n'
                      f'- Total stop commands sent: {stats["stop_command"]}\n'
                      f'Total games played: {stats["total_games"]}')
            case 'stop':
                print('Not implemented yet!')
            case 'debug':
                match utils.debug_enabled:
                    case True:
                        utils.debug_enabled = False
                        print('The debugger is now off!')
                    case False:
                        utils.debug_enabled = True
                        print('The debugger is now on!')
            case _:
                print('This command doesn\'t exists! Type help for list of commands.')


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('TicTacToe (testing)!'))
    if not synced:
        await tree.sync(guild=discord.Object(id=guildId))
    print(f'Logged in as {client.user}!')


with open('token.txt', 'r') as token_file:
    token = token_file.readline()


@tree.command(guild=discord.Object(id=guildId), name='help',
              description='Gives a list of commands that you can use.')
async def help_command(interaction: discord.Interaction):
    embed = get_help_embed()
    await interaction.response.send_message(embed=embed)


@tree.command(guild=discord.Object(id=guildId), name='stop',
              description='Cancel a request or stop a running maingame.')
async def stop_command(interaction: discord.Interaction):
    if not utils.check_permissions(interaction.channel.permissions_for(interaction.guild.me), interaction.channel):
        await interaction.followup.send(content=utils.get_invalid_perms_message(interaction.channel))
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

    if not utils.check_permissions(interaction.channel.permissions_for(interaction.guild.me), interaction.channel):
        await interaction.followup.send(content=utils.get_invalid_perms_message(interaction.channel))
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
    create_invite(opponent.name, interaction.user.name, opponent.id, interaction.user.id, interaction.guild_id,
                  message.id,
                  interaction.channel_id)


if __name__ == '__main__':
    threading.Thread(target=console, daemon=True).start()

    utils.time_started = time.time()

    client.run(token)
