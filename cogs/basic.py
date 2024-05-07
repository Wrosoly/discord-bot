import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import hybrid_command

class Basic(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    @hybrid_command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f"Pong! **{round(self.bot.latency * 1000)}ms**")
    
    @commands.command()
    async def sync(self, ctx):
        self.bot.tree.copy_global_to(guild=ctx.guild)
        await ctx.reply("Synced")

async def setup(bot: commands.Bot):
    await bot.add_cog(Basic(bot))