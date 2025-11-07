import discord
import os
from discord.ext import commands
from discord import app_commands, Interaction
import asyncio
from discord import Interaction
from datetime import datetime

# Configurar intents corretamente
intents = discord.Intents.default()
intents.message_content = True  # Permite ler o conteúdo das mensagens
intents.members = True          # Permite ver membros (se precisar)
intents.presences = False       # Pode deixar False se não for usar status

# IDs enviados por você ✅
CATEGORY_ID = 1387269436259434557
LOG_CHANNEL_ID = 1436234566015914077
STAFF_ROLE_ID = 1387269134609420358

bot = commands.Bot(command_prefix="!", intents=intents)

ticket_count = 0
blacklist = set()

# ============================
# ✅ BOT ONLINE
# ============================
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    await bot.tree.sync()


# ============================
# ✅ SELECT MENU
# ============================
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Suporte Geral", emoji="🔔"),
            discord.SelectOption(label="Financeiro", emoji="💰"),
            discord.SelectOption(label="Reportar Bug", emoji="🐞"),
            discord.SelectOption(label="Ativação Produto/Plano", emoji="✅"),
        ]

        super().__init__(
            placeholder="Clique aqui para selecionar o assunto",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: Interaction):

        # ✅ Blacklist
        if interaction.user.id in blacklist:
            await interaction.response.send_message(
                "🚫 Você está bloqueado de abrir tickets.",
                ephemeral=True
            )
            return

        global ticket_count
        ticket_count += 1

        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        staff_role = guild.get_role(STAFF_ROLE_ID)
        logs = guild.get_channel(LOG_CHANNEL_ID)

        ticket_name = f"ticket-{ticket_count:03d}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True),
            staff_role: discord.PermissionOverwrite(view_channel=True),
        }

        ticket_channel = await guild.create_text_channel(
            name=ticket_name,
            category=category,
            overwrites=overwrites
        )

        # ✅ ENVIAR LOG
        await logs.send(
            f"✅ **Ticket criado:** {ticket_channel.mention}\n"
            f"👤 **Usuário:** {interaction.user.mention}\n"
            f"📂 **Categoria:** {self.values[0]}"
        )

        # ✅ Resposta oculta ao usuário
        await interaction.response.send_message(
            "✅ Seu ticket foi criado!",
            ephemeral=True
        )

        # ✅ Embed de boas-vindas
        embed = discord.Embed(
            title="📨 Bem-vindo ao seu Ticket!",
            description=(
                f"Olá {interaction.user.mention},\n"
                f"Um membro da equipe irá te atender em breve.\n\n"
                f"📌 **Assunto selecionado:** `{self.values[0]}`"
            ),
            color=0x2b2d31
        )

        view = CloseTicketView()

        await ticket_channel.send(embed=embed, view=view)


# ============================
# ✅ VIEW COM SELECT MENU
# ============================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# ============================
# ✅ BOTÃO DE FECHAR TICKET
# ============================
class CloseTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="🔒 Fechar Ticket",
            style=discord.ButtonStyle.danger
        )

    async def callback(self, interaction: Interaction):
        channel = interaction.channel

        await interaction.response.send_message(
            "✅ O ticket será fechado em 5 segundos...",
            ephemeral=True
        )

        await asyncio.sleep(5)

        # ✅ Gerar transcrição
        transcript_text = ""
        async for msg in channel.history(limit=None, oldest_first=True):
            transcript_text += f"[{msg.created_at}] {msg.author}: {msg.content}\n"

        filename = f"{channel.name}-transcript.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        guild = interaction.guild
        logs = guild.get_channel(LOG_CHANNEL_ID)

        # ✅ Enviar transcrição nos logs
        await logs.send(
            f"🔒 **Ticket fechado:** {channel.name}\n"
            f"👤 Fechado por: {interaction.user.mention}",
            file=discord.File(filename)
        )

        await channel.delete()


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton())


# ============================
# ✅ COMANDO PARA ENVIAR O PAINEL
# ============================
@bot.command()
async def ticketpainel(ctx):
    embed = discord.Embed(
        title="📨 Sistema de Tickets",
        description="Selecione abaixo a categoria do seu atendimento:",
        color=0x2b2d31
    )

    await ctx.send(embed=embed, view=TicketView())


# ============================
# ✅ COMANDOS DA STAFF
# ============================

@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def blacklist_add(ctx, member: discord.Member):
    blacklist.add(member.id)
    await ctx.send(f"🚫 {member.mention} foi **bloqueado** de abrir tickets.")


@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def blacklist_remove(ctx, member: discord.Member):
    blacklist.discard(member.id)
    await ctx.send(f"✅ {member.mention} foi **desbloqueado**.")
# ============================================================ FINAL BOT TICKET=====================================================================================================

@bot.command()
async def teste(ctx, *, mensagem):
    embed = discord.Embed(
        description=mensagem,
        color=0xA02D8E  # escolha sua cor
    )

    embed.set_thumbnail(url="https://heavencity.com/suaimagem.png")  # opcional
    embed.set_footer(text="💜 Atenciosamente Heaven City")

    await ctx.send(content="@everyone", embed=embed)

@bot.command()
async def enviar(ctx, *, mensagem):
    await ctx.send(mensagem)

@bot.command()
async def anuncio(ctx):
    embed = discord.Embed(
        title="🟪 PAINEL:",
        description="🌐 [Clique aqui para acessar o site](https://heavencity.com/)",
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

# ============================
# ✅ INICIAR BOT
# ============================
# Token seguro vindo das variáveis da Railway
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)











