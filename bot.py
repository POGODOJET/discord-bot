import discord
import os
from discord.ext import commands

# Configurar intents corretamente
intents = discord.Intents.default()
intents.message_content = True  # Permite ler o conteúdo das mensagens
intents.members = True          # Permite ver membros (se precisar)
intents.presences = False       # Pode deixar False se não for usar status

bot = commands.Bot(command_prefix="/", intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} conectado com sucesso!")

@bot.command()
async def enviar(ctx, *, mensagem):
    await ctx.send(mensagem)

bot.run(TOKEN)
