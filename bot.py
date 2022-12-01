import asyncio
import sqlite3
import threading

from discord import app_commands
from discord.ext import tasks

from database.database import get_stats, create_tables, update_stat, Stat
from discordbot.commands.help_command import get_help_embed
from discordbot.commands.start_command import *
from discordbot.commands.stop_command import check_stop_command, get_nothing_cancel_embed
from discordbot.game.game_manager import has_running_game, running_games
from discordbot.views import game_button_view
from request.request_manager import *

intents = discord.Intents.default()

synced = False
cancel_time = 10

# Using local commands for testing instead of public commands.
guildId = '720702767211216928'


class TicTacToeClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        self.start_timer.start()
        await self.tree.sync()

    async def on_ready(self):
        await client.change_presence(activity=discord.Game(presence_text()))

        print(f'Logged in as {client.user}!')

    @tasks.loop(seconds=cancel_time)
    async def start_timer(self):
        """Check if there are games or requests that are idle for too long. If so, cancel the game or request."""

        async def cancel_message(guild_id, channel_id, message_id, title, description):
            """Change the active message to a cancel message if the game or request is inactive for a long time.

            :param guild_id: guild ID
            :param channel_id: channel ID
            :param message_id: message ID
            :param title: title of the embed
            :param description: description of the embed
            """
            guild = client.get_guild(guild_id)
            if guild:
                channel = client.get_channel(channel_id)
                if channel:
                    try:
                        message = await channel.fetch_message(message_id)
                        embed = discord.Embed(
                            title=title,
                            description=description,
                            color=utils.error_color
                        )
                        await message.edit(view=None, embed=embed)
                    except discord.errors.HTTPException:
                        pass

        requests = list(inviter_users.values())
        for request in requests.copy():
            current_time = round(time.time())
            if (current_time - request.created_at) > cancel_time:
                decline_request_inviter(request.inviter_id)
                await cancel_message(guild_id=request.guild_id,
                                     channel_id=request.channel_id,
                                     message_id=request.message_id,
                                     title='Request cancelled due to inactivity',
                                     description='This request is cancelled due to inactivity for a long time.')
        games = list(running_games.values())
        for game in games.copy():
            current_time = round(time.time())
            if (current_time - game.last_active) > cancel_time:
                if game.playerO_id in running_games.keys():
                    running_games.pop(game.playerX_id)
                    running_games.pop(game.playerO_id)
                    await cancel_message(guild_id=game.guild_id,
                                         channel_id=game.channel_id,
                                         message_id=game.message_id,
                                         title='Game cancelled due to inactivity',
                                         description='This game is cancelled due to inactivity for a long time.')


client = TicTacToeClient(intents=intents)


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
                      'debug - Turn the debug messages on or off.\n'
                      'presence - Change the presence message on Discord.')
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
            case 'presence':
                presence = input('Please enter a new presence: ').strip()
                presence_text(presence)
                asyncio.run(client.change_presence(activity=discord.Game(presence)))
                print(f'Presence changed to \'{presence}\'!')
            case _:
                print('This command doesn\'t exists! Type help for list of commands.')


def presence_text(text=None):
    if not text:
        with open('presence_text.txt', 'r') as presence_file:
            return presence_file.read()
    else:
        with open('presence_text.txt', 'w') as presence_file:
            presence_file.write(text)


with open('token.txt', 'r') as token_file:
    token = token_file.readline()


@client.tree.command(name='help',
                     description='Gives a list of commands that you can use.')
async def help_command(interaction: discord.Interaction):
    update_stat(Stat.HELP_COMMAND)
    update_stat(Stat.TOTAL_COMMANDS)
    embed = get_help_embed()
    await interaction.response.send_message(embed=embed)


@client.tree.command(name='stop',
                     description='Cancel a request or stop a running maingame.')
async def stop_command(interaction: discord.Interaction):
    update_stat(Stat.STOP_COMMAND)
    update_stat(Stat.TOTAL_COMMANDS)
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


@client.tree.command(name='start',
                     description='Play a match of tic tac toe!')
@app_commands.describe(opponent='Choose a Discord member you want to play against.')
async def start_command(interaction: discord.Interaction, opponent: discord.Member):
    update_stat(Stat.START_COMMAND)
    update_stat(Stat.TOTAL_COMMANDS)
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


create_tables()

threading.Thread(target=console, daemon=True).start()

utils.time_started = time.time()

client.run(token)
