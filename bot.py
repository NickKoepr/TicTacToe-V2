import os.path

from discord import app_commands
from discord.ext import tasks

from database.database import get_stats, create_tables, update_stat, Stat
from discordbot.commands.help_command import get_help_embed
from discordbot.commands.start_command import *
from discordbot.commands.stop_command import check_stop_command, get_nothing_cancel_embed
from discordbot.game.game_manager import has_running_game, running_games, remove_game
from discordbot.views import game_button_view
from request.request_manager import *

intents = discord.Intents.default()

synced = False
cancel_time = 60 * 5


class TicTacToeClient(discord.AutoShardedClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        self.start_timer.start()
        await self.tree.sync()

    async def on_ready(self):
        await client.change_presence(activity=discord.Game(presence_text()))

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
                        if not utils.check_permissions(channel.permissions_for(guild.me), channel):
                            await message.edit(
                                content=utils.get_invalid_perms_message(channel), view=None)
                            return
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
                debug('Cancelled invite due to inactivity:')
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
                    debug('Cancelled game due to inactivity:')
                    remove_game(game.playerO_id, game.playerX_id)
                    await cancel_message(guild_id=game.guild_id,
                                         channel_id=game.channel_id,
                                         message_id=game.message_id,
                                         title='Game cancelled due to inactivity',
                                         description='This game is cancelled due to inactivity for a long time.')


client = TicTacToeClient(intents=intents, shard_count=2)

def presence_text(text=None):
    if not text:
        with open('presence_text.txt', 'r') as presence_file:
            return presence_file.read()
    else:
        with open('presence_text.txt', 'w') as presence_file:
            presence_file.write(text)


if os.path.isfile('token.txt'):
    with open('token.txt', 'r') as token_file:
        token = token_file.readline()
else:
    with open('token.txt', 'w') as token_file:
        input_token = input('Thanks for using the TicTacToe Discord bot!\nPlease paste your bot token here: ').strip()
        token_file.write(input_token)
        token = input_token


@client.tree.command(name='help',
                     description='Gives a list of commands that you can use.')
@app_commands.guild_only()
async def help_command(interaction: discord.Interaction):
    debug('help command sent')
    update_stat(Stat.HELP_COMMAND)
    update_stat(Stat.TOTAL_COMMANDS)
    embed = get_help_embed()
    await interaction.response.send_message(embed=embed)


@client.tree.command(name='stop',
                     description='Cancel a request or stop a running maingame.')
@app_commands.guild_only()
async def stop_command(interaction: discord.Interaction):
    debug('stop command sent')
    update_stat(Stat.STOP_COMMAND)
    update_stat(Stat.TOTAL_COMMANDS)
    await interaction.response.defer(thinking=True)

    if not utils.check_permissions(interaction.channel.permissions_for(interaction.guild.me), interaction.channel):
        await interaction.followup.send(content=utils.get_invalid_perms_message(interaction.channel))
        debug('Bot has not the required permissions')
        return

    # Get the stop result if a user types the stop command.
    stop_result = check_stop_command(interaction.user.id)
    if not stop_result:
        await interaction.followup.send(embed=get_nothing_cancel_embed())
        debug('Player has nothing to cancel')
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
        await interaction.followup.send(embed=stop_result['stop_embed'])


@client.tree.command(name='start',
                     description='Play a match of tic tac toe!')
@app_commands.describe(opponent='Choose a Discord member you want to play against.')
@app_commands.guild_only()
async def start_command(interaction: discord.Interaction, opponent: discord.Member):
    debug('start command sent')
    update_stat(Stat.START_COMMAND)
    update_stat(Stat.TOTAL_COMMANDS)
    await interaction.response.defer(thinking=True)

    if not utils.check_permissions(interaction.channel.permissions_for(interaction.guild.me), interaction.channel):
        await interaction.followup.send(content=utils.get_invalid_perms_message(interaction.channel))
        debug('Bot has not the required permissions')
        return

    if opponent.bot:
        await interaction.followup.send(embed=get_invite_bot_embed())
        debug('Player tried to invite a Discord bot')
        return

    if interaction.user.id == opponent.id:
        await interaction.followup.send(embed=get_invited_self_embed())
        debug('Player tried to invite himself')
        return

    if has_sent_an_invite(interaction.user.id):
        await interaction.followup.send(embed=get_already_invite_embed())
        debug('Player has already sent a invite')
        return

    if has_running_game(interaction.user.id):
        await interaction.followup.send(embed=is_in_game(True))
        debug('Player has already a running game')
        return

    if has_running_game(opponent.id):
        await interaction.followup.send(embed=is_in_game(False, opponent_name=opponent.name))
        debug('Opponent has a running game')
        return

    message = await interaction.followup.send(embed=get_request_embed(opponent.name, interaction.user.name),
                                              view=start_buttons_view())
    create_invite(opponent.name, interaction.user.name, opponent.id, interaction.user.id, interaction.guild_id,
                  message.id,
                  interaction.channel_id)


create_tables()

utils.time_started = time.time()

client.run(token)
