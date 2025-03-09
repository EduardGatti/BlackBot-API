import discord
from discord.ext import commands
import asyncio
import random
from PIL import Image, ImageDraw, ImageFont
import string
import re
import aiohttp
from discord.ui import View, Button


links_suspeitos = [
    "bit.ly", "shorturl.at", "tinyurl.com", "cutt.ly", "shorte.st",
    "adf.ly", "grabify.link", "iplogger.org", "yip.su", "gyazo.nl",
    "discord.gift", "free-nitro.com", "steam-giveaway.com", "fake-discord.com"
]

link_regex = re.compile(r"https?://(?:www\.)?\S+")


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Lista de palavrões para moderação
palavroes = [
    "merda", "bosta", "porra", "caralho", "cacete", "foda", "puta", "puto", "putaria",
    "desgraça", "arrombado", "viado", "veado", "fdp", "filho da puta", "foda-se",
    "fodase", "cu", "cuzão", "cuzinho", "babaca", "otário", "otaria", "imbecil",
    "idiota", "corno", "corna", "piranha", "vagabunda", "vagabundo", "escroto",
    "mongol", "retardado", "buceta", "xoxota", "pinto", "pau no cu", "pau no seu cu",
    "vai se fuder", "vai tomar no cu", "vsf", "vtmnc", "vtnc", "vtmc","caralh*", "pqp", "porcaria", 
    "macaco", "preto", "senzala", "chipanze", "sua vagabunda"
]



@bot.event
async def on_ready():
    print("Bot inicializado com sucesso!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    conteudo = message.content.lower()

    # 🛑 🚨 DETECTA PALAVRÕES
    if any(palavra in conteudo for palavra in palavroes):
        try:
            await message.delete()
            await message.channel.send(f"🚨 {message.author.mention}, sua mensagem foi removida por conter palavras inadequadas!", delete_after=5)

            # 🔇 Aplicar mute
            mute_role = discord.utils.get(message.guild.roles, name="Mutado")
            if not mute_role:
                mute_role = await message.guild.create_role(name="Mutado")
                for channel in message.guild.channels:
                    await channel.set_permissions(mute_role, send_messages=False, speak=False)

            await message.author.add_roles(mute_role)
            await message.channel.send(f"🔇 {message.author.mention} foi **mutado por 5 minutos** por usar linguagem inadequada!")

            await asyncio.sleep(300)  # Espera 5 minutos (300 segundos)

            await message.author.remove_roles(mute_role)
            await message.channel.send(f"✅ {message.author.mention} foi **desmutado automaticamente**!")

        except discord.Forbidden:
            print("❌ O bot não tem permissão para mutar ou excluir mensagens.")
        except discord.HTTPException:
            print("❌ Erro ao tentar excluir a mensagem ou aplicar o mute.")

    # 🔗 🚨 DETECTA LINKS SUSPEITOS
    if link_regex.search(conteudo):
        for link in links_suspeitos:
            if link in conteudo:
                if message.author.guild_permissions.manage_messages:
                    return  # Se o usuário for um moderador, ignora
                
                try:
                    await message.delete()
                    await message.guild.ban(message.author, reason="Enviou link suspeito!")
                    await message.channel.send(f"🚨 {message.author.mention} foi **banido** por enviar um link suspeito!")
                
                except discord.Forbidden:
                    print("❌ O bot não tem permissão para banir usuários.")
                except discord.HTTPException:
                    print("❌ Erro ao tentar excluir a mensagem ou banir o usuário.")
                
                return  # Sai da função para evitar mensagens duplicadas

    await bot.process_commands(message)
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Membro Não especificado"):
    try:
        await member.ban(reason=reason)
        await ctx.reply(f"🔨 {member.mention} foi banido! Motivo: {reason}")
    except discord.Forbidden:
        await ctx.reply("❌ Não tenho permissão para banir esse usuário.")
    except discord.HTTPException:
        await ctx.reply("❌ Ocorreu um erro ao tentar banir o usuário.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Sem motivo"):
    if member == ctx.author:
        await ctx.send("❌ Você não pode se expulsar!")
        return

    if ctx.guild.owner == member:
        await ctx.send("❌ Não posso expulsar o dono do servidor!")
        return

    await member.kick(reason=reason)
    await ctx.send(f"✅ {member.mention} foi expulso! Motivo: {reason}")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para expulsar membros!")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Você não tem permissão para banir membros!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("❌ Use o comando corretamente: `!ban @usuário [motivo]`")

ALERTA_CANAL_ID = 1348389019372748820  # ID do canal de alertas

async def enviar_alerta(guild, usuario, tipo, motivo, responsavel=None):
    canal_alerta = guild.get_channel(ALERTA_CANAL_ID)
    if not canal_alerta:
        print("❌ Canal de alertas não encontrado!")
        return

    embed = discord.Embed(
        title="🚨 PUNIÇÃO APLICADA 🚨",
        description=f"**Usuário:** {usuario.mention} (`{usuario.id}`)\n"
                    f"**Punição:** `{tipo}`\n"
                    f"**Motivo:** `{motivo}`",
        color=discord.Color.red()
    )

    if responsavel:
        embed.add_field(name="👮 Responsável:", value=responsavel.mention, inline=False)

    embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else usuario.default_avatar.url)
    await canal_alerta.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, tempo: int, *, reason="Não especificado"):
    """Muta um usuário por um tempo determinado."""
    
    mute_role = discord.utils.get(ctx.guild.roles, name="Mutado")
    if not mute_role:
        try:
            mute_role = await ctx.guild.create_role(name="Mutado", reason="Cargo para usuários mutados")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
        except discord.Forbidden:
            return await ctx.send("❌ **Erro:** Não tenho permissão para criar o cargo 'Mutado'.")
    
    if mute_role in member.roles:
        return await ctx.send(f"⚠️ **Erro:** {member.mention} já está mutado!")

    try:
        await member.add_roles(mute_role)
        await ctx.send(f"🔇 {member.mention} foi **mutado** por {tempo} minutos! Motivo: {reason}")
        await enviar_alerta(ctx.guild, member, "Mute", reason, ctx.author)

        await asyncio.sleep(tempo * 60)

        await member.remove_roles(mute_role)
        await ctx.send(f"✅ {member.mention} foi **desmutado** automaticamente.")
        await enviar_alerta(ctx.guild, member, "Desmute", "Tempo de mute expirado.")

    except discord.Forbidden:
        await ctx.send("❌ **Erro:** Não tenho permissão para mutar esse usuário.")
    except discord.HTTPException:
        await ctx.send("❌ **Erro:** Ocorreu um problema ao tentar mutar o usuário.")

