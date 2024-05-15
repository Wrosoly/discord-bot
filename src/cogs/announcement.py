from discord.ext import commands
from discord import Embed, ButtonStyle, NotFound
from discord.ui import Button, View
from dotenv import dotenv_values
from datetime import datetime
import yaml

# This cog listens for messages in the announcements new channel and sends them to the validation channel.
# It adds a button to the message that allows the validators to approve the message.
# When the button is clicked, the message is sent to the announcements channel.
class AnnouncementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def getConfig():
        with open("config.yaml", "r") as file: # Loads config from config.yaml
            config = yaml.safe_load(file)
            
        return  {
            "CHANNEL_ID_ANNOUNCEMENTS_NEW":         config["announcments"]["new"],
            "CHANNEL_ID_ANNOUNCEMENTS":             config["announcments"]["main"],
            "CHANNEL_ID_ANNOUNCEMENTS_VALIDATE":    config["announcments"]["validate"],
            "ROLE_ID_ANNOUNCEMENT_VALIDATORS":      config["announcments"]["validator_admin_role"]
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        config = await AnnouncementCog.getConfig()

        if message.channel.id == int(config["CHANNEL_ID_ANNOUNCEMENTS_NEW"]):
            if message.author == self.bot.user:
                return

            async def button_callback(interaction):
                try:
                    await message.add_reaction("✅")
                except NotFound:
                    # Original message not found, it might have been deleted
                    return

                new_embed = interaction.message.embeds[0]
                new_embed.color = 0x00FF00
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_embed.add_field(name="Jóváhagyta", value=interaction.user.mention, inline=False)
                new_embed.add_field(name="Jóváhagyva", value=current_date, inline=False)
                await interaction.message.edit(embed=new_embed, view=View())

                target_channel = self.bot.get_channel(int(config["CHANNEL_ID_ANNOUNCEMENTS"]))
                await target_channel.send(f"@everyone\n\n{message.content}")

            button = Button(label="Beküldés", style=ButtonStyle.green, custom_id="publish_btn")
            button.callback = button_callback
            view = View()
            view.add_item(button)

            embed = Embed(
                title="Új bejelentés",
                description=message.content,
                color=0xFF0000,
            )
            embed.add_field(name="Szerző", value=message.author.mention, inline=False)

            channel = self.bot.get_channel(int(config["CHANNEL_ID_ANNOUNCEMENTS_VALIDATE"]))
            validator_role = config["ROLE_ID_ANNOUNCEMENT_VALIDATORS"]
            await channel.send(content=f"<@&{validator_role}>", embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AnnouncementCog(bot))
