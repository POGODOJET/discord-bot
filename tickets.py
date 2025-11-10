# tickets.py

import discord
from discord.ext import commands
from discord import Interaction
import asyncio

_blacklist = set()


# ===============================================================
# ✅ BOTÕES: ADD USER / REMOVE USER / CLOSE TICKET
# ===============================================================

class AddUserButton(discord.ui.Button):
    def __init__(self, staff_role_id):
        super().__init__(label="➕ Adicionar Usuário", style=discord.ButtonStyle.primary)
        self.staff_role_id = staff_role_id

    async def callback(self, interaction: Interaction):
        if not any(r.id == self.staff_role_id for r in interaction.user.roles):
            return await interaction.response.send_message("🚫 Somente staff.", ephemeral=True)

        await interaction.response.send_message(
            "👤 Mencione o usuário para adicionar no ticket.",
            ephemeral=True
        )


class RemoveUserButton(discord.ui.Button):
    def __init__(self, staff_role_id):
        super().__init__(label="➖ Remover Usuário", style=discord.ButtonStyle.secondary)
        self.staff_role_id = staff_role_id

    async def callback(self, interaction: Interaction):
        if not any(r.id == self.staff_role_id for r in interaction.user.roles):
            return await interaction.response.send_message("🚫 Somente staff.", ephemeral=True)

        await interaction.response.send_message(
            "👤 Mencione o usuário para remover do ticket.",
            ephemeral=True
        )


class CloseTicketButton(discord.ui.Button):
    def __init__(self, opener_id, log_channel_id, staff_role_id):
        super().__init__(label="🔒 Fechar Ticket", style=discord.ButtonStyle.danger)
        self.opener_id = opener_id
        self.log_channel_id = log_channel_id
        self.staff_role_id = staff_role_id

    async def callback(self, interaction: Interaction):

        if not any(role.id == self.staff_role_id for role in interaction.user.roles):
            return await interaction.response.send_message("🚫 Apenas staff pode fechar tickets.", ephemeral=True)

        await interaction.response.send_message("✅ Fechando ticket em 5 segundos...", ephemeral=True)
        await asyncio.sleep(5)

        channel = interaction.channel
        guild = interaction.guild
        log_channel = guild.get_channel(self.log_channel_id)

        transcript = ""
        async for msg in channel.history(limit=None, oldest_first=True):
            transcript += f"[{msg.created_at}] {msg.author}: {msg.content}\n"

        file_name = f"{channel.name}_transcript.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(transcript)

        opener = guild.get_member(self.opener_id)

        if opener:
            try:
                await opener.send(
                    "✅ Seu ticket foi fechado! Aqui está a transcrição:",
                    file=discord.File(file_name)
                )
            except:
                pass

        if log_channel:
            await log_channel.send(
                f"🔒 Ticket **{channel.name}** foi fechado por {interaction.user.mention}.",
                file=discord.File(file_name)
            )

        await channel.delete()


# ===============================================================
# ✅ SELECT DE CATEGORIAS
# ===============================================================

