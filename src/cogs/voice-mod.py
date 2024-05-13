import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import hybrid_command
import yaml
import datetime
import logging
from faker import Faker


class VoiceMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.state = False
        self.voice_client = None
        self.faker = Faker('hu_HU')  # Magyar lokalizáció beállítása
        self.bot: commands.Bot = bot

    async def getVoiceChannels(self) -> dict:
        with open("config.yaml", "r") as file:  # Loads config from config.yaml
            config = yaml.safe_load(file)

        return {
            "mod1": await self.bot.fetch_channel(config["voice"]["moderated-1"])
        }

    def isStaff(self, member: discord.Member) -> bool:
        #fixme ennek a logikája nem biztos hogy jó, rá kell nézni
        if member.nick.startswith('TM') and member.nick:
            return True
        return False

    def get_random_name(self) -> str:
        random_name = self.faker.first_name()  # Véletlenszerű magyar keresztnév generálása
        return random_name

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        channel_id_data = await self.getVoiceChannels()
        target_channel = channel_id_data['mod1']
        guild = target_channel.guild
        # Ha vki BELÉPETT egy voice channelbe
        if after.channel is not None and after.channel.id == target_channel.id:
            if before.channel is None or before.channel.id != target_channel.id:
                if self.isStaff(member):
                    #ha moderátor csatlakozott fel
                    if (self.state == True):
                        #és az automod fenn van, akkor hess automod
                        await self.voice_client.disconnect()
                        self.state = False
                        return

        # Ha a felhasználó kilépett az adott csatornáról
        if before.channel is not None and before.channel.id == target_channel.id:
            if after.channel is None or after.channel.id != target_channel.id:
                members = target_channel.members
                for member in members:
                    if self.isStaff(member):
                        # ha van még fenn modi, nem kell automod
                        return
                if(self.state == True): return
                bot_member = guild.me
                await bot_member.edit(nick=f"TM {self.get_random_name()} - Moderátor")
                self.voice_client = await target_channel.connect()
                self.state = True
                await self.voice_client.guild.change_voice_state(self_mute=True, channel=target_channel)


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceMod(bot))
