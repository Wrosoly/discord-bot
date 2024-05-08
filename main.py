import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
from config import path

load_dotenv()
env = {
    "TOKEN": os.getenv("TOKEN")
}

class TM(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="tm!", help_command=None, intents=discord.Intents.all())

    async def on_ready(self):
        """
        Runs when the bot establishes a connection to Discord.
        
        This can run multiple times, although highly unlikely.
        """
        
        logging.info(f"Bot connected as {self.user.name}")
    
    async def load_cogs(self):
        """
        Loads every .py file in cogs/        
        """
        
        for cog in os.listdir(path["cogs"]):
            if cog.endswith(".py") == False: continue
             
            try:
                # i[:-3] = "basic.py" -> "basic"
                cog_name = cog[:-3]

                await self.load_extension(f"cogs.{cog_name}")
                logging.info(f"Loaded {cog} as {cog_name}")
            except Exception as e:
                logging.error(f"Error loading {cog} as {cog_name}: {e}")
    
    async def setup_hook(self):
        """
        Like on_ready, but only runs once, when you start the file.
        on_ready can run multiple times, although unlikely for such a small bot.
        """
        
        await self.load_cogs()

bot = TM()

if __name__ == "__main__":
    try:
        bot.run(env["TOKEN"])
    except:
        logging.info("Disconnected")