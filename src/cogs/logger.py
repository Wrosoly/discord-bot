import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import hybrid_command
import yaml
import datetime

class MessageLogger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        with open("config.yaml", "r") as file: # Loads config from config.yaml
            config = yaml.safe_load(file)
            
        channels = {
            "simple": self.bot.fetch_channel(config["log"]["simple"]),
            "detailed": self.bot.fetch_channel(config["log"]["detailed"])
        }
        
        # Create corresponding embeds
        simpleEmbed = discord.Embed(description=message.content, color=message.author.color, timestamp=message.created_at)
        if len(message.attachments) > 0:
            simpleEmbed.add_field(name="Csatolmányok", value=len(message.attachments))
            simpleEmbed.set_image(url=message.attachments[0].url)
        simpleEmbed.set_footer(text=message.author.top_role.name)
        simpleEmbed.set_author(name=message.author.name, icon_url=message.author.avatar.url)

async def setup(bot: commands.Bot):
    await bot.add_cog(MessageLogger(bot))