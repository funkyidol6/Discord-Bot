from discord.ext import commands
from discord.ext.commands import MissingPermissions
import discord
import datetime
import json
import discord.ext.commands
import requests
from dispie import EmbedCreator
import os
import discord.ext
from dotenv import load_dotenv


load_dotenv()
 # Replace with your testing guild id

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

guild_ids = [1224008327621513316,1223917167741894667]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!",intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,activity=discord.Activity(name="you",type=discord.ActivityType.watching))
    print(f"Logged in as {bot.user} | Owner : {bot.owner_id}")
    print(f"Commands : {bot.commands}")
    print(f"Help Command : {bot.help_command}")


# command will be global if guild_ids is not specified
@bot.hybrid_command(description="Ping command",guild_ids=guild_ids)
async def ping(interaction: commands.Context):
    await interaction.send("Pong!")
    await bot.tree.sync()


@bot.hybrid_command(description='Kick a member',guild_ids=guild_ids)
@commands.has_permissions(kick_members=True)
async def kick(interaction: commands.Context,member:discord.Member,*,reason = None):
    reason = "N/A" if reason == None else reason
    await member.kick(reason=reason)
    await interaction.send(f"user {member} has been kicked")
    await bot.tree.sync()

@kick.error
async def kick_error(interaction: commands.Context,error):
    if isinstance(error,commands.MissingPermissions):
        await interaction.send("you dont have permission to kick")
    else:
        await interaction.send(f"An unknown error has occured.\nDebug : {error}")
    await bot.tree.sync()

@bot.hybrid_command(description='ban a member',guild_ids= guild_ids )
@commands.has_permissions(ban_members=True)
async def ban(interaction: commands.Context,member:discord.Member,*,reason = None):
    await member.ban(reason=reason)
    await interaction.send(f"user {member} has been banned")
    await bot.tree.sync()

@ban.error
async def ban_error(interaction: commands.Context,error):
    if isinstance(error,commands.MissingPermissions):
        await interaction.send("you dont have permission to ban")
        await bot.tree.sync()

@bot.hybrid_command(description='unban a member',guild_ids= guild_ids )
@commands.has_permissions(ban_members=True)
async def unban(interaction: commands.Context,member:discord.User,*,reason = None):
    guild = interaction.guild
    await guild.unban(user = member)
    await interaction.send(f"user {member} has been unbanned")
    await bot.tree.sync()

@bot.hybrid_command(description='mute a member from voice channels',guild_ids= guild_ids )
@commands.has_guild_permissions(mute_members=True)
async def mute_voice(interaction: commands.Context,member:discord.Member,*,reason=None):
    await member.edit(mute=True,reason=reason)
    await interaction.send(f"{member} voice muted")


@bot.hybrid_command(description='unmute a member from voice channels',guild_ids= guild_ids )
@commands.has_guild_permissions(mute_members=True)
async def unmute_voice(interaction: commands.Context,member:discord.Member,*,reason=None):
    await member.edit(mute=False,reason=reason)
    await interaction.send(f"{member} voice unmuted")


@bot.hybrid_command(description='deafen a member',guild_ids= guild_ids )
@commands.has_guild_permissions(deafen_members=True)
async def deafen(interaction: commands.Context,member:discord.Member,*,reason=None):
    await member.edit(deafen=True,reason=reason)
    await interaction.send(f"{member} deafened")
    await bot.tree.sync()

@bot.hybrid_command(description='undeafen a member',guild_ids= guild_ids )
@commands.has_guild_permissions(deafen_members=True)
async def undeafen(interaction: commands.Context,member:discord.Member,*,reason=None):
    await member.edit(deafen=False,reason=reason)
    await interaction.send(f"{member} undeafened")
    await bot.tree.sync()

