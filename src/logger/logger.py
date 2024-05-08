import discord
import discord.ext

class TMLogger():
    def __init__(self) -> None:
        pass

    async def handleMessage(bot: discord.ext.commands.Bot, message: discord.Message):
        print(message)