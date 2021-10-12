import asyncio
import discord
from discord import activity
from discord import Member, Guild, User
import random

client = discord.Client(intents=discord.Intents.all())

antworten = ['Ja', 'Nein', 'Wahrscheinlich', 'Sieht so aus', 'Sehr wahrscheinlich', 'Sehr unwahrscheinlich']

autoroles = {
    768144203049074729: {'memberroles': [769231398162137108], 'botroles': [827544755289587733]}
}

@client.event
async def on_ready():
    print('Der imperiale Bot ist nun bereit!')
    client.loop.create_task(status_task())
    
async def status_task():
    colors = [discord.Colour.red(), discord.Colour.orange(), discord.Colour.gold(), discord.Colour.green(),
              discord.Colour.blue(), discord.Colour.purple()]
    while True:
        await client.change_presence(activity=discord.Game('Lang lebe das Imperium!'), status=discord.Status.online)
        await asyncio.sleep(5)
        await client.change_presence(activity=discord.Game('Ich helfe den imperialen Bot!'), status=discord.Status.online)
        await asyncio.sleep(5)
        await client.change_presence(activity=discord.Game('https://discord.gg/7PMrd8cdFy'), status=discord.Status.online)
        await asyncio.sleep(5)
        await client.change_presence(activity=discord.Game('?help'), status=discord.Status.online)
        await asyncio.sleep(5)
        await client.change_presence(activity=discord.Game('Der imperiale Bot!'), status=discord.Status.online)
        await asyncio.sleep(5)
        guild: Guild = client.get_guild(768144203049074729)
        if guild:
            role = guild.get_role(769231398162137108)
            if role:
                if role.position < guild.get_member(client.user.id).top_role.position:
                    await role.edit(colour=random.choice(colors))


def is_not_pinned(mess):
    return not mess.pinned

@client.event
async def on_member_join(member):
    guild: Guild = member.guild
    if not member.bot:
        embed = discord.Embed(title='Willkommen auf dem imperialen Server {}'.format(member.name),
                              description='Wir heißen dich herzlich Willkommen auf unserem Server!', color=0x22a7f0)
        try:
            if not member.dm_channel:
                await member.create_dm()
            await member.dm_channel.send(embed=embed)
        except discord.errors.Forbidden:
            print('Es konnte keine Willkommensnachricht an {} gesendet werden.'.format(member.name))
        autoguild = autoroles.get(guild.id)
        if autoguild and autoguild['memberroles']:
            for roleId in autoguild['memberroles']:
                role = guild.get_role(roleId)
                if role:
                    await member.add_roles(role, reason='AutoRoles', atomic=True)
    else:
        autoguild = autoroles.get(guild.id)
        if autoguild and autoguild['botroles']:
            for roleId in autoguild['botroles']:
                role = guild.get_role(roleId)
                if role:
                    await member.add_roles(role, reason='AutoRoles', atomic=True)

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith('?userinfo'):
        args = message.content.split(' ')
        if len(args) == 2:
            member: Member = discord.utils.find(lambda m: args[1] in m.name, message.guild.members)
            if member:
                embed = discord.Embed(title='Userinfo für {}'.format(member.name),
                                      description='Dies ist eine Userinfo für den User {}'.format(member.mention),
                                      color=0x22a7f0)
                embed.add_field(name='Server beigetreten', value=member.joined_at.strftime('%d/%m/%Y, %H:%M:%S'),
                                inline=True)
                embed.add_field(name='Discord beigetreten', value=member.created_at.strftime('%d/%m/%Y, %H:%M:%S'),
                                inline=True)
                rollen = ''
                for role in member.roles:
                    if not role.is_default():
                        rollen += '{} \r\n'.format(role.mention)
                if rollen:
                    embed.add_field(name='Rollen', value=rollen, inline=True)
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_footer(text='Ich bin ein EmbedFooter.')
                mess = await message.channel.send(embed=embed)
                await mess.add_reaction('🚍')

    if message.content.startswith('?clear'):
        if message.author.permissions_in(message.channel).manage_messages:
            args = message.content.split(' ')
            if len(args) == 2:
                if args[1].isdigit():
                    count = int(args[1]) + 1
                    deleted = await message.channel.purge(limit=count, check=is_not_pinned)
                    await message.channel.send('{} Nachrichten gelöscht.'.format(len(deleted)-1))

    if message.content.startswith('?8ball'):
        args = message.content.split(' ')
        if len(args) >= 2:
            frage = ' '.join(args[1:])
            mess = await message.channel.send('Ich versuche deine Frage `{0}` zu beantworten.'.format(frage))
            await asyncio.sleep(2)
            await mess.edit(content='Ich kontaktiere das Orakel...')
            await asyncio.sleep(2)
            await mess.edit(content='Deine Antwort zur Frage `{0}` lautet: `{1}`'.format(frage,
                                                                                         random.choice(antworten)))

    if message.content.startswith('?ban') and message.author.guild_permissions.ban_members:
        args = message.content.split(' ')
        if len(args) == 2:
            member: Member = discord.utils.find(lambda m: args[1] in m.name, message.guild.members)
            if member:
                await member.ban()
                await message.channel.send(f'Member {member.name} gebannt.')
            else:
                await message.channel.send(f'Kein User mit dem Namen {args[1]} gefunden.')
    if message.content.startswith('?unban') and message.author.guild_permissions.ban_members:
        args = message.content.split(' ')
        if len(args) == 2:
            user: User = discord.utils.find(lambda m: args[1] in m.user.name, await message.guild.bans()).user
            if user:
                await message.guild.unban(user)
                await message.channel.send(f'User {user.name} entbannt.')
            else:
                await message.channel.send(f'Kein User mit dem Namen {args[1]} gefunden.')
    if message.content.startswith('?kick') and message.author.guild_permissions.kick_members:
        args = message.content.split(' ')
        if len(args) == 2:
            member: Member = discord.utils.find(lambda m: args[1] in m.name, message.guild.members)
            if member:
                await member.kick()
                await message.channel.send(f'Member {member.name} gekickt.')
            else:
                await message.channel.send(f'Kein User mit dem Namen {args[1]} gefunden.')

client.run('YourBotToken')
