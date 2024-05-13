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

        with open("keyphrases.txt", "r") as file:
            self.keyphrases = [phrase.strip() for phrase in file if phrase.strip() != '']

        with open("rss_urls.txt", "r") as file:
            self.rss_urls = [url.strip() for url in file if url.strip() != '']

        self.rss_latest_date = {url:None for url in self.rss_urls} # kind of a cursor; for detecting new posts

    def get_fresh_entries(self, rss_data):
        if self.rss_latest_date[rss_data.url] is None:
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
        
        full_content = self.fetch_entry(rss_entry)
        
        if self.is_keyphrase_found(full_content):
            await self.post_entry(rss_entry)

    def fetch_entry(self, rss_entry):
        # TODO: do some actual HTML parsing
        return str(requests.get(rss_entry.link).content) # consider using some async library instead of request
    
    async def post_entry(self, rss_entry):
        article_channel: discord.ForumChannel = await self.bot.fetch_channel(self.article_channel_id)
        await article_channel.create_thread(name=rss_entry.link)

    def is_keyphrase_found(self, haystack):
        for needle in self.keyphrases:
            if re.search(rf"\b{re.escape(needle)}\b"):
                return True
        return False


    def cog_unload(self):
        self.pollNews.cancel()

    @tasks.loop(**updatePeriod)
    async def pollNews(self):
        for url in self.rss_urls:
            try:
                data = feedparser.parse(url)
                fresh_entries = self.get_fresh_entries(data)
                for entry in fresh_entries:
                    await self.search_keyphrase_and_send(entry)

            except Exception as e:
                logging.warning(f"Error while processing RSS URL {url}: {e}")

    
async def setup(bot: commands.Bot):
    await bot.add_cog(NewsListener(bot))
