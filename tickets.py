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

        # ✅ Transcrição do ticket
        transcript = ""
        async for msg in channel.history(limit=None, oldest_first=True):
            transcript += f"[{msg.created_at}] {msg.author}: {msg.content}\n"

        file_name = f"{channel.name}_transcript.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(transcript)

        opener = guild.get_member(self.opener_id)

        # ✅ Enviar DM ao usuário
        if opener:
            try:
                await opener.send(
                    "✅ Seu ticket foi fechado! Aqui está a transcrição:",
                    file=discord.File(file_name)
                )
            except:
                pass

        # ✅ Log no servidor
        await log_channel.send(
            f"🔒 Ticket **{channel.name}** foi fechado por {interaction.user.mention}.",
            file=discord.File(file_name)
        )

        # ✅ Deletar canal
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

        super()
