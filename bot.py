import discord
from discord.ext import commands
from datetime import datetime

# =========================
# CONFIG
# =========================
TOKEN = "SEU_TOKEN_AQUI"
CANAL_LOGS_ID = 1418436632129962054  # ID do canal de logs

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# HIERARQUIA
# =========================
@bot.command()
async def hierarquia(ctx):

    cargos_lista = [
        "Delegado Geral",
        "Delegado Adjunto",
        "Comando CGPC",
        "Coordenador CGPC",
        "Comandos",
        "Investigador Ilegal"
    ]

    # Cargos que não aparecem nos investigadores
    cargos_comando = [
        "Delegado Geral",
        "Delegado Adjunto",
        "Comando CGPC",
        "Coordenador CGPC",
        "Comandos"
    ]

    mensagem = "📊 **DEPARTAMENTO DE INVESTIGAÇÃO**\n\n"
    total_membros = 0

    for nome_cargo in cargos_lista:

        cargo = discord.utils.get(ctx.guild.roles, name=nome_cargo)

        if cargo is None:
            mensagem += f"**{nome_cargo}**\nCargo não encontrado.\n\n"
            continue

        membros = cargo.members

        # Filtrar investigadores que têm cargos de comandos
        if nome_cargo == "Investigador Ilegal":

            filtrados = []

            for m in membros:

                tem_comandos = any(
                    discord.utils.get(m.roles, name=c)
                    for c in cargos_comando
                )

                if not tem_comandos:
                    filtrados.append(m)

            membros = filtrados

        mensagem += f"{cargo.mention} ({len(membros)})\n"

        if len(membros) == 0:
            mensagem += "Nenhum membro.\n\n"
        else:
            for m in membros:
                mensagem += f"{m.mention}\n"

            mensagem += "\n"
            total_membros += len(membros)

    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    mensagem += f"**Total de membros:** {total_membros}\n"
    mensagem += f"Atualizado em: {agora}"

    await ctx.send(mensagem)

# =========================
# BOTÕES LOGS
# =========================
class LogsView(discord.ui.View):

    def __init__(self, membro, nome, cid):
        super().__init__(timeout=None)
        self.membro = membro
        self.nome = nome
        self.cid = cid

    @discord.ui.button(label="Aprovar", style=discord.ButtonStyle.green, emoji="✅")
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        novo_nome = f"[INV] {self.nome} | {self.cid}"

        cargo = discord.utils.get(guild.roles, name="Investigador Ilegal")

        try:
            await self.membro.edit(nick=novo_nome)

            if cargo:
                await self.membro.add_roles(cargo)

            await interaction.response.send_message(
                f"✅ {self.membro.mention} aprovado.",
                ephemeral=True
            )

        except:
            await interaction.response.send_message(
                "❌ Erro ao alterar nick/cargo. Verifique permissões.",
                ephemeral=True
            )

    @discord.ui.button(label="Reprovar", style=discord.ButtonStyle.red, emoji="❌")
    async def reprovar(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            f"❌ {self.membro.mention} reprovado.",
            ephemeral=True
        )

# =========================
# MODAL
# =========================
class RegistroModal(discord.ui.Modal, title="Registro de Investigador"):

    nome = discord.ui.TextInput(
        label="QRA"
    )

    id_cidade = discord.ui.TextInput(
        label="ID na cidade"
    )

    async def on_submit(self, interaction: discord.Interaction):

        canal = bot.get_channel(CANAL_LOGS_ID)

        if canal is None:
            await interaction.response.send_message(
                "❌ Canal de logs não encontrado.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="📋 Solicitação de Registro",
            color=discord.Color.yellow(),
            timestamp=datetime.now()
        )

        embed.add_field(
            name="Usuário",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="Nome",
            value=self.nome.value,
            inline=True
        )

        embed.add_field(
            name="CID",
            value=self.id_cidade.value,
            inline=True
        )

        view = LogsView(
            interaction.user,
            self.nome.value,
            self.id_cidade.value
        )

        await canal.send(embed=embed, view=view)

        await interaction.response.send_message(
            "✅ Registro enviado para análise.",
            ephemeral=True
        )

# =========================
# PAINEL BOTÃO
# =========================
class PainelView(discord.ui.View):

    @discord.ui.button(label="Registrar", style=discord.ButtonStyle.green, emoji="✅")
    async def registrar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RegistroModal())

# =========================
# COMANDOs PAINEL
# =========================
@bot.command()
async def painel(ctx):

    embed = discord.Embed(
        title="Painel de Registro",
        description="Clique no botão abaixo para se registrar.",
        color=discord.Color.blue()
    )

    # IMAGEM GRANDE (banner)
    embed.set_image(
        url="https://cdn.discordapp.com/attachments/1413274359677583411/1471122812747120766/regi.png?ex=698dc962&is=698c77e2&hm=5866c9ea80cc625c3beee2c822ddc9708b04f41734be796eb613d1a1e341394c&"
    )

    # Se quiser miniatura no canto, use este também:
    # embed.set_thumbnail(url="https://link_da_sua_imagem.png")

    await ctx.send(embed=embed, view=PainelView())

# =========================
# ONLINE
# =========================
@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")

# =========================
# RUN
# =========================
bot.run("")
