import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
from config import path
from logger.logger import TMLogger



class TM(commands.Bot):
    def __init__(self):
        self.tm_logger = TMLogger()
        super().__init__(command_prefix="tm!", help_command=None, intents=discord.Intents.all())

    async def on_ready(self):   
        logging.info(f"Bot connected as {self.user.name}")
    
    async def load_cogs(self):
        for cog in os.listdir(path["COGS"]):
            if cog.endswith(".py") == False: continue
             
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
        load_dotenv()
        
        env = {
            "TOKEN": os.getenv("TOKEN")
        }

        self.run(env["TOKEN"])

        log = TMLogger()
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.tm_logger.handleMessage(message)

        
        

class BotApp():
    def __init__(self):
        bot = TM()
        bot.start_bot()
        try:
            ...
        except Err:
            print("Applitaction crashed")