import discord
from discord.ext import commands

TOKEN = 'INSERT TOKEN HERE!!!!!'
RATE_LIMIT_MESSAGES = 10
RATE_LIMIT_TIME = 20
TIMEOUT_DURATION = 300
YOUR_ROLE_ID = 123456789012345678
YOUR_USER_ID = 1112469181720432753

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
message_counts = {}
last_weh_author = None
bot_frozen = False
admin_role_id = None
TARGET_CHANNEL_ID = None

def save_counter_to_file():
    with open('counter.txt', 'w') as file:
        for channel_id, count in message_counts.items():
            file.write(f'{channel_id}:{count}\n')

def load_counter_from_file():
    try:
        with open('counter.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                channel_id, count = line.strip().split(':')
                message_counts[int(channel_id)] = int(count)
    except FileNotFoundError:
        pass

def save_settings_to_file():
    with open('settings.txt', 'w') as file:
        file.write(f'TARGET_CHANNEL_ID:{TARGET_CHANNEL_ID}\n')
        file.write(f'admin_role_id:{admin_role_id}\n')

def load_settings_from_file():
    try:
        with open('settings.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                key, value = line.strip().split(':')
                if key == 'TARGET_CHANNEL_ID':
                    global TARGET_CHANNEL_ID
                    TARGET_CHANNEL_ID = int(value)
                elif key == 'admin_role_id':
                    global admin_role_id
                    admin_role_id = int(value) if value != 'None' else None
    except FileNotFoundError:
        pass

@bot.event
async def on_ready():
    load_counter_from_file()
    load_settings_from_file()
    print(f'Angemeldet als {bot.user.name}')
    print(f'Zielkanal: {TARGET_CHANNEL_ID}')
    print(f'Admin-Rolle: {admin_role_id}')
    print('Bot gestartet.')

@bot.event
async def on_message(message):
    global last_weh_author
    global bot_frozen

    if message.author.bot:
        return

    if bot_frozen:
        return

    if message.channel.id == TARGET_CHANNEL_ID:
        content = message.content.lower().replace(" ", "")
        if 'weh' in content or 'wäh' in content:
            if message.author == last_weh_author:
                await message.channel.send(f'{message.author.mention}, du hast schon "weh" oder "wäh" gesagt!')
                return
            elif last_weh_author is None:
                last_weh_author = message.author

            if TARGET_CHANNEL_ID not in message_counts:
                message_counts[TARGET_CHANNEL_ID] = 1
            else:
                message_counts[TARGET_CHANNEL_ID] += 1
                last_weh_author = message.author

            await message.add_reaction('✅')
        else:
            last_weh_author = None
            await message.channel.send(f'{message.author.mention}, das war eine falsche Nachricht.')
            await message.add_reaction('❌')

    await bot.process_commands(message)

@bot.command()
async def debug(ctx):
    global bot_frozen
    if ctx.author.id == YOUR_USER_ID:
        bot_frozen = not bot_frozen
        status = "eingefroren" if bot_frozen else "aktiv"
        await ctx.send(f'Bot-Status: {status}')

@bot.command()
async def setadmin(ctx, role: discord.Role):
    global admin_role_id
    if admin_role_id is None:
        admin_role_id = role.id
        save_settings_to_file()
        await ctx.send(f'Admin-Rolle wurde auf {role.mention} festgelegt.')
    else:
        await ctx.send('Die Admin-Rolle wurde bereits festgelegt.')

@bot.command()
async def setchannel(ctx):
    global TARGET_CHANNEL_ID
    TARGET_CHANNEL_ID = ctx.channel.id
    save_settings_to_file()
    await ctx.send(f'Zielkanal wurde auf {ctx.channel.mention} festgelegt.')

@bot.command()
async def load(ctx):
    global message_counts
    load_counter_from_file()
    load_settings_from_file()
    await ctx.send('Zählerstände und Einstellungen wurden aus den Dateien geladen.')

@bot.command()
async def save(ctx):
    global message_counts
    save_counter_to_file()
    save_settings_to_file()
    await ctx.send('Zählerstände und Einstellungen wurden in die Dateien gespeichert.')

@bot.command()
async def showadmin(ctx):
    global admin_role_id
    role = ctx.guild.get_role(admin_role_id)
    if role:
        await ctx.send(f'Die aktuelle Admin-Rolle ist {role.mention}.')
    else:
        await ctx.send('Es wurde keine Admin-Rolle festgelegt.')

@bot.command()
async def freeze(ctx):
    global bot_frozen
    if ctx.author.id == YOUR_USER_ID:
        bot_frozen = not bot_frozen
        status = "eingefroren" if bot_frozen else "aktiv"
        await ctx.send(f'Bot-Status: {status}')

bot.run(TOKEN)

#TOKEN = 'MTE0Mzk5NzE2NjA4MDIyOTU0Ng.GHIAeF.5YjlDLHs-E2mmVlbjOo65GcXXGiCe9NJwzbPlY'
