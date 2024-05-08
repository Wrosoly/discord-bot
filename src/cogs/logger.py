import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import hybrid_command
import yaml
import datetime

class MessageLogger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        ctx_menu = app_commands.ContextMenu(
            name="Üzenet törlése",
            callback=self.delete_message
        )
        print("added ctx menu")
        self.bot.tree.add_command(ctx_menu)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: # DON'T LOG MESSAGES IF AUTHOR IS A BOT
            return
        with open("config.yaml", "r") as file: # Loads config from config.yaml
            config = yaml.safe_load(file)
            
        channels = {
            "simple": await self.bot.fetch_channel(config["log"]["simple"]),
            "detailed": await self.bot.fetch_channel(config["log"]["detailed"])
        }
        
        # Create corresponding embeds
        simpleEmbed = discord.Embed(
            title="#" + message.channel.name,
            url=message.jump_url, # A direct link to the message
            description=message.content,
            color=message.author.color, # Display color
            timestamp=message.created_at
        )
        if len(message.attachments) > 0:
            simpleEmbed.add_field(
                name="Csatolmányok",
                value=len(message.attachments)
            )
            simpleEmbed.set_image(url=message.attachments[0].url) # Only first image is shown
        simpleEmbed.set_footer(text="Rang: " + message.author.top_role.name)
        simpleEmbed.set_author(
            name=message.author.name,
            icon_url=message.author.avatar.url
        )
        await channels["simple"].send(embed=simpleEmbed)
        
        detailedEmbed = discord.Embed(
            title=message.author.display_name + " | #" + message.channel.name,
            url=message.jump_url,
            description=message.content,
            color=message.author.color, # Display color
            timestamp=message.created_at
        )
        detailedEmbed.set_author(
            name=message.author.name,
            icon_url=message.author.avatar.url,
            url="https://discord.com/users/" + str(message.author.id)
        )
        detailedEmbed.set_footer(
            text=message.author.id
        )
        detailedEmbed.add_field(
            name="Csatolmányok",
            value=len(message.attachments),
            inline=True
        )
        detailedEmbed.add_field(
            name="ID-k",
            value=f"Felhasználó: `{message.author.id}`\nCsatorna: `{message.channel.id}`\nÜzenet: `{message.id}`\n[**Ugrás a csatornába**]({message.channel.jump_url})"
        )
        await channels["detailed"].send(embed=detailedEmbed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot: # DON'T LOG MESSAGES IF AUTHOR IS A BOT
            return
        with open("config.yaml", "r") as file: # Loads config from config.yaml
            config = yaml.safe_load(file)
            
        channels = {
            "simple": await self.bot.fetch_channel(config["log"]["simple"]),
            "detailed": await self.bot.fetch_channel(config["log"]["detailed"])
        }
        
        # Create corresponding embeds
        simpleEmbed = discord.Embed(
            title="#" + after.channel.name,
            url=after.jump_url, # A direct link to the message
            color=after.author.color, # Display color
            timestamp=after.created_at
        )
        
        if len(after.attachments) > 0:
            simpleEmbed.add_field(
                name="Csatolmányok",
                value=len(after.attachments)
            )
            simpleEmbed.set_image(url=after.attachments[0].url) # Only first image is shown
        
        simpleEmbed.add_field(
            name="Eredeti üzenet",
            value=before.content,
            inline=False
        )
        simpleEmbed.add_field(
            name="Új üzenet",
            value=after.content,
            inline=False
        )
        simpleEmbed.set_footer(text="Rang: " + after.author.top_role.name)
        simpleEmbed.set_author(
            name=after.author.name + " - Üzenet szerkesztés",
            icon_url=after.author.avatar.url
        )
        await channels["simple"].send(embed=simpleEmbed)
        
        detailedEmbed = discord.Embed(
            title=after.author.display_name + " | #" + after.channel.name,
            url=after.jump_url,
            color=after.author.color, # Display color
            timestamp=after.created_at
        )
        detailedEmbed.set_author(
            name=after.author.name + " - Üzenet szerkesztés",
            icon_url=after.author.avatar.url,
            url="https://discord.com/users/" + str(after.author.id)
        )
        detailedEmbed.set_footer(
            text=after.author.id
        )
        print(before.content, after.content, sep=", ", end="|")
        detailedEmbed.add_field(
            name="Eredeti üzenet",
            value=before.content if before.content != "" else "(nincs tartalom)",
            inline=False
        )
        detailedEmbed.add_field(
            name="Új üzenet",
            value=after.content if after.content != "" else "(nincs tartalom)",
            inline=False
        )
        detailedEmbed.add_field(
            name="Csatolmányok",
            value=len(after.attachments),
            inline=True
        )
        detailedEmbed.add_field(
            name="ID-k",
            value=f"Felhasználó: `{after.author.id}`\nCsatorna: `{after.channel.id}`\nÜzenet: `{after.id}`\n[**Ugrás a csatornába**]({after.channel.jump_url})"
        )
        await channels["detailed"].send(embed=detailedEmbed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot: # DON'T LOG MESSAGES IF AUTHOR IS A BOT
            return
        with open("config.yaml", "r") as file: # Loads config from config.yaml
            config = yaml.safe_load(file)
            
        channels = {
            "simple": await self.bot.fetch_channel(config["log"]["simple"]),
            "detailed": await self.bot.fetch_channel(config["log"]["detailed"])
        }
        
        # Create corresponding embeds
        simpleEmbed = discord.Embed(
            title="#" + message.channel.name,
            description=message.content,
            color=message.author.color, # Display color
            timestamp=message.created_at
        )
        if len(message.attachments) > 0:
            simpleEmbed.add_field(
                name="Csatolmányok",
                value=len(message.attachments)
            )
            simpleEmbed.set_image(url=message.attachments[0].url) # Only first image is shown
        simpleEmbed.set_footer(text="Rang: " + message.author.top_role.name)
        simpleEmbed.set_author(
            name=message.author.name + " - Üzenet törlés",
            icon_url=message.author.avatar.url
        )
        await channels["simple"].send(embed=simpleEmbed)
        
        detailedEmbed = discord.Embed(
            title=message.author.display_name + " | #" + message.channel.name,
            url=message.jump_url,
            description=message.content,
            color=message.author.color, # Display color
            timestamp=message.created_at
        )
        detailedEmbed.set_author(
            name=message.author.name + " - Üzenet törlés",
            icon_url=message.author.avatar.url,
            url="https://discord.com/users/" + str(message.author.id)
        )
        detailedEmbed.set_footer(
            text=message.author.id
        )
        detailedEmbed.add_field(
            name="Csatolmányok",
            value=len(message.attachments),
            inline=True
        )
        detailedEmbed.add_field(
            name="ID-k",
            value=f"Felhasználó: `{message.author.id}`\nCsatorna: `{message.channel.id}`\nÜzenet: `{message.id}`\n[**Ugrás a csatornába**]({message.channel.jump_url})"
        )
        await channels["detailed"].send(embed=detailedEmbed)
    
    async def delete_message(self, interaction: discord.Interaction, message: discord.Message):
        print("delete message ctx menu")
        if message.author.id != self.bot.user.id:
            if message.author.top_role < interaction.user.top_role:
                await message.delete()
            else:
                await interaction.response.send_message("A személy magasabb beosztású, mint te, ezért az ő üzenetét nem törölheted!", ephemeral=True)
                return
        else:
            try:
                data = message.embeds[0].url.split("/") # Splits up message so we can extract the IDs
            except IndexError:
                await interaction.response.send_message("Ezt az üzenetet nem törölheted!")
                return
            print(data)
            channel: discord.TextChannel | discord.Thread = message.guild.get_channel(int(data[5]))
            newMessage: discord.Message = await channel.fetch_message(int(data[6]))
            await newMessage.delete()
        await interaction.response.send_message("Az üzenet törölve!", ephemeral=True)
    
    async def get_joined_date(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"Member joined: {member.joined_at}")

async def setup(bot: commands.Bot):
    await bot.add_cog(MessageLogger(bot))