import discord
from discord import app_commands
from commands.help_command import get_help_embed

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


@tree.command(guild=discord.Object(id=guildId), name='stop', description='Cancel a request or stop a running game.')
async def stop_command(interaction: discord.Interaction):
    await interaction.response.send_message('test')


@tree.command(guild=discord.Object(id=guildId), name='start',
              description='Play a match of tic tac toe!')
@app_commands.describe(opponent='Choose a Discord member you want to play against.')
async def start_command(interaction: discord.Interaction, opponent: discord.Member):
    await interaction.response.send_message(f'test: {opponent.name}')


client.run(token)