@mute.error
async def mute_error(ctx, error):
    """Trata erros do comando !mute."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ **Uso correto:** `!mute @usuário <tempo (min)> <motivo>`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ **Erro:** Você não tem permissão para mutar membros!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ **Erro:** Usuário ou tempo inválido. Certifique-se de mencionar corretamente!")

# 🔥 Comando de Aviso (Warn) Atualizado com Tratamento de Erro
@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="Não especificado"):
    """Avisa um usuário sobre comportamento inadequado."""
    
    try:
        await ctx.send(f"⚠️ {member.mention}, você recebeu um aviso! Motivo: {reason}")
        await enviar_alerta(ctx.guild, member, "Aviso", reason, ctx.author)
    except discord.Forbidden:
        await ctx.send("❌ **Erro:** Não tenho permissão para avisar esse usuário.")
    except discord.HTTPException:
        await ctx.send("❌ **Erro:** Ocorreu um erro ao enviar o aviso.")

@warn.error
async def warn_error(ctx, error):
    """Trata erros do comando !warn."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ **Uso correto:** `!warn @usuário <motivo>`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ **Erro:** Você não tem permissão para avisar membros!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ **Erro:** Usuário inválido. Mencione corretamente!")


# 🚨 SISTEMA DE CAPTCHA 🚨
@bot.event
async def on_member_join(member):
    captcha_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Criar imagem do CAPTCHA
    img = Image.new('RGB', (200, 80), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((50, 30), captcha_code, fill=(0, 0, 0), font=font)
    
    # Salvar imagem temporária
    captcha_path = f"captcha_{member.id}.png"
    img.save(captcha_path)

    try:
        await member.send(f"🔍 Olá {member.name}, para acessar o servidor, digite o código abaixo no canal de verificação.")
        await member.send(file=discord.File(captcha_path))

        def check(msg):
            return msg.author == member and msg.content == captcha_code

        channel = discord.utils.get(member.guild.text_channels, name="verifycaptcha")

        if not channel:
            return await member.send("❌ O canal de verificação não foi encontrado no servidor.")

        await channel.send(f"{member.mention}, você tem **5 minutos** para digitar o código do CAPTCHA.")

        try:
            msg = await bot.wait_for("message", check=check, timeout=300)
            await channel.send(f"✅ {member.mention} foi verificado com sucesso!")

            role = discord.utils.get(member.guild.roles, name="verifyAccepted")
            if role:
                await member.add_roles(role)
            else:
                await channel.send("⚠️ O cargo 'Verificado' não foi encontrado!")

        except asyncio.TimeoutError:
            await member.kick(reason="Falha na verificação do CAPTCHA")
            await channel.send(f"⏳ {member.mention} não passou na verificação e foi expulso.")

    except discord.Forbidden:
        print(f"Não foi possível enviar mensagem para {member.name}.")
        
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome")

    if not channel:
        print("❌ Canal 'welcome' não encontrado! Crie o canal para exibir a mensagem de boas-vindas.")
        return

    data_entrada = member.joined_at.strftime("%d/%m/%Y %H:%M:%S") if member.joined_at else "Desconhecido"
    data_criacao = member.created_at.strftime("%d/%m/%Y %H:%M:%S")

    mensagem = (
        f"🎉 **Bem-vindo ao servidor, {member.mention}!** 🎉\n\n"
        f"📅 **Você entrou no servidor em:** {data_entrada}\n"
        f"🆕 **Sua conta foi criada em:** {data_criacao}\n\n"
        f"Esperamos que se divirta aqui! 🚀"
    )

    await channel.send(mensagem)
    
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False 

    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send(f"🔒 {ctx.channel.mention} foi bloqueado! Apenas administradores podem falar.")
    


@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True  

    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send(f"🔓 {ctx.channel.mention} foi desbloqueado! Todos podem falar novamente.")

@lock.error
@unlock.error
async def lock_unlock_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para gerenciar canais!")
        
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user.mention} foi **desbanido** com sucesso!")
    except discord.NotFound:
        await ctx.send("❌ Usuário não encontrado na lista de banidos!")
    except discord.Forbidden:
        await ctx.send("❌ Não tenho permissão para desbanir esse usuário!")
    except discord.HTTPException:
        await ctx.send("❌ Ocorreu um erro ao tentar desbanir o usuário.")