class TicketSelect(discord.ui.Select):
    def __init__(self, category_id, log_channel_id, staff_role_id):
        self.category_id = category_id
        self.log_channel_id = log_channel_id
        self.staff_role_id = staff_role_id

        options = [
            discord.SelectOption(label="Suporte Geral", emoji="🔔"),
            discord.SelectOption(label="Denúncia", emoji="☎️"),
            discord.SelectOption(label="Financeiro", emoji="💰"),
            discord.SelectOption(label="Reportar Bug", emoji="🐞"),
            discord.SelectOption(label="Ativação Produto/Plano", emoji="✅"),
        ]

        super().__init__(placeholder="Selecione o assunto:", options=options)

    async def callback(self, interaction: Interaction):
        user = interaction.user

        if user.id in _blacklist:
            return await interaction.response.send_message(
                "🚫 Você está bloqueado de abrir tickets.",
                ephemeral=True
            )

        guild = interaction.guild
        category = guild.get_channel(self.category_id)
        staff_role = guild.get_role(self.staff_role_id)
        log_channel = guild.get_channel(self.log_channel_id)

        ticket_name = f"ticket-{user.name}-{interaction.id}".replace(" ", "-")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=ticket_name,
            category=category,
            overwrites=overwrites
        )

        admin_view = AdminTicketView(user.id, self.log_channel_id, self.staff_role_id)

        embed = discord.Embed(
            title="📨 Ticket Aberto!",
            description=(
                f"{user.mention}, seu ticket foi criado.\n"
                f"**Categoria:** `{self.values[0]}`\n\n"
                f"<@&{self.staff_role_id}> foi notificada!"
            ),
            color=0x2b2d31
        )

        embed.set_image(url="https://media.discordapp.net/attachments/795844164763516969/1436384412928446607/heavenbanner.png?ex=69120bba&is=6910ba3a&hm=448016be260e494b64e14d8de2721fd9db6a385b8785af1902e0be85f4f1faa6&=&format=webp&quality=lossless")
        await ticket_channel.send(embed=embed, view=admin_view)

        embed_user = discord.Embed(
            title="✅ Ticket criado com sucesso!",
            description=(
                f"**Ticket:** `{ticket_name}`\n"
                f"**Categoria:** `{self.values[0]}`\n"
                f"**Canal:** {ticket_channel.mention}\n\n"
                "A equipe foi notificada."
            ),
            color=0x2ecc71
        )

        await interaction.response.send_message(
            embed=embed_user,
            ephemeral=True
        )

        if log_channel:
            await log_channel.send(f"✅ Novo ticket aberto: {ticket_channel.mention}")


# ===============================================================
# ✅ VIEWS
# ===============================================================

class TicketView(discord.ui.View):
    def __init__(self, category_id, log_channel_id, staff_role_id):
        super().__init__(timeout=None)
        self.add_item(TicketSelect(category_id, log_channel_id, staff_role_id))


class AdminTicketView(discord.ui.View):
    def __init__(self, opener_id, log_channel_id, staff_role_id):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton(opener_id, log_channel_id, staff_role_id))
        self.add_item(AddUserButton(staff_role_id))
        self.add_item(RemoveUserButton(staff_role_id))


# ===============================================================
# ✅ Enviar painel
# ===============================================================

async def send_ticket_panel(ctx, category_id, log_channel_id, staff_role_id):
    embed = discord.Embed(
        title="🎫 Sistema de Tickets",
        description="Selecione abaixo o motivo do atendimento:",
        color=0x2b2d31
    )
    
    embed.set_image(url="https://media.discordapp.net/attachments/795844164763516969/1436384412928446607/heavenbanner.png?ex=69120bba&is=6910ba3a&hm=448016be260e494b64e14d8de2721fd9db6a385b8785af1902e0be85f4f1faa6&=&format=webp&quality=lossless")

    view = TicketView(category_id, log_channel_id, staff_role_id)
    await ctx.send(embed=embed, view=view)


# ===============================================================
# ✅ Setup (usado no bot.py)
# ===============================================================

async def setup_tickets(bot, category_id, log_channel_id, staff_role_id):
    bot.ticket_category_id = category_id
    bot.ticket_log_channel_id = log_channel_id
    bot.ticket_staff_role_id = staff_role_id
    await bot.add_cog(_TicketCommands(bot))


class _TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ticketpainel")
    async def ticketpainel(self, ctx):
        await send_ticket_panel(
            ctx,
            self.bot.ticket_category_id,
            self.bot.ticket_log_channel_id,
            self.bot.ticket_staff_role_id
        )

    @commands.command(name="blacklist_add")
    async def blacklist_add(self, ctx, member: discord.Member):
        if self.bot.ticket_staff_role_id not in [r.id for r in ctx.author.roles]:
            return await ctx.send("🚫 Apenas staff pode usar este comando.")

        _blacklist.add(member.id)
        await ctx.send(f"🚫 {member.mention} bloqueado.")

    @commands.command(name="blacklist_remove")
    async def blacklist_remove(self, ctx, member: discord.Member):
        if self.bot.ticket_staff_role_id not in [r.id for r in ctx.author.roles]:
            return await ctx.send("🚫 Apenas staff pode usar este comando.")

        _blacklist.discard(member.id)
        await ctx.send(f"✅ {member.mention} desbloqueado.")
