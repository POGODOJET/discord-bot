# comandos.py
import discord
from discord.ext import commands
from tickets import send_ticket_panel




def setup_commands(bot):
bot.add_cog(_MiscCommands(bot))


class _MiscCommands(commands.Cog):
def __init__(self, bot):
self.bot = bot


@commands.command()
async def teste(self, ctx, *, mensagem):
embed = discord.Embed(description=mensagem, color=0xA02D8E)
embed.set_thumbnail(url="https://heavencity.com/suaimagem.png")
embed.set_footer(text="💜 Atenciosamente Heaven City")
await ctx.send(content="@everyone", embed=embed)


@commands.command()
async def enviar(self, ctx, *, mensagem):
await ctx.send(mensagem)


@commands.command()
async def anuncio(self, ctx):
embed = discord.Embed(title="🟪 PAINEL:", description="🌐 [Clique aqui para acessar o site](https://heavencity.com/)", color=0xA02D8E)
embed.add_field(name="🏙️ CONNECT HEAVEN CITY:", value=
