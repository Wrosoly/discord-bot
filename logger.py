import discord
from discord.ext import commands
from datetime import datetime, timezone, timedelta

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)
token = 'TOKEN'

reaction_log_channel_id = 1238939047217332224
voice_log_channel_id = 1238939047217332224
invite_log_channel_id = 1238939047217332224
channel_log_channel_id = 1238939047217332224

@bot.event
async def on_ready():
    print(f"A {bot.user.name} bot online!")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel:
        if before.channel:
            await log_voice_event(member, before.channel, "left")
        if after.channel:
            await log_voice_event(member, after.channel, "joined")

async def log_voice_event(member, channel, action):
    log_channel = bot.get_channel(voice_log_channel_id)

    if log_channel is None:
        print(f"Error: Az alábbi voice log channel {voice_log_channel_id} nem létezik.")
        return

    embed_color = discord.Color.red() if action == "left" else discord.Color.green()
    embed = discord.Embed(color=embed_color)

    if action == "left":
        embed.title = f"{member.display_name} kilépett {channel.name}"
    elif action == "joined":
        embed.title = f"{member.display_name} belépett {channel.name}"

    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    else:
        embed.set_thumbnail(url=member.default_avatar.url)

    embed.add_field(name="Nickname", value=member.display_name, inline=False)
    embed.add_field(name="Username", value=member.mention, inline=False)
    embed.add_field(name="UserID", value=member.id, inline=False)

    cet = timezone(timedelta(hours=2))
    now_cet = datetime.now(cet)
    embed.add_field(name="Időpont", value=now_cet.strftime('%Y-%m-%d %H:%M:%S'), inline=False)

    await log_channel.send(embed=embed)

@bot.event
async def on_invite_create(invite):
    log_channel = bot.get_channel(invite_log_channel_id)

    if log_channel is None:
        print(f"Error: Az alábbi invite log channel {invite_log_channel_id} nem létezik.")
        return

    embed = discord.Embed(color=discord.Color.blue())
    embed.title = f"{invite.inviter.display_name} meghívót hozott létre"

    if invite.inviter.avatar:
        embed.set_thumbnail(url=invite.inviter.avatar.url)
    else:
        embed.set_thumbnail(url=invite.inviter.default_avatar.url)

    embed.add_field(name="Nickname", value=invite.inviter.display_name, inline=False)
    embed.add_field(name="Username", value=invite.inviter.mention, inline=False)
    embed.add_field(name="UserID", value=invite.inviter.id, inline=False)
    embed.add_field(name="Meghívó", value=invite.url, inline=False)

    cet = timezone(timedelta(hours=2))
    now_cet = datetime.now(cet)
    embed.add_field(name="Időpont", value=now_cet.strftime('%Y-%m-%d %H:%M:%S'), inline=False)

    await log_channel.send(embed=embed)

@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = await bot.fetch_user(payload.user_id)
    await log_reaction_event(message, payload.emoji, user, "hozzáadva")

@bot.event
async def on_raw_reaction_remove(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = await bot.fetch_user(payload.user_id)
    await log_reaction_event(message, payload.emoji, user, "eltávolítva")

async def log_reaction_event(message, emoji, user, action):
    log_channel = bot.get_channel(reaction_log_channel_id)

    if log_channel is None:
        print(f"Error: Az alábbi reakció log channel {reaction_log_channel_id} nem létezik.")
        return

    if action == "eltávolítva":
        embed_color = discord.Color.red()
    elif action == "hozzáadva":
        embed_color = discord.Color.green()
    else:
        embed_color = discord.Color.gold()

    embed = discord.Embed(color=embed_color)
    embed.title = f"Reakció {action}"

    if user:
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="Nickname", value=user.display_name, inline=False)
        embed.add_field(name="Username", value=user.mention, inline=False)
        embed.add_field(name="UserID", value=user.id, inline=False)
    else:
        embed.add_field(name="User", value="Unknown", inline=False)

    embed.add_field(name="Reakció", value=str(emoji), inline=False)
    embed.add_field(name="Üzenet", value=f"[Ugrás az üzenethez]({message.jump_url})", inline=False)

    cet = timezone(timedelta(hours=2))
    now_cet = datetime.now(cet)
    embed.add_field(name="Időpont", value=now_cet.strftime('%Y-%m-%d %H:%M:%S'), inline=False)

    await log_channel.send(embed=embed)

async def log_channel_event(admin, action, channel, embed_color, details):
    log_channel = bot.get_channel(channel_log_channel_id)

    if log_channel is None:
        print(f"Error: Az alábbi channel log channel {channel_log_channel_id} nem létezik.")
        return

    embed = discord.Embed(color=embed_color)
    embed.title = f"Csatorna {action}"

    if admin.avatar:
        embed.set_thumbnail(url=admin.avatar.url)
    else:
        embed.set_thumbnail(url=admin.default_avatar.url)

    embed.add_field(name="Nickname", value=admin.display_name, inline=False)
    embed.add_field(name="Username", value=admin.mention, inline=False)
    embed.add_field(name="UserID", value=admin.id, inline=False)
    embed.add_field(name="Részletek", value=details, inline=False)

    cet = timezone(timedelta(hours=2))
    now_cet = datetime.now(cet)
    embed.add_field(name="Időpont", value=now_cet.strftime('%Y-%m-%d %H:%M:%S'), inline=False)

    await log_channel.send(embed=embed)

async def fetch_admin(channel, action):
    async for entry in channel.guild.audit_logs(limit=1, action=action):
        return entry.user
    return None

@bot.event
async def on_guild_channel_delete(channel):
    admin = await fetch_admin(channel, discord.AuditLogAction.channel_delete)
    details = f"Csatorna neve: {channel.name}\nCsatorna ID: {channel.id}"
    await log_channel_event(admin, "törölve", channel, discord.Color.red(), details)

@bot.event
async def on_guild_channel_create(channel):
    admin = await fetch_admin(channel, discord.AuditLogAction.channel_create)
    details = f"Csatorna neve: {channel.name}\nCsatorna ID: {channel.id}"
    await log_channel_event(admin, "létrehozva", channel, discord.Color.green(), details)

@bot.event
async def on_guild_channel_update(before, after):
    admin = await fetch_admin(after, discord.AuditLogAction.channel_update)
    changes = []
    if before.name != after.name:
        changes.append(f"Név: {before.name} -> {after.name}")
    if before.topic != after.topic:
        changes.append(f"Téma: {before.topic} -> {after.topic}")
    if before.category != after.category:
        changes.append(f"Kategória: {before.category} -> {after.category}")
    details = f"Csatorna ID: {after.id}\n" + ("\n".join(changes) if changes else "Nincs változás")
    await log_channel_event(admin, "módosítva", after, discord.Color.blue(), details)

@bot.event
async def on_guild_channel_pins_update(channel, last_pin):
    admin = await fetch_admin(channel, discord.AuditLogAction.channel_update)
    details = f"Csatorna neve: {channel.name}\nCsatorna ID: {channel.id}\nUtolsó pinek frissítve: {last_pin.strftime('%Y-%m-%d %H:%M:%S') if last_pin else 'Nincs pin'}"
    await log_channel_event(admin, "pinek frissítve", channel, discord.Color.gold(), details)

bot.run(token)