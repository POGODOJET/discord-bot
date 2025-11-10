# comandos.py

import discord
from discord.ext import commands
from tickets import send_ticket_panel


# ===============================================================
# ✅ Setup dos módulos de comandos
# ===============================================================
def setup_commands(bot):
    bot.add_cog(_MiscCommands(bot))


# ===============================================================
# ✅ Classe com os comandos
# ===============================================================
class _MiscCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ comando: !teste
    @commands.command()
    async def teste(self, ctx, *, mensagem):
        embed = discord.Embed(description=mensagem, color=0xA02D8E)
        embed.set_thumbnail(url="https://heavencity.com/suaimagem.png")
        embed.set_footer(text="💜 Atenciosamente Heaven City")

        await ctx.send(content="@everyone", embed=embed)

    # ✅ comando: !enviar
    @commands.command()
    async def enviar(self, ctx, *, mensagem):
        await ctx.send(mensagem)

    # ✅ comando: !anuncio
    @commands.command()
    async def anuncio(self, ctx):
        embed = discord.Embed(
            title="🟪 PAINEL:",
            description="🌐 [Clique aqui para acessar o site](https://heavencity.com/)",
            color=0xA02D8E
        )

        embed.add_field(
            name="🏙️ CONNECT HEAVEN CITY:",
            value="```189.127.164.145:22749```",
            inline=False
        )

        embed.set_thumbnail(url="https://i.imgur.com/AvL2Qck.png")
        embed.set_footer(text="🟪 Atenciosamente Heaven City")

        await ctx.send(content="@everyone", embed=embed)
