# bot.py
import os
from discord.ext import commands
import discord

from tickets import setup_tickets
from comandos import setup_commands

# IDs fornecidos
CATEGORY_ID = 1387269436259434557
LOG_CHANNEL_ID = 1436234566015914077
STAFF_ROLE_ID = 1387269134609420358

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# setup modules
setup_tickets(bot, CATEGORY_ID, LOG_CHANNEL_ID, STAFF_ROLE_ID)
setup_commands(bot)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        await bot.tree.sync()
    except Exception:
        pass

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN não encontrado nas variáveis de ambiente")
    bot.run(TOKEN)
