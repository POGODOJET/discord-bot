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

# ✅ IDs configurados por você
CATEGORY_ID = 1387269436259434557
LOG_CHANNEL_ID = 1436234566015914077
STAFF_ROLE_ID = 1387269134609420358

bot = commands.Bot(command_prefix="!", intents=intents)

ticket_count = 0
blacklist = set()

# ========================================================================
# ✅ BOT ONLINE
# ========================================================================
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        await bot.tree.sync()
    except:
        pass


# ========================================================================
# ✅ SELECT MENU PARA ABRIR TICKET
# ========================================================================
class TicketSelect(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label="Suporte Geral", emoji="🔔"),
            discord.SelectOption(label="Denuncia", emoji="☎️"),
            discord.SelectOption(label="Financeiro", emoji="💰"),
            discord.SelectOption(label="Reportar Bug", emoji="🐞"),
            discord.SelectOption(label="Ativação Produto/Plano", emoji="✅"),
        ]

        super().__init__(
            placeholder="Selecione o assunto do ticket:",
            options=options
        )

    async def callback(self, interaction: Interaction):

        # ✅ Verificar blacklist
        if interaction.user.id in blacklist:
            await interaction.response.send_message(
                "🚫 Você está bloqueado de abrir tickets.",
                ephemeral=True
            )
            return

        global ticket_count
        ticket_count += 1

        guild = interaction.guild
        staff_role = guild.get_role(STAFF_ROLE_ID)
        logs = guild.get_channel(LOG_CHANNEL_ID)
        category = guild.get_channel(CATEGORY_ID)

        ticket_name = f"ticket-{ticket_count:03d}"

        # ✅ Permissões do ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        # ✅ Criar canal do ticket
        ticket_channel = await guild.create_text_channel(
            name=ticket_name,
            category=category,
            overwrites=overwrites
        )

        # ✅ Painel administrativo no ticket
        admin_view = AdminTicketView(interaction.user.id)

        # ✅ Mensagem de boas-vindas
        embed = discord.Embed(
            title="📨 Ticket Aberto!",
            description=(
                f"{interaction.user.mention}, obrigado por abrir um ticket.\n"
                f"**Seleção:** `{self.values[0]}`\n\n"
                f"<@&{STAFF_ROLE_ID}> um novo ticket foi aberto!"
            ),
            color=0x2b2d31
        )

        embed.set_image(url="https://media.discordapp.net/attachments/795844164763516969/1436384412928446607/heavenbanner.png?ex=690f68ba&is=690e173a&hm=cbc9faeaceb864c1c4e9105228a785fa441b66571660d047d6638b0afeb37b0a&=&format=webp&quality=lossless")  # ✅ Banner que você pediu

        await ticket_channel.send(embed=embed, view=admin_view)

        # ✅ Log
        await logs.send(
            f"✅ **Ticket criado:** {ticket_channel.mention}\n"
            f"👤 **Usuário:** {interaction.user.mention}\n"
            f"📂 **Categoria:** `{self.values[0]}`"
        )

        # ✅ Resposta oculta ao usuário
        await interaction.response.send_message(
            "✅ Ticket criado com sucesso!",
            ephemeral=True
        )


# ========================================================================
# ✅ VIEW DO SELECT MENU
# ========================================================================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# ========================================================================
# ✅ ADMIN VIEW (APARECE EM TODO TICKET)
# ========================================================================
class AdminTicketView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

        self.add_item(CloseTicketButton())
        self.add_item(AddUserButton())
        self.add_item(RemoveUserButton())


# ========================================================================
# ✅ FECHAR TICKET
# ========================================================================
class CloseTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="🔒 Fechar Ticket",
            style=discord.ButtonStyle.danger
        )

    async def callback(self, interaction: Interaction):
        if STAFF_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(
                "🚫 Apenas staff pode fechar tickets.",
                ephemeral=True
            )
            return

        channel = interaction.channel
        guild = interaction.guild
        logs = guild.get_channel(LOG_CHANNEL_ID)

        await interaction.response.send_message(
            "🔒 Fechando ticket em 5 segundos...",
            ephemeral=True
        )

        await asyncio.sleep(5)

        # ✅ Criar transcrição
        transcript = ""
        async for msg in channel.history(limit=None, oldest_first=True):
            transcript += f"[{msg.created_at}] {msg.author}: {msg.content}\n"

        filename = f"{channel.name}-transcript.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(transcript)

        opener = None
        async for msg in channel.history(limit=5):
            opener = msg.mentions[0] if msg.mentions else None
            break

        # ✅ Enviar transcrição no DM do usuário
        if opener:
            try:
                await opener.send(
                    "✅ Seu ticket foi fechado! Aqui está uma cópia da transcrição:",
                    file=discord.File(filename)
                )

                # ✅ Enviar avaliação
                await opener.send(
                    "**⭐ Avalie o atendimento!**\n"
                    "Responda com um número de **1 a 5**, sendo:\n"
                    "1 ⭐ = Péssimo\n"
                    "5 ⭐ = Excelente"
                )
            except:
                pass

        # ✅ Enviar log no servidor
        await logs.send(
            f"🔒 **Ticket fechado:** {channel.name}\n"
            f"👤 Fechado por: {interaction.user.mention}",
            file=discord.File(filename)
        )

        await channel.delete()


# ========================================================================
# ✅ ADICIONAR USUÁRIO AO TICKET
# ========================================================================
class AddUserButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="➕ Adicionar Usuário", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: Interaction):
        if STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]:
            return await interaction.response.send_message("🚫 Somente staff.", ephemeral=True)

        await interaction.response.send_message("👤 Marque o usuário para adicionar:", ephemeral=True)


# ========================================================================
# ✅ REMOVER USUÁRIO DO TICKET
# ========================================================================
class RemoveUserButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="➖ Remover Usuário", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: Interaction):
        if STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]:
            return await interaction.response.send_message("🚫 Somente staff.", ephemeral=True)

        await interaction.response.send_message("👤 Marque o usuário para remover:", ephemeral=True)


# ========================================================================
# ✅ COMANDO PARA ENVIAR O PAINEL COM BANNER
# ========================================================================
@bot.command()
async def ticketpainel(ctx):

    embed = discord.Embed(
        title="🎫 Sistema de Tickets",
        description="Selecione abaixo o assunto do seu atendimento:",
        color=0x2b2d31
    )

    embed.set_image(url="https://media.discordapp.net/attachments/795844164763516969/1436384412928446607/heavenbanner.png?ex=690f68ba&is=690e173a&hm=cbc9faeaceb864c1c4e9105228a785fa441b66571660d047d6638b0afeb37b0a&=&format=webp&quality=lossless")  # ✅ Banner aqui

    await ctx.send(embed=embed, view=TicketView())


# ========================================================================
# ✅ BLACKLIST (Staff)
# ========================================================================
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def blacklist_add(ctx, member: discord.Member):
    blacklist.add(member.id)
    await ctx.send(f"🚫 {member.mention} não pode mais abrir tickets.")


@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def blacklist_remove(ctx, member: discord.Member):
    blacklist.discard(member.id)
    await ctx.send(f"✅ {member.mention} pode abrir tickets novamente.")

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





