import discord
from discord.ext import commands, tasks
from typing import Literal, List
import datetime
import yaml

class PunishmentView(discord.ui.Modal, title="Büntetés"):
    """This should be added to a message. Ex: `await TextChannel.send(content=..., view=PunishmentView())`"""
    member = discord.ui.UserSelect(
        placeholder="Felhasználó"
    )
    
    reason = discord.ui.Select(
        placeholder="Indoklás",
        options=[
            discord.SelectOption(
                label="Egyedi indoklás",
                value="custom"
            ),
            discord.SelectOption(
                label="Trollkodás",
                value="trollkodás blablabla hosszú leírás"
            )
            # add more options :3
        ]
    )
    
    customReason = discord.ui.TextInput(
        label="Indok",
        placeholder="pl. szabályok megszegése",
        required=False,
        min_length=10
    )
    
    weight = discord.ui.Select(
        placeholder="Súlyosság",
        options=[
            discord.SelectOption(
                label="Enyhe",
                value=1
            ),
            discord.SelectOption(
                label="Közepes",
                value=2
            ),
            discord.SelectOption(
                label="Súlyos",
                value=3
            )
        ],
        min_values=1,
        max_values=1
    )
    
    duration = discord.ui.TextInput(
        label="Lejárat",
        placeholder="Pl. 1d12h, 12h, 5m",
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.reason == "custom" and self.customReason is None:
            return await interaction.response.send_message("Kötelező megadni egyedi indokot, ha kiválasztottad az \"Egyedi indoklás\"-t az indokok listájából!")
        
        Penalty.punishments.append(Punishment(
            Penalty.sanction(
                Penalty,
                self.member.id,
                interaction.user.id,
                self.weight,
                self.duration,
                reason=self.reason
            )
        ))
        await interaction.response.send_message("Büntetés kiosztva!")

class Punishment:
    def __init__(self, author: int, user: int, duration: int, reason: str, time: datetime.datetime, weight: Literal[1, 2, 3]):
        self.author = author # Discord ID
        self.user = user # Discord ID
        self.duration = duration
        self.reason = reason
        self.time = time
        self.weight = weight

class Penalty(commands.Cog):
    def __init__(self, bot: commands.Bot, serverid: int):
        self.bot: commands.Bot = bot
        self.serverid = serverid # This will be 
        self.punishments = []
        
        with open("config.yaml", "r") as file:
            self.server = yaml.safe_load(file)["servers"]["test"]
    
    async def sanction(self, user: discord.Member, author: discord.Member, weight: Literal[1, 2, 3], time: int, *, reason: str):
        """Sanctions member of discord server"""
        punishmentData = Punishment(author.id, user.id, time*weight, reason, datetime.datetime.now())
        self.punishments.append(
            {
                "author": punishmentData.author,
                "user": punishmentData.user,
                "duration": punishmentData.time,
                "reason": punishmentData.reason,
                "time": datetime.datetime.now(),
                "weight": weight
            }
        )
        # TODO: Use db, for now everything gets deleted after bot restart
        
    
    async def autoPunish(self, punishments: List[Punishment], userid: int):
        """This function should be ran every time a punishment takes place. It will punish the member based on how many warns they have in the past week.

        Args:
            punishments (List[Punishment]): A list of every punishment in the server. (this will be removed when we'll have a db)
            userid (int): The user's ID
        """
        userPunishments = []
        for i in punishments:
            if i.user == userid:
                userPunishments.append(i)

        BAN_CASES = 10
        MUTE_CASES = 5
        
        # Calculate the date and time for one week ago
        now = datetime.datetime.now()
        one_week_ago = now - datetime.timedelta(days=7)

        # Filter the list to include only those dates that are within the last week
        filtered_dates = [date for date in [x.time for x in userPunishments] if one_week_ago <= date <= now]
        
        guild: discord.Guild = await self.bot.fetch_guild(self.server)
        user: discord.Member = guild.fetch_member(userid)
        if user is None:
            return # If user is not in the guild, don't try muting/banning them, it'll give an error
            
        if len(filtered_dates) < MUTE_CASES:
            return
        elif len(filtered_dates) == MUTE_CASES:
            await user.timeout(until=now + datetime.timedelta(days=1), reason=f"1 hét alatt {MUTE_CASES} figyelmeztetés")
            try:
                embed = discord.Embed(title="Le lettél némítva", description=f"Mivel egy hét alatt **{MUTE_CASES} alkalommal** figyelmeztettek téged, ezért 1 napra automatikusan le lettél némítva.\nHa 1 hét alatt **{BAN_CASES}** figyelmeztetést kapsz, __örökre ki leszel tiltva a szerverről!__", timestamp=discord.utils.utcnow())
                embed.set_footer(text="Ha fellebbeznél, írj itt!")
                await user.send(embed=embed)
            except:
                pass # If user has DMs disabled, don't make the bot freak out (discord gives a 403 error)
        elif len(filtered_dates) >= BAN_CASES:
            await user.timeout(until=now + datetime.timedelta(days=1), reason=f"1 hét alatt {MUTE_CASES} figyelmeztetés")
            try:
                embed = discord.Embed(title="Örökre ki lettél tiltva", description=f"Mivel egy hét alatt több, mint **{BAN_CASES} alkalommal** figyelmeztettek téged, ezért örökre ki lettél tiltva a **Talpra, Magyarok!** szerveréről!", timestamp=discord.utils.utcnow())
                embed.set_footer(text="Ha fellebbeznél, írj itt!")
                await user.send(embed=embed)
            except:
                pass # If user has DMs disabled, don't make the bot freak out (discord gives a 403 error)

async def setup(bot):
    await bot.add_cog(Penalty(bot), Penalty(bot).server)