from discord import app_commands
from discordbot.commands.help_command import get_help_embed
from discordbot.commands.start_command import *
from request.request_manager import *

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
    await interaction.response.send_message('test')


@tree.command(guild=discord.Object(id=guildId), name='start',
              description='Play a match of tic tac toe!')
@app_commands.describe(opponent='Choose a Discord member you want to play against.')
async def start_command(interaction: discord.Interaction, opponent: discord.Member):
    await interaction.response.defer(thinking=True)

    if not utils.check_permissions(interaction.channel.permissions_for(interaction.guild.me)):
        await interaction.followup.send(embed=utils.get_invalid_perms_embed())
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

    message = await interaction.followup.send(embed=get_request_embed(opponent.name, interaction.user.name),
                                              view=start_buttons_view())
    create_invite(opponent.name, interaction.user.name, opponent.id, interaction.user.id, message.id,
                  interaction.channel_id)


client.run(token)
