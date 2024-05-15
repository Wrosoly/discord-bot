import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import hybrid_command
import yaml
import datetime

class MessageLogger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

        #TODO: Move to PenaltySystem cog
        ctx_menu = app_commands.ContextMenu(
            name="Üzenet törlése",
            callback=self.delete_message
        )
        self.bot.tree.add_command(ctx_menu)

    async def getLogChannels(self):
        with open("config.yaml", "r") as file: # Loads config from config.yaml
            config = yaml.safe_load(file)
            
        return  {
            "simple": await self.bot.fetch_channel(config["log"]["simple"]),
            "detailed": await self.bot.fetch_channel(config["log"]["detailed"]),
            "role": await self.bot.fetch_channel(config["log"]["role"]),
            "member-join-left": await self.bot.fetch_channel(config["log"]["member-join-left"])
        }
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return
            
        channels = await self.getLogChannels()
        
        await self.processSimpleMsgLog(channels["simple"], message)
        await self.processDetailedMsgLog(channels["detailed"], message)
        
    
    async def processSimpleMsgLog(self, channel : discord.abc.GuildChannel | discord.abc.PrivateChannel | discord.Thread, message : discord.message):
        # Create corresponding embeds
        simpleEmbed = discord.Embed(
            title = "#" + message.channel.name,
            url = message.jump_url, # A direct link to the message
            description = message.content,
            color = message.author.color, # Display color
            timestamp = message.created_at
        )

        simpleEmbed.set_footer(text="Rang: " + message.author.top_role.name)

        simpleEmbed.set_author(
            name=message.author.name,
            icon_url=message.author.avatar.url
        )

        if len(message.attachments) == 0: return await channel.send(embed=simpleEmbed)

        attachments = []

        for attachment in message.attachments:
            file = await attachment.to_file()

            attachments.append(file)

        return await channel.send(embed=simpleEmbed, files=attachments)

    async def processDetailedMsgLog(self, channel : discord.abc.GuildChannel | discord.abc.PrivateChannel | discord.Thread, message : discord.message):
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
            name="ID-k",
            value=f"Felhasználó: `{message.author.id}`\nCsatorna: `{message.channel.id}`\nÜzenet: `{message.id}`\n[**Ugrás a csatornába**]({message.channel.jump_url})"
        )

        if len(message.attachments) == 0: return await channel.send(embed=detailedEmbed) 

        attachments = []

        for attachment in message.attachments:
            file = await attachment.to_file()

            attachments.append(file)

        return await channel.send(embed=detailedEmbed, files=attachments)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot: return
            
        channels = await self.getLogChannels()

        await self.processSimpleMsgEdit(channels["simple"], before, after)
        await self.processsDetailedMsgEdit(channels["detailed"], before, after)
    
    async def processSimpleMsgEdit(self, channel : discord.abc.GuildChannel | discord.abc.PrivateChannel | discord.Thread, before: discord.Message, after: discord.Message):
        beforeAttachments = []
        afterAttachments = []
        
        # Create corresponding embeds
        simpleEmbed = discord.Embed(
            title="#" + after.channel.name,
            url=after.jump_url, # A direct link to the message
            color=after.author.color, # Display color
            timestamp=after.created_at
        )
        
        if len(before.attachments) > 0:
            for attachment in before.attachments:
                file = await attachment.to_file()

                beforeAttachments.append(file)

            simpleEmbed.add_field(
                name="Eredeti csatolmányok",
                value=len(beforeAttachments),
                inline=False
            )

            for attachment in after.attachments:
                file = await attachment.to_file()

                afterAttachments.append(file)

            simpleEmbed.add_field(
                name="új csatolmányok",
                value=len(afterAttachments)
            )

        
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
        await channel.send(embed=simpleEmbed, files=beforeAttachments + afterAttachments)

    async def processsDetailedMsgEdit(self, channel : discord.abc.GuildChannel | discord.abc.PrivateChannel | discord.Thread, before: discord.Message, after: discord.Message):
        beforeAttachments = []
        afterAttachments = []
    
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

        if len(before.attachments) > 0:
            for attachment in before.attachments:
                file = await attachment.to_file()

                beforeAttachments.append(file)

            detailedEmbed.add_field(
                name="Eredeti csatolmányok",
                value=len(beforeAttachments),
                inline=False
            )

            for attachment in after.attachments:
                file = await attachment.to_file()

                afterAttachments.append(file)

            detailedEmbed.add_field(
                name="új csatolmányok",
                value=len(afterAttachments)
            )

        detailedEmbed.add_field(
            name="ID-k",
            value=f"Felhasználó: `{after.author.id}`\nCsatorna: `{after.channel.id}`\nÜzenet: `{after.id}`\n[**Ugrás a csatornába**]({after.channel.jump_url})"
        )
        await channel.send(embed=detailedEmbed, files=beforeAttachments +  afterAttachments)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot: return
        
        channels = await self.getLogChannels()

        await self.processSimpleMsgDelete(channels["simple"], message)
        await self.processDetailedMsgDelete(channels["detailed"], message)
    
    async def processSimpleMsgDelete(self, channel : discord.abc.GuildChannel | discord.abc.PrivateChannel | discord.Thread, message : discord.message):
        # Create corresponding embeds
        simpleEmbed = discord.Embed(
            title="#" + message.channel.name,
            description=message.content,
            color=message.author.color, # Display color
            timestamp=message.created_at
        )

        simpleEmbed.set_footer(text="Rang: " + message.author.top_role.name)
        simpleEmbed.set_author(
            name=message.author.name + " - Üzenet törlés",
            icon_url=message.author.avatar.url
        )

        if len(message.attachments) == 0: return await channel.send(embed=simpleEmbed)
           
        attachments = []

        for attachment in message.attachments:
            file = await attachment.to_file()

            attachments.append(file)

        return await channel.send(embed=simpleEmbed, files=attachments)

    async def processDetailedMsgDelete(self, channel : discord.abc.GuildChannel | discord.abc.PrivateChannel | discord.Thread, message : discord.message):
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
            name="ID-k",
            value=f"Felhasználó: `{message.author.id}`\nCsatorna: `{message.channel.id}`\nÜzenet: `{message.id}`\n[**Ugrás a csatornába**]({message.channel.jump_url})"
        )
        
        if len(message.attachments) == 0: return await channel.send(embed=detailedEmbed)
           
        attachments = []

        for attachment in message.attachments:
            file = await attachment.to_file()

            attachments.append(file)

        return await channel.send(embed=detailedEmbed, files=attachments)
    
    async def delete_message(self, interaction: discord.Interaction, message: discord.Message):
        #TODO: Move to PenaltySystem cog
        #return
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

            if(newMessage == None): 
                interaction.response.send_message("Az üzenetet már törölték", ephemeral=True)
                return
            
            await newMessage.delete()
        await interaction.response.send_message("Az üzenet törölve!", ephemeral=True)
    
    async def get_joined_date(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"Member joined: {member.joined_at}")
    

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if len(before.roles) == len(after.roles): return
        channels = await self.getLogChannels()

        await self.processDetailedRoleUpdate(channels["role"], before, after)

    async def processDetailedRoleUpdate(self, channel: discord.TextChannel, before: discord.Member, after: discord.Member):
        embed = discord.Embed(
            title="Rangok változása",
            color=after.color, # Display color
            timestamp=datetime.datetime.now()
        )
        embed.set_author(
            name=after.name,
            icon_url=after.avatar.url,
            url="https://discord.com/users/" + str(after.id)
        )
        embed.set_footer(
            text="Felhasználó ID: " + str(after.id)
        )
        del before.roles[0]
        del after.roles[0]
        roleNamesBefore = ", ".join(["<@&" + str(x.id) + ">" for x in before.roles])
        roleNamesAfter = ", ".join(["<@&" + str(x.id) + ">" for x in after.roles])
        
        if len(roleNamesBefore) > 1024:
            roleNamesBefore = "(túl sok a megjelenítéshez.)"
        if len(roleNamesAfter) > 1024:
            roleNamesAfter = "(túl sok a megjelenítéshez.)"
        
        difference = []
        if len(before.roles) > len(after.roles):
            roleText = "Eltávolított rangok"
            for role in before.roles:
                if role not in after.roles:
                    difference.append(role)
        else:
            roleText = "Hozzáadott rangok"
            for role in after.roles:
                if role not in before.roles:
                    difference.append(role)
        differenceText = ", ".join(["<@&" + str(x.id) + ">" for x in difference])
        
        if len(differenceText) > 1024:
            differenceText = "(túl sok a megjelenítéshez.)"
        
        embed.add_field(
            name=roleText + f" ({len(difference)})",
            value=differenceText,
            inline=False
        )
        
        embed.add_field(
            name=f"Eddigi rangok ({len(before.roles)})",
            value=roleNamesBefore
        )
        embed.add_field(
            name=f"Jelenlegi rangok ({len(after.roles)})",
            value=roleNamesAfter
        )
        
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot: return
            
        channels = await self.getLogChannels()
        
        await MessageLogger.processMemberJoinLeftLog(channels["member-join-left"], member, True)
    
    @commands.Cog.listener() 
    async def on_member_remove(self, member: discord.Member):
        if member.bot: return
            
        channels = await self.getLogChannels()
        
        await MessageLogger.processMemberJoinLeftLog(channels["member-join-left"], member, False)

    async def processMemberJoinLeftLog(channel : discord.abc.GuildChannel | discord.abc.PrivateChannel | discord.Thread, member : discord.Member, joined : bool):
        # Create corresponding embeds
        memberJoinEmbed = discord.Embed(
            title = "Felhasználó" + (" belépett" if joined else " kilépett"),
            color = member.color, # Display color
            timestamp = member.joined_at
        )

        memberJoinEmbed.set_footer(text = "Rang: " + member.top_role.name)
        memberJoinEmbed.set_author(
            name = member.name,
            icon_url = member.avatar.url
        )

        memberJoinEmbed.add_field(
            name="Felhasználói adatok:",
            value=f"Nickname: `{member.display_name}`\nFelhasználónév: `{member.name}`\nID: `{member.id}`"
        )

        return await channel.send(embed=memberJoinEmbed)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(MessageLogger(bot))