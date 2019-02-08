import discord
from discord.ext.commands import Bot
from discord.ext import commands
from discord import Game
from discord import utils
from itertools import cycle
import asyncio

import time, datetime
import json
import typing
from BNF import eval_expression_complete as BNF_eval
import random

BOT_PREFIX = ('?', '.')
DISPLAY_STATUSES = [("with your Mom *Kappa*", 10), ("RDR2", 2)]
START_TIME = datetime.datetime.now()
PLAYERS =  {}
with open("discord-api/secret.json") as rf:
	TOKEN = json.load(rf)["token"]

client = Bot(command_prefix=BOT_PREFIX)
client.remove_command('help')


@client.event
async def on_ready():
	START_TIME = datetime.datetime.now()
	print('Logged in as')
	print(f"Name:\t\t {client.user.name}")
	print(f"ID:\t\t {client.user.id}")
	print(f"Start time:\t {START_TIME}")
	print('-----------------')


async def log_active_time():
	await client.wait_until_ready()
	while not client.is_closed:
		await asyncio.sleep(5)
		print(f"Running time:\t {datetime.datetime.now() - START_TIME}")
		if PLAYERS:
			try:
				print("Players:")
				for i, srvr in enumerate(PLAYERS.values()):
					main_player = srvr['current']
					stat = "Playing" if main_player.is_playing() else "Paused"
					print(f"\t{i+1}. Current: \'{str(main_player.title)}\' ({str(main_player.duration)}s) - " + stat)
					print("\t\t"+", ".join([   f"\'{str(q.title)[:15]}\' ({str(q.duration)}s)" for q in srvr["queue"]   ]))
			except AttributeError:
				pass
async def change_status():
	await client.wait_until_ready()
	msgs = cycle(DISPLAY_STATUSES)
	while not client.is_closed:
		current_status = next(msgs)
		await client.change_presence(game=discord.Game(name=current_status[0]))
		await asyncio.sleep(current_status[1])

@client.command(name='ping', aliases=["Beer"], pass_context=True,
				description="Answers with \"'mention' Pong!\"", brief="Replies Pong!")
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


@client.command(name='roles', aliases=["list-roles"],	pass_context=True,
				description="lists roles", brief="lists roles")
async def roles(context, *member_name):
	member_name = " ".join(member_name)
	if not member_name:
		member_name = context.message.author.name
		out_print = [x.name for x in context.message.author.roles]
	else:
		member = utils.get(context.message.author.server.members, name=member_name)
		if not member:
			await client.say(f"No member named {member_name}!")
			return
		out_print = [x.name for x in member.roles]
	await client.say(f"{member_name}\'s roles:\n\t" + '\n\t'.join(out_print))
	print(out_print)


@client.command(name='basic', pass_context=True,
				description="basic command", brief="basic command")
async def basic(context):
	for m in context.message.server.members:
		print(m.name)


@client.command(name='clear', pass_context=True,
				description="clears your last n messages", brief="clears your messages")
async def clear(context, amount=100):
	amount = int(float(amount))
	if amount < 1:
		await client.say(f'Can not delete {amount} messages!')
		return
	channel = context.message.channel
	author = context.message.author
	messages = []
	async for message in client.logs_from(channel, limit=amount):
		if message.author.id == author.id:
			messages.append(message)
	if len(messages) == 1:
		await client.delete_message(messages[0])
		await client.say(f'Deleted 1 {author.name}\'s message! :white_check_mark:')
	else:
		await client.delete_messages(messages)
		await client.say(f'Deleted {len(messages)} {author.name}\'s messages! :white_check_mark:')


@client.event
async def on_member_join(member):
	role = utils.get(member.server.roles, name='TestRole1')
	if role:
		await client.add_roles(member, role)


@client.command(pass_context=True)
async def help(context):
	author = context.message.author

	embed = discord.Embed(color=discord.Color.orange())

	embed.set_author(name='Help')
	embed.add_field(name ='roles <user=You>', value='Returns roles of user')
	await client.send_message(author, embed=embed)



"""  ========== VOICE SECTION ==========  """

def next_player_in_queue_pop(id_):
	this_srvr = PLAYERS[id_]
	if this_srvr["loop_1"]:
		this_srvr["current"].start()
	elif this_srvr["queue"] != []:
		if this_srvr["loop_q"] == -1:
			player = this_srvr["queue"].pop(0)
			this_srvr["current"] = player
			player.start()
		else:
			player = this_srvr["queue"][this_srvr["loop_q"]]
			this_srvr["current"] = player
			this_srvr["loop_q"] = this_srvr["loop_q"]%len(this_srvr["queue"])
			player.start()
	else:
		this_srvr["current"] = None


