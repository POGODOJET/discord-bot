import discord
import os
from discord.ext import commands
from discord import app_commands, Interaction

# Configurar intents corretamente
intents = discord.Intents.default()
intents.message_content = True  # Permite ler o conteúdo das mensagens
intents.members = True          # Permite ver membros (se precisar)
intents.presences = False       # Pode deixar False se não for usar status

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} conectado com sucesso!")

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
        category_name = self.values[0]
        guild = interaction.guild
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites
        )

        await ticket_channel.send(f"✅ **Ticket aberto! Categoria:** `{category_name}`")
        await interaction.response.send_message("✅ Ticket criado!", ephemeral=True)


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


@bot.command()
async def ticketpainel1(ctx):
    embed = discord.Embed(
        title="📨 Sistema de Tickets",
        description="Selecione abaixo a categoria do seu atendimento:",
        color=0x2b2d31
    )

    await ctx.send(embed=embed, view=TicketView())

class OpenTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="📨 Abrir Ticket", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: Interaction):
        view = TicketView()
        await interaction.response.send_message(
            "Selecione o tipo de ticket:",
            view=view,
            ephemeral=True
        )


class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Suporte Geral", emoji="🔔"),
            discord.SelectOption(label="Financeiro", emoji="💰"),
            discord.SelectOption(label="Reportar Bug", emoji="🐞"),
            discord.SelectOption(label="Ativação Produto/Plano", emoji="✅"),
        ]

        super().__init__(
            placeholder="Escolha o tipo de ticket...",
            options=options
        )

    async def callback(self, interaction: Interaction):
        guild = interaction.guild
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True),
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites
        )

        await ticket_channel.send(
            f"✅ Ticket aberto! Tipo selecionado: **{self.values[0]}**"
        )
        await interaction.response.send_message("✅ Ticket criado!", ephemeral=True)


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


@bot.command()
async def ticketpainel2(ctx):
    await ctx.send(
        "Clique no botão abaixo para abrir um ticket:",
        view=discord.ui.View().add_item(OpenTicketButton())
    )

class TicketButton(discord.ui.Button):
    def __init__(self, label, emoji):
        super().__init__(label=label, emoji=emoji, style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: Interaction):
        guild = interaction.guild

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True),
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites
        )

        await ticket_channel.send(f"✅ Ticket aberto para **{self.label}**!")
        await interaction.response.send_message("✅ Ticket criado!", ephemeral=True)


class TicketButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(TicketButton("Suporte", "🔧"))
        self.add_item(TicketButton("Financeiro", "💰"))
        self.add_item(TicketButton("Bug / Erro", "🐞"))
        self.add_item(TicketButton("Orçamento", "🧾"))


@bot.command()
async def ticketpainel3(ctx):
    embed = discord.Embed(
        title="📨 Abertura de Tickets",
        description="Clique na categoria desejada:",
        color=0x2b2d31
    )

    await ctx.send(embed=embed, view=TicketButtons())

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

# Token seguro vindo das variáveis da Railway
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)









