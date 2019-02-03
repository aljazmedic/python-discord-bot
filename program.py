import discord
from discord.ext.command import Bot
from discord.ext import commands
import asyncio
import time
import json

with open("discord-api/secret.json") as rf:
	client.run(json.load(rf)["token"])

Cient = discord.Client()
client = command.Bot(command_prefix="!")

@client.event
async def on_ready():
	print("Bot is ready!")

@client.event
async def on_message(message):
	if message.content == "cookie":
		await client.send_message(message.channel, ":cookie:")
