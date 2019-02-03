import discord
from discord.ext.commands import Bot
from discord.ext import commands
from discord import Game
import asyncio
import time
import json
from BNF import eval_expression_complete as BNF_eval
import random

BOT_PREFIX = ('?', '!')
with open("discord-api/secret.json") as rf:
	TOKEN = json.load(rf)["token"]

client = commands.Bot(command_prefix=BOT_PREFIX)

@client.event
async def on_ready():
	await client.change_presence(game=Game(name="with your Mom *Kappa*"))
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('-------')

@client.command(name='ping',
				description="Answers with \"'mention' Pong!\"",
				brief="Replies Pong!",
				aliases=["Beer"],
				pass_context=True)
async def ping(context):
	userMention = context.message.author.mention
	await client.say("%s Pong!"%userMention)
@client.command(name='calculate',
				description="Caclulates a custom expression using +, /, *, -, (, )",
				brief="A Calculator",
				aliases=["calc", "evaluate"],
				pass_context=True)
async def calculate(context, expression):
	userMention = context.message.author.mention
	r = BNF_eval(expression, log=False)
	await client.say(expression + " = " + str(r["result"]) +", "+userMention)

@client.command(name='random_pick',
				description="roll-dice, dice (1-6), choose(1-100), coin, coin-flip(heads, tails), you can specify your number of options",
				brief="Random chooser",
				aliases=["roll-dice", "dice", "choose", "coin", "coin flip"],
				pass_context=True)
async def pick_random(context, *args):
	OPTIONS_ROLL = {
		"coin" : ["flipped ", ["heads", "tails"]],
		"coin flip":["flipped ", ["heads", "tails"]],
		"roll-dice":["rolled ", range(6)],
		"dice":["rolled ",range(6)],
		"choose":["chosen ",range(100)],
	}
	to_say = OPTIONS_ROLL[context.invoked_with]
	if args and context.invoked_with in ["roll-dice", "dice", "choose"]:
		for e in args:
			try:
				await client.say(context.message.author.mention + ", I have " + to_say[0] + str(random.choice(range(int(e)))+1))
			except ValueError:
				await client.say(context.message.author.mention + ", what the heck is %s'%s' :alien:"%("an " if str(e)[0]=="a" else "a ", str(e)))
	else:
		await client.say(context.message.author.mention + ", I have " + to_say[0] + str(random.choice(to_say[1])+1))

@client.command(name='roles',
				description="lists roles",
				brief="lists roles",
				aliases=["list-roles"],
				pass_context=True)
async def roles(context, user=None):
	print(client.get_user(user))
	out_print = [x.name for x in context.message.author.roles]
	print(out_print)
client.run(TOKEN)