@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para desbanir membros!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Use o comando corretamente: `!unban <ID do usuário>`")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount <= 0:
        await ctx.send("❌ O número de mensagens deve ser maior que 0!")
        return
    
    deleted = await ctx.channel.purge(limit=amount + 1) 
    await ctx.send(f"✅ {len(deleted) - 1} mensagens foram apagadas!", delete_after=5)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para apagar mensagens!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Use o comando corretamente: `!clear <quantidade>`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Digite um número válido de mensagens para apagar!")


@bot.command()
@commands.has_permissions(manage_emojis=True)  
async def addemoji(ctx, nome: str, url: str):
    guild = ctx.guild

    if not url.endswith((".png", ".jpg", ".jpeg", ".webp")):
        await ctx.send("❌ O link deve ser uma imagem válida (`.png`, `.jpg`, `.jpeg`, `.webp`).")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await ctx.send("❌ Não foi possível baixar a imagem. Verifique o link.")
                return
            img_data = await response.read()

    emoji = await guild.create_custom_emoji(name=nome, image=img_data)

    await ctx.send(f"✅ Emoji `{emoji}` (`:{emoji.name}:`) adicionado com sucesso!")

@addemoji.error
async def addemoji_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para adicionar emojis!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Use o comando corretamente: `!addemoji <nome> <link_da_imagem>`")
        
