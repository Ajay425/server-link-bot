import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
client=discord.Client(intents=intents)
TOKEN = 'xxxx'

#Command to trigger the bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send("https://discord.gg/MehwPd9f")

bot.run(TOKEN)