@bot.hybrid_command(description='enable slowmode',guild_ids= guild_ids )
@commands.has_permissions(manage_channels=True)
async def slowmode(interaction: commands.Context,time,*,reason=None):
    await interaction.channel.edit(slowmode_delay=time,reason=reason)
    await interaction.send(f"slowmode enabled for {time} seconds")
    await bot.tree.sync()

@unban.error
async def unban_error(interaction: commands.Context,error):
    if isinstance(error,commands.MissingPermissions):
        await interaction.send("you dont have permission to unban")
        await bot.tree.sync()


@bot.hybrid_command(description='timeout a member',guild_ids= guild_ids)
@commands.has_permissions(moderate_members=True)
async def timeout(interaction: commands.Context,member:discord.Member,time,*,reason=None):
    try:
        resume = datetime.timedelta(minutes=int(time))
        await member.edit(timed_out_until=discord.utils.utcnow() + resume,reason=reason)
        await interaction.send(f"{member} timed out for {time} minutes")
        await bot.tree.sync()
    except discord.Forbidden:
        await interaction.send('you dont have permission to timeout members')
        await bot.tree.sync()


@bot.hybrid_command(description='removes timeout from a member',guild_ids= guild_ids)
@commands.has_permissions(moderate_members=True)
async def removetimeout(interaction: commands.Context,member:discord.Member,*,reason=None):
    try:
        await member.edit(timed_out_until=discord.utils.utcnow(),reason=reason)
        await interaction.send(f"removed {member} from timeout")
    except discord.Forbidden:
        await interaction.send('you dont have permission to remove timeout from members')
    finally:
        await bot.tree.sync()

@bot.hybrid_command(description="mutes a member from texting",guild_ids=guild_ids)
@commands.has_guild_permissions(mute_members=True)
async def mute_text(interaction:commands.Context,member:discord.Member,*,reason=None):
    role = discord.utils.get(interaction.guild.roles,name="Muted")
    guild = interaction.guild
    if role not in guild.roles:
        perm = discord.Permissions(send_messages=False)
        guild.create_role(name="Muted",permissions=perm)
    await member.add_roles(role,reason=reason)
    await interaction.send(f'{member} was muted from text channels')
    await bot.tree.sync()

@bot.hybrid_command(description="unmutes a member from texting",guild_ids=guild_ids)
@commands.has_guild_permissions(mute_members=True)
async def unmute_text(interaction:commands.Context,member:discord.Member,*,reason=None):
    role = discord.utils.get(interaction.guild.roles,name="Muted")
    await member.remove_roles(role,reason=reason)
    await interaction.send(f'{member} was unmuted from text channels')
    await bot.tree.sync()

@bot.hybrid_command(description="tell a joke",guild_ids=guild_ids)
async def joke(interaction:commands.Context):
    data = requests.get(r"https://official-joke-api.appspot.com/random_joke")
    tt = json.loads(data.text)
    await interaction.send(f"{tt['setup']}\n{tt['punchline']}")
    await bot.tree.sync()

@bot.hybrid_command(description="tell a chuck norris joke",guild_ids=guild_ids)
async def chuck_norris(interaction:commands.Context):
    data = requests.get(r"https://api.chucknorris.io/jokes/random")
    tt = json.loads(data.text)
    await interaction.send(f"{tt['value']}")


@bot.hybrid_command(description='Create a custom embed',guild_ids=guild_ids)
async def create_embed(interaction:commands.Context):
    mbed = EmbedCreator(bot=bot)
    await interaction.send(embed=mbed.get_default_embed,view=mbed)
    await bot.tree.sync()

@bot.hybrid_command(description='Send a message as an Embed',guild_ids=guild_ids)
async def quick_mbed(interaction:commands.Context,title:str,description:str,color:int=000000):
    mbed = discord.Embed()
    mbed.colour = color
    mbed.title = title
    mbed.description = description
    mbed.set_footer(text=interaction.author)
    mbed.timestamp = datetime.datetime.now()
    await interaction.send(embed=mbed)
    await bot.tree.sync()


bot.run(os.getenv(key="TOKEN"))