CATEGORIA_TICKETS = 1348358421006778428 
CARGO_FUNDADOR = "funder"  
CARGO_SUB_FUNDADOR = "sub funder"  
CARGO_SUPORTE = "suport"  
CARGO_ADMIN = "admin"  
CARGO_ASSISTENTE = "assistant"
CANAL_LOGS = "logs-ticket"  

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Abrir Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user

        for channel in guild.text_channels:
            if channel.name == f"ticket-{member.name.lower().replace(' ', '-')}":
                await interaction.response.send_message("❌ Você já tem um ticket aberto!", ephemeral=True)
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False), 
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            discord.utils.get(guild.roles, name=CARGO_SUPORTE): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            discord.utils.get(guild.roles, name=CARGO_ADMIN): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            discord.utils.get(guild.roles, name=CARGO_FUNDADOR): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            discord.utils.get(guild.roles, name=CARGO_SUB_FUNDADOR): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            discord.utils.get(guild.roles, name=CARGO_ASSISTENTE): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        categoria = discord.utils.get(guild.categories, id=CATEGORIA_TICKETS)
        if not categoria:
            await interaction.response.send_message("❌ Categoria de tickets não encontrada! Verifique a configuração.", ephemeral=True)
            return

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{member.name.lower().replace(' ', '-')}",
            category=categoria,
            overwrites=overwrites
        )

        admin_role = discord.utils.get(guild.roles, name=CARGO_ADMIN)
        funder_role = discord.utils.get(guild.roles, name=CARGO_FUNDADOR)
        sub_funder_role = discord.utils.get(guild.roles, name=CARGO_SUB_FUNDADOR)
        suporte_role = discord.utils.get(guild.roles, name=CARGO_SUPORTE)
        assistant_role = discord.utils.get(guild.roles, name=CARGO_ASSISTENTE)
        admin_mention = admin_role.mention if admin_role else ""
        funder_mention = funder_role.mention if funder_role else ""
        sub_funder_mention = sub_funder_role.mention if sub_funder_role else ""
        suporte_mention = suporte_role.mention if suporte_role else ""
        assistant_mention = assistant_role.mention if assistant_role else ""

        await interaction.response.send_message(f"✅ Ticket criado! Acesse: {ticket_channel.mention}", ephemeral=True)

        await ticket_channel.send(
            f"🎟 **Ticket aberto por {member.mention}**\n"
            f"{admin_mention}{suporte_mention} {assistant_mention}, por favor, atendam a este ticket.\n\n"
            "Para fechar o ticket, um **Administrador, Fundador, Sub Fundador, Suporte ou Assistente** deve clicar no botão abaixo.",
            view=CloseTicketView()
        )

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user

        admin_role = discord.utils.get(guild.roles, name=CARGO_ADMIN)
        funder_role = discord.utils.get(guild.roles, name=CARGO_FUNDADOR)
        sub_funder_role = discord.utils.get(guild.roles, name=CARGO_SUB_FUNDADOR)
        suporte_role = discord.utils.get(guild.roles, name=CARGO_SUPORTE)
        assistant_role = discord.utils.get(guild.roles, name=CARGO_ASSISTENTE)

        if not any(role in member.roles for role in [admin_role, funder_role, sub_funder_role, suporte_role, assistant_role]):
            await interaction.response.send_message("❌ Apenas **Administradores, Fundadores, Sub Fundadores, Suporte ou Assistentes** podem fechar tickets!", ephemeral=True)
            return

        log_channel = discord.utils.get(guild.text_channels, name=CANAL_LOGS)
        if log_channel:
            await log_channel.send(f"📌 **Ticket fechado**\n🔒 {interaction.channel.name} foi fechado por {member.mention}.")

        await interaction.response.send_message("✅ Fechando o ticket...", ephemeral=True)
        await interaction.channel.delete()