async def get_voice_client(context, join_if_not=False):
	voice_client = client.voice_client_in(context.message.server)
	if not voice_client:

		#client is not in a voice channel
		if join_if_not:

			#joining authors voice channel
			channel = context.message.author.voice.voice_channel
			if not channel:
				#user isnt in a voice channel
				await client.say(f"You have to be in a voice channel to use this command! :x:")
				raise Exception("User not in a voice channel!")

			await client.join_voice_channel(channel)
			return client.voice_client_in(context.message.server)

		await client.send_message(context.message.channel, f"I am not in a voice channel! :x:")
		raise Exception("Client not in a voice channel")
	return voice_client

@client.command(pass_context=True)
async def fart(context):
	pass #TODO find wav

@client.command(pass_context=True)
async def join(context):
	channel = context.message.author.voice.voice_channel
	if not channel:
		#user isnt in a voice channel
		await client.say(f"You have to be in a voice channel to use this command! :x:")
		raise Exception("User not in a voice channel!")

	await client.join_voice_channel(channel)


@client.command(name="disconnect", aliases=["leave", "dc"], pass_context=True)
async def leave(context):
	voice_client = await get_voice_client(context)

	#pause
	id_ = context.message.server.id
	PLAYERS[id_]["current"].pause()

	#if not voice_client:
	#	await client.say(f"You have to be in a voice channel to use this command! :x:")
	#	return
	await voice_client.disconnect()

@client.command(name="play", aliases=["queue"], pass_context=True)
async def play(context, *qword):
	qword = " ".join(qword)
	server = context.message.server
	voice_client = await get_voice_client(context, join_if_not=True)
	player = await voice_client.create_ytdl_player(qword, ytdl_options={'default_search': 'auto'}, after=lambda: next_player_in_queue_pop(server.id))

	queues = PLAYERS.get(server.id, {"current":None, "queue":[], "loop_1":False, "loop_q":-1})
	if not queues["current"]:
		queues["current"] = player
		player.start()
	else:
		queues["queue"].append(player)
		await client.say(f"Queued {player.title}! :white_check_mark:")
	PLAYERS[server.id] = queues



@client.command(name="pause", pass_context=True)
async def pause(context):
	id_ = context.message.server.id
	PLAYERS[id_]["current"].pause()

@client.command(name="stop", pass_context=True)
async def stop(context):
	id_ = context.message.server.id
	PLAYERS[id_]["current"].stop()

@client.command(name="resume", pass_context=True)
async def resume(context):
	await get_voice_client(context, join_if_not=True)
	id_ = context.message.server.id
	PLAYERS[id_]["current"].resume()

@client.command(name="skip", pass_context=True)#TODO index skip
async def skip(context, n="1"):
	try:
		n = int(n)
	except:
		n = 1
	n = min(n, len(PLAYERS[id_]["queue"]))
	id_ = context.message.server.id
	PLAYERS[id_]["current"].stop()
	for _ in range(n):
		PLAYERS[id_]["current"] = PLAYERS[id_]["queue"].pop(0)
	PLAYERS[id_]["current"].start()

@client.command(name="volume", pass_context=True)#TODO embed
async def volume(context, n):
	try:
		n = int(n)
		n = max(1, min(n, 100))
		id_ = context.message.server.id
		PLAYERS[id_]["current"].volume = n
	except:
		pass

@client.command(name="loop", pass_context=True)
async def loop(context):
	id_ = context.message.server.id
	PLAYERS[id_]["loop_1"] = not PLAYERS[id_]["loop_1"]
	loop_n = "Song loop"
	loop_q = "Enabled!" if PLAYERS[id_]["loop_1"] >= 0 else "Disabled!"

	embed = discord.Embed(
			title=loop_n,
			color = discord.Color.blue()
		)
	embed.add_field(name=loop_n, value=loop_q)
	await client.say(embed=embed)


@client.command(name="loopqueue", pass_context=True)
async def loopqueue(context):
	id_ = context.message.server.id
	PLAYERS[id_]["loop_q"] = 0 if PLAYERS[id_]["loop_q"] == -1 else -1


	loop_n = "Queue loop"
	loop_q = "Enabled!" if PLAYERS[id_]["loop_q"] >= 0 else "Disabled!"

	embed = discord.Embed(
			title=loop_n,
			color = discord.Color.blue()
		)
	embed.add_field(name=loop_n, value=loop_q)
	await client.say(embed=embed)

client.loop.create_task(change_status())
client.loop.create_task(log_active_time())
client.run(TOKEN)