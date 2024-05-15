from discord.ext import commands, tasks
import yaml
import feedparser
import logging
from itertools import takewhile
import requests
import discord
import re

class NewsListener(commands.Cog):

    updatePeriod = { 'minutes': 5 }

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
            
        self.article_channel_id = config["news-listener"]["articles-forum"]

        with open("RSS/keyphrases.txt", "r") as file:
            self.keyphrases = [phrase.strip() for phrase in file if phrase.strip() != '']

        with open("RSS/rss_urls.txt", "r") as file:
            self.rss_urls = [url.strip() for url in file if url.strip() != '']

        self.rss_latest_date = {} # kind of a cursor; for detecting new posts

    def get_fresh_entries(self, rss_data):
        if rss_data.url not in self.rss_latest_date:
            result = rss_data.entries
        else:
            result = list(takewhile(
                lambda entry: entry.published_parsed > self.rss_latest_date[rss_data.url],
                rss_data.entries))
        
        self.rss_latest_date[rss_data.url] = rss_data.entries[0].published_parsed

        return result
    
    async def search_keyphrase_and_send(self, rss_entry):
        if self.is_keyphrase_found(rss_entry.title):
            await self.post_entry(rss_entry)
            return
        
        if self.is_keyphrase_found(rss_entry.description):
            await self.post_entry(rss_entry)
            return
        
        # One could also search in the content by resolving .link but that's costly

    
    async def post_entry(self, rss_entry):
        article_channel: discord.ForumChannel = await self.bot.fetch_channel(self.article_channel_id)
        await article_channel.create_thread(name=rss_entry.title[:100], content=rss_entry.link) # 100 is the max length for forum titles

    def is_keyphrase_found(self, haystack):
        for needle in self.keyphrases:
            if re.search(rf"(?i)\b{re.escape(needle)}\b", haystack):
                return True
        return False

    def cog_load(self):
        self.poll_news.start()

    def cog_unload(self):
        self.poll_news.cancel()

    @tasks.loop(**updatePeriod)
    async def poll_news(self):
        for url in self.rss_urls:
            try:
                data = feedparser.parse(url)
                fresh_entries = self.get_fresh_entries(data)
                logging.info(f'Got fresh entries from {url}: {[entry.title for entry in fresh_entries]}')
                for entry in fresh_entries:
                    await self.search_keyphrase_and_send(entry)

            except Exception as e:
                logging.warning(f"Error while processing RSS URL {url}: {e.with_traceback()}")

    
async def setup(bot: commands.Bot):
    await bot.add_cog(NewsListener(bot))
