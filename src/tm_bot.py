import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
from config import path

class TM(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="tm!", help_command=None, intents=discord.Intents.all())
        load_dotenv()
        
        self.env = {
            "TOKEN": os.getenv("TOKEN")
        }

    async def on_ready(self):   
        logging.info(f"Bot connected as {self.user.name}")
    
    async def load_cogs(self):
        for cog in os.listdir(path["COGS"]):
            if cog.endswith(".py") == False: 
                continue
             
            try:
                cog_name = cog[:-3]

                await self.load_extension(f"cogs.{cog_name}")
                logging.info(f"Loaded {cog} as {cog_name}")
            except Exception as e:
                logging.error(f"Error loading {cog} as {cog_name}: {e}")
    
    async def setup_hook(self): 
        await self.load_cogs()
    
    def start_bot(self):
        print("Starting bot...")


        self.run(self.env["TOKEN"])

class BotApp():
    def __init__(self):
        try:
            bot = TM()
            bot.start_bot()
        except:
            logging.exception("Application crashed")