@bot.command(name="painel_ticket")
@commands.has_permissions(administrator=True)
async def painel_ticket(ctx):
    embed = discord.Embed(
        title="📩 Sistema de Tickets",
        description="Clique no botão abaixo para abrir um ticket e falar com a equipe de suporte.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TicketView())

@bot.event
async def on_ready():
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    print(f"✅ {bot.user} está online!")
    
AUDITORIA_CANAL = "registro-de-auditoria"

async def log_auditoria(guild, mensagem):
    canal = discord.utils.get(guild.text_channels, name=AUDITORIA_CANAL)
    if canal:
        await canal.send(mensagem)

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    await log_auditoria(message.guild, f"🗑️ **Mensagem apagada**\n📌 **Usuário:** {message.author.mention}\n📝 **Conteúdo:** `{message.content}`\n📍 **Canal:** {message.channel.mention}")

@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    await log_auditoria(before.guild, f"✏️ **Mensagem editada**\n📌 **Usuário:** {before.author.mention}\n📍 **Canal:** {before.channel.mention}\n🔹 **Antes:** `{before.content}`\n🔸 **Depois:** `{after.content}`")

@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        role_diff = set(after.roles) - set(before.roles)
        role_removed = set(before.roles) - set(after.roles)
        if role_diff:
            await log_auditoria(after.guild, f"🎭 **Cargo adicionado**\n📌 **Usuário:** {after.mention}\n🔹 **Cargo:** `{', '.join([r.name for r in role_diff])}`")
        if role_removed:
            await log_auditoria(after.guild, f"🚫 **Cargo removido**\n📌 **Usuário:** {after.mention}\n🔹 **Cargo:** `{', '.join([r.name for r in role_removed])}`")

@bot.event
async def on_member_ban(guild, user):
    await log_auditoria(guild, f"🔨 **Usuário banido**\n📌 **Usuário:** {user.mention}")

@bot.event
async def on_member_unban(guild, user):
    await log_auditoria(guild, f"✅ **Usuário desbanido**\n📌 **Usuário:** {user.mention}")

@bot.event
async def on_member_remove(member):
    await log_auditoria(member.guild, f"🚪 **Usuário saiu ou foi expulso**\n📌 **Usuário:** {member.mention}")

@bot.event
async def on_guild_channel_create(channel):
    await log_auditoria(channel.guild, f"📢 **Canal criado**\n📌 **Nome:** {channel.mention}")

@bot.event
async def on_guild_channel_delete(channel):
    await log_auditoria(channel.guild, f"🚨 **Canal excluído**\n📌 **Nome:** `{channel.name}`")

@bot.event
async def on_guild_channel_update(before, after):
    if before.name != after.name:
        await log_auditoria(after.guild, f"🔄 **Canal renomeado**\n📌 **Antes:** `{before.name}`\n📌 **Depois:** `{after.name}`")

@bot.event
async def on_guild_role_create(role):
    await log_auditoria(role.guild, f"🆕 **Cargo criado**\n📌 **Nome:** `{role.name}`")

@bot.event
async def on_guild_role_delete(role):
    await log_auditoria(role.guild, f"❌ **Cargo excluído**\n📌 **Nome:** `{role.name}`")

@bot.event
async def on_guild_role_update(before, after):
    if before.name != after.name:
        await log_auditoria(after.guild, f"📝 **Cargo renomeado**\n📌 **Antes:** `{before.name}`\n📌 **Depois:** `{after.name}`")

@bot.command()
async def regras(ctx):
    embed = discord.Embed(
        title="📜 Regras da Comunidade - Black Bot",
        description="Seja bem-vindo ao nosso servidor! Para garantir um ambiente seguro e agradável para todos, siga as regras abaixo:",
        color=discord.Color.blue()
    )

    embed.add_field(name="🚨 1. Respeito acima de tudo", value="🔹 Trate todos com respeito, sem ofensas, assédios ou bullying.\n🔹 Discurso de ódio será punido severamente.", inline=False)

    embed.add_field(name="🔒 2. Proibição de conteúdo impróprio", value="🔹 Proibido NSFW, discurso de ódio e conteúdos que violem direitos autorais.", inline=False)

    embed.add_field(name="⚠️ 3. Sem spam ou flood", value="🔹 Sem mensagens repetitivas, CAPS LOCK excessivo ou menções desnecessárias.", inline=False)

    embed.add_field(name="🛡 4. Segurança e Privacidade", value="🔹 Não compartilhe informações pessoais.\n🔹 Evite cair em golpes! Não clique em links suspeitos.", inline=False)

    embed.add_field(name="🔗 5. Links suspeitos e scams", value="🔹 Links encurtados ou suspeitos = **Ban automático**.", inline=False)

    embed.add_field(name="🎮 6. Comportamento nos canais de voz", value="🔹 Sem gritaria, sons irritantes ou perturbação nos canais de voz.", inline=False)

    embed.add_field(name="📌 7. Sistema de Moderação", value="🔹 Black Bot aplica punições automáticas:\n✅ Linguagem ofensiva → **Mute (3 min)**\n✅ Links suspeitos → **Ban**\n✅ Spam → **Aviso**", inline=False)

    embed.add_field(name="🎟 8. Sistema de Tickets", value="🔹 Para suporte, abra um ticket no canal **#suporte**.", inline=False)

    embed.add_field(name="📜 9. Uso correto dos canais", value="🔹 **#bate-papo** para conversas gerais.\n🔹 **#memes** para memes.\n🔹 **#logs** para acompanhar ações da moderação.", inline=False)

    embed.add_field(name="❌ 10. Penalidades", value="⚠️ Descumprir regras resulta em:\n- Avisos ⚠️\n- Mute 🔇\n- Expulsão 🚪\n- Banimento 🔨", inline=False)

    embed.set_footer(text="✅ Ao permanecer no servidor, você concorda com todas as regras.")

    await ctx.send(embed=embed)
    
@bot.command()
@commands.has_permissions(administrator=True)  # Apenas administradores podem usar
async def anuncio(ctx, *, mensagem=None):
    if not mensagem:  # Se a mensagem estiver vazia
        await ctx.send(f"❌ {ctx.author.mention}, você precisa escrever um anúncio!\n\n**Exemplo:** `!anuncio Atualização no servidor! 🎉`")
        return
    
    embed = discord.Embed(
        title="📢 Anúncio Importante!",
        description=mensagem,
        color=discord.Color.gold()
    )

    embed.set_footer(text=f"Anunciado por {ctx.author.name}", icon_url=ctx.author.avatar.url)
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3039/3039362.png")  # Ícone de megafone
    embed.timestamp = discord.utils.utcnow()

    await ctx.send("@everyone", embed=embed)  # Menciona todos do servidor

@anuncio.error
async def anuncio_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"❌ {ctx.author.mention}, você não tem permissão para fazer anúncios!")

@bot.command(name="commands", aliases=["comandos"])
async def commands_list(ctx):
    embed = discord.Embed(
        title="📜 Lista de Comandos",
        description="Aqui estão todos os comandos disponíveis no Black Bot:",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🔨 **Moderação**",
        value=(
            "`!ban @usuário [motivo]` → Bane um usuário.\n"
            "`!kick @usuário [motivo]` → Expulsa um usuário.\n"
            "`!unban <ID>` → Remove o ban de um usuário.\n"
            "`!mute @usuário <tempo>` → Silencia um usuário por X minutos.\n"
            "`!warn @usuário [motivo]` → Dá um aviso a um usuário."
        ),
        inline=False
    )

    embed.add_field(
        name="📢 **Anúncios**",
        value="`!anuncio <mensagem>` → Envia um anúncio para o servidor.",
        inline=False
    )

    embed.add_field(
        name="🎫 **Sistema de Tickets**",
        value="`!painel-ticket` → Cria um painel para abrir tickets de suporte.",
        inline=False
    )

    embed.add_field(
        name="🛑 **Segurança e Logs**",
        value=(
            "`!clear <quantidade>` → Apaga mensagens do chat.\n"
            "O bot também **deleta mensagens impróprias automaticamente** e **protege contra links suspeitos**."
        ),
        inline=False
    )

    embed.add_field(
        name="🔗 **Links Úteis**",
        value=(
            "[Adicione o Bot](https://discord.com/oauth2/authorize?client_id=1348279158521860186)\n"
            "[Servidor de Suporte](https://discord.gg/4b7wzaaHST)"
        ),
        inline=False
    )

    embed.set_footer(text=f"Comando solicitado por {ctx.author.name}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)
    
    
bot.run("SEU_TOKEN")

