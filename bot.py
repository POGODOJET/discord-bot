import discord
import os
from discord.ext import commands

# Configurar intents corretamente
intents = discord.Intents.default()
intents.message_content = True  # Permite ler o conteúdo das mensagens
intents.members = True          # Permite ver membros (se precisar)
intents.presences = False       # Pode deixar False se não for usar status

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} conectado com sucesso!")

@bot.command()
async def enviar(ctx, *, mensagem):
    await ctx.send(mensagem)

@bot.command()
async def anuncio(ctx):
    embed = discord.Embed(
        title="🟪 PAINEL:",
        description="[https://heavencity.com/](https://heavencity.com/)",
        color=0xA02D8E  # Roxo
    )

    embed.add_field(
        name="🏙️ CONNECT HEAVEN CITY:",
        value="```189.127.164.145:22749```",
        inline=False
    )

    embed.set_thumbnail(url="https://i.imgur.com/AvL2Qck.png")  # substitua pela imagem que quiser
    embed.set_footer(text="🟪 Atenciosamente Heaven City")

    await ctx.send(content="@everyone", embed=embed)

# Token seguro vindo das variáveis da Railway
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)




