# tickets.py
import discord
from discord.ext import commands
from discord import Interaction
import asyncio
import os
from utils import write_transcript_and_send

# module-level state will be initialized in setup_tickets
_ticket_count = 0
_blacklist = set()

class TicketSelect(discord.ui.Select):
    def __init__(self, category_id, log_channel_id, staff_role_id):
        options = [
            discord.SelectOption(label="Suporte Geral", emoji="🔔"),
            discord.SelectOption(label="Orçamento Script", emoji="🧾"),
            discord.SelectOption(label="Financeiro", emoji="💰"),
            discord.SelectOption(label="Reportar Bug", emoji="🐞"),
            discord.SelectOption(label="Ativação Produto/Plano", emoji="✅"),
        ]
        super().__init__(placeholder="Selecione o assunto do ticket:", options=options)
        self.category_id = category_id
        self.log_channel_id = log_channel_id
        self.staff_role_id = staff_role_id

    async def callback(self, interaction: Interaction):
        global _ticket_count
        guild = interaction.guild

        # blacklist check
        if interaction.user.id in _blacklist:
            return await interaction.response.send_message("🚫 Você está bloqueado de abrir tickets.", ephemeral=True)

        _ticket_count += 1
        ticket_name = f"ticket-{_ticket_count:03d}"

        category = guild.get_channel(self.category_id)
        staff_role = guild.get_role(self.staff_role_id)
        logs = guild.get_channel(self.log_channel_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        ticket_channel = await guild.create_text_channel(name=ticket_name, category=category, overwrites=overwrites)

        # admin view
        admin_view = AdminTicketView(interaction.user.id, self.log_channel_id, self.staff_role_id)

        # ticket embed (banner)
        embed = discord.Embed(title="📨 Ticket Aberto!",
                              description=(f"{interaction.user.mention}, obrigado por abrir um ticket.\n"
                                           f"**Seleção:** `{self.values[0]}`\n\n"
                                           f"<@&{self.staff_role_id}> um novo ticket foi aberto!"), color=0x2b2d31)
        # banner - mantenha sua imagem ou troque
        embed.set_image(url="https://i.imgur.com/LV7Q2Sx.png")

        await ticket_channel.send(embed=embed, view=admin_view)

        # ephemeral message to user with full details
        embed_user = discord.Embed(title="✅ Ticket criado com sucesso!",
                                   description=(f"**Ticket:** `{ticket_name}`\n"
                                                f"**Categoria:** `{self.values[0]}`\n"
                                                f"**Canal:** {ticket_channel.mention}\n\n"
                                                "A equipe foi notificada e irá te atender em breve."),
                                   color=0x2ecc71)

        await interaction.response.send_message(embed=embed_user, ephemeral=True)

        # minimal log to log channel
        if logs:
            await logs.send(f"✅ Novo ticket aberto: {ticket_channel.mention}")

# Admin view and buttons
class CloseTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="🔒 Fechar Ticket", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: Interaction):
        # only staff
        if not any(r.id == interaction.guild.get_role(self.view.staff_role_id).id for r in interaction.user.roles):
            return await interaction.response.send_message("🚫 Apenas staff pode fechar tickets.", ephemeral=True)

        channel = interaction.channel
        logs = interaction.guild.get_channel(self.view.log_channel_id)

        await interaction.response.send_message("🔒 Fechando ticket em 5 segundos...", ephemeral=True)
        await asyncio.sleep(5)

        # create transcript
        transcript = ""
        async for msg in channel.history(limit=None, oldest_first=True):
            transcript += f"[{msg.created_at}] {msg.author}: {msg.content}\n"

        filename = f"{channel.name}-transcript.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(transcript)

        # send transcript to opener via DM (find first non-bot author)
        opener = None
        async for msg in channel.history(limit=200, oldest_first=True):
            if msg.author and not msg.author.bot:
                opener = msg.author
                break

        if opener:
            try:
                await opener.send("✅ Seu ticket foi fechado! Aqui está a transcrição:", file=discord.File(filename))
                # send evaluation prompt
                await opener.send("**⭐ Avalie o atendimento!**\nResponda com um número de 1 a 5 (1=péssimo ... 5=excelente)")
            except Exception:
                pass

        if logs:
            await logs.send(f"🔒 **Ticket fechado:** {channel.name} por {interaction.user.mention}", file=discord.File(filename))

        await channel.delete()

class AddUserButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="➕ Adicionar Usuário", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: Interaction):
        if not any(r.id == interaction.guild.get_role(self.view.staff_role_id).id for r in interaction.user.roles):
            return await interaction.response.send_message("🚫 Somente staff.", ephemeral=True)
        await interaction.response.send_message("👤 Mencione o usuário para adicionar no ticket.", ephemeral=True)

class RemoveUserButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="➖ Remover Usuário", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: Interaction):
        if not any(r.id == interaction.guild.get_role(self.view.staff_role_id).id for r in interaction.user.roles):
            return await interaction.response.send_message("🚫 Somente staff.", ephemeral=True)
        await interaction.response.send_message("👤 Mencione o usuário para remover do ticket.", ephemeral=True)

class AdminTicketView(discord.ui.View):
    def __init__(self, opener_id, log_channel_id, staff_role_id):
        super().__init__(timeout=None)
        self.opener_id = opener_id
        self.log_channel_id = log_channel_id
        self.staff_role_id = staff_role_id
        self.add_item(CloseTicketButton())
        self.add_item(AddUserButton())
        self.add_item(RemoveUserButton())

# Ticket panel command
class TicketView(discord.ui.View):
    def __init__(self, category_id, log_channel_id, staff_role_id):
        super().__init__(timeout=None)
        self.add_item(TicketSelect(category_id, log_channel_id, staff_role_id))

async def send_ticket_panel(ctx, category_id, log_channel_id, staff_role_id):
    embed = discord.Embed(title="🎫 Sistema de Tickets", description="Selecione abaixo o assunto do seu atendimento:", color=0x2b2d31)
    embed.set_image(url="https://i.imgur.com/LV7Q2Sx.png")
    view = TicketView(category_id, log_channel_id, staff_role_id)
    await ctx.send(embed=embed, view=view)

# Setup function
def setup_tickets(bot, category_id, log_channel_id, staff_role_id):
    # attach helper to bot so comandos can use
    bot.ticket_category_id = category_id
    bot.ticket_log_channel_id = log_channel_id
    bot.ticket_staff_role_id = staff_role_id
    bot.add_cog(_TicketCommands(bot))

class _TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ticketpainel")
    async def ticketpainel(self, ctx):
        await send_ticket_panel(ctx, self.bot.ticket_category_id, self.bot.ticket_log_channel_id, self.bot.ticket_staff_role_id)

    @commands.command(name="blacklist_add")
    @commands.has_role(lambda ctx: ctx.guild.get_role(self.bot.ticket_staff_role_id))
    async def _bl_add(self, ctx, member: discord.Member):
        _blacklist.add(member.id)
        await ctx.send(f"🚫 {member.mention} bloqueado de abrir tickets.")

    @commands.command(name="blacklist_remove")
    @commands.has_role(lambda ctx: ctx.guild.get_role(self.bot.ticket_staff_role_id))
    async def _bl_remove(self, ctx, member: discord.Member):
        _blacklist.discard(member.id)
        await ctx.send(f"✅ {member.mention} desbloqueado.")
