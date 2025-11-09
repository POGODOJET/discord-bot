# tickets.py
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
