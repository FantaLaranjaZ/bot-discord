import discord
from discord.ext import commands
from PIL import Image, ImageSequence
import requests
from io import BytesIO
from discord.ui import Button, View, Modal, TextInput

# Configurações e Inicialização
intents = discord.Intents.default()
intents.members = True  # Permitir acesso à lista de membros
bot = commands.Bot(command_prefix="!", intents=intents)

# IDs do primeiro servidor (arma)
WELCOME_CHANNEL_ID = 1285511478144667699  # Substitua pelo ID do canal de boas-vindas
GOODBYE_CHANNEL_ID = 1285607272604762132  # Substitua pelo ID do canal de despedidas
PEDIR_SET_CHANNEL_ID_1 = 1285521186134163549  # Substitua pelo ID do canal "pedir-set"
MEMBER_ROLE_ID_1 = 1282761075376525364  # Substitua pelo ID do cargo de "Membro"

# IDs do segundo servidor (cohab)
PEDIR_SET_CHANNEL_ID_2 = 1285815612907458570  # ID do canal "pedir-set" no segundo servidor
COHAB_ROLE_ID = 1237907323503120494  # ID do cargo "Cohab" no segundo servidor
NOVATO_ROLE_ID = 1254606365280698378  # ID do cargo "Novato" no segundo servidor

# Função para criar GIF de boas-vindas/despedida com o avatar do usuário (apenas para o primeiro servidor)
async def create_gif_with_avatar(member, gif_path, output_filename):
    background = Image.open(gif_path)
    if member.avatar:
        avatar_url = str(member.avatar.url)
        response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(response.content)).convert("RGBA")
        avatar = avatar.resize((150, 150))

        frames = []
        for frame in ImageSequence.Iterator(background):
            frame = frame.convert("RGBA")
            frame.paste(avatar, (frame.width // 2 - 75, frame.height // 2 - 75), avatar)
            frames.append(frame)

        frames[0].save(output_filename, save_all=True, append_images=frames[1:], loop=0, duration=background.info['duration'])
    else:
        background.save(output_filename)

    return output_filename


# Evento quando alguém entra no servidor (apenas para o primeiro servidor)
@bot.event
async def on_member_join(member):
    if member.guild.id == 1282761075376525364:  # Verifica se é o primeiro servidor
        channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            welcome_gif = await create_gif_with_avatar(member, "Boas vindas/ezgif-5-59fe66bef9.gif", f"welcome_{member.id}.gif")
            with open(welcome_gif, "rb") as f:
                gif_file = discord.File(f)
                await channel.send(f"Bem-vindo ao servidor, {member.mention}!", file=gif_file)


# Evento quando alguém sai do servidor (apenas para o primeiro servidor)
@bot.event
async def on_member_remove(member):
    if member.guild.id == 1282761075376525364:  # Verifica se é o primeiro servidor
        channel = bot.get_channel(GOODBYE_CHANNEL_ID)
        if channel:
            goodbye_gif = await create_gif_with_avatar(member, "C:\\Users\\nikki\\Desktop\\Bot\\Boas vindas\\garota-gamer-discord-mensagem-saiu-do-servidor.gif", f"goodbye_{member.id}.gif")
            with open(goodbye_gif, "rb") as f:
                gif_file = discord.File(f)
                await channel.send(f"{member.name} saiu do servidor.", file=gif_file)


# Classe do Modal para solicitar nome e ID
class AccessModal(Modal):
    def __init__(self, guild_id):
        super().__init__(title="Liberar Acesso")
        self.guild_id = guild_id
        self.name_input = TextInput(label="Nome", placeholder="Digite seu nome", required=True)
        self.id_input = TextInput(label="ID", placeholder="Digite seu ID", required=True)
        self.add_item(self.name_input)
        self.add_item(self.id_input)

    async def on_submit(self, interaction: discord.Interaction):
        member = interaction.user
        nome = self.name_input.value
        id_number = self.id_input.value

        # Ajusta o prefixo do apelido de acordo com o servidor
        if self.guild_id == 1282761075376525364:  # Primeiro servidor
            novo_apelido = f"[M] {nome} | {id_number}"
        elif self.guild_id == 1254866649329303622:  # Segundo servidor
            novo_apelido = f"[N] {nome} | {id_number}"

        try:
            await member.edit(nick=novo_apelido)
            await interaction.response.send_message(f"Seu apelido foi alterado para: {novo_apelido}", ephemeral=True)

            if self.guild_id == 1282761075376525364:  # Primeiro servidor
                role = member.guild.get_role(MEMBER_ROLE_ID_1)
                if role:
                    await member.add_roles(role)
            elif self.guild_id == 1254866649329303622:  # Segundo servidor
                role_cohab = member.guild.get_role(COHAB_ROLE_ID)
                role_novato = member.guild.get_role(NOVATO_ROLE_ID)
                if role_cohab and role_novato:
                    await member.add_roles(role_cohab, role_novato)
        except discord.Forbidden:
            await interaction.response.send_message("Não tenho permissão para alterar seu apelido.", ephemeral=True)


# View com o botão para solicitar set
class AccessButtonView(View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.add_item(Button(label="Liberar Acesso", style=discord.ButtonStyle.green, custom_id=f"liberar_acesso_{guild_id}"))

    @discord.ui.button(label="Liberar Acesso", style=discord.ButtonStyle.green)
    async def liberar_acesso_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(AccessModal(self.guild_id))


# Evento para enviar a mensagem com o botão no canal "pedir-set" nos dois servidores
@bot.event
async def on_ready():
    # Primeiro servidor (arma)
    channel_1 = bot.get_channel(PEDIR_SET_CHANNEL_ID_1)
    if channel_1:
        view_1 = AccessButtonView(1282761075376525364)
        await channel_1.send("Clique no botão abaixo para liberar seu acesso:", view=view_1)

    # Segundo servidor (cohab)
    channel_2 = bot.get_channel(PEDIR_SET_CHANNEL_ID_2)
    if channel_2:
        view_2 = AccessButtonView(1254866649329303622)
        await channel_2.send("Clique no botão abaixo para liberar seu acesso:", view=view_2)

    await bot.tree.sync()
    print("Comandos de barra sincronizados com sucesso!")


# Adicionar comando de barra
@bot.tree.command(name="hello", description="Says hello!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello there!")


# Rodar o bot
bot.run('discord token')
