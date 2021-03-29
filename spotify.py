import asyncio
import secrets
import random
import os
import io
import re

from signal import SIGINT

import ffmpeg	# pip install ffmpeg-python

from PIL import Image, ImageEnhance, ImageOps

from pyrogram import filters
from pyrogram.types import InputMediaPhoto, InputMediaVideo, Message

from pytgcalls import GroupCall		# pip install pytgcalls

from bot import alemiBot

from util import batchify
from util.permission import is_allowed, is_superuser
from util.message import edit_or_reply, get_text, is_me
from util.command import filterCommand

from plugins.help import HelpCategory

import logging
logger = logging.getLogger(__name__)

HELP = HelpCategory("SPOTIFY")
group_call = None
decoder_instance = None
spotify_instance = None
muted = False

async def prep_radio(device_name="SpotyRobot"):
	global spotify_instance
	global decoder_instance
	global group_call
	username = alemiBot.config.get("spotify", "username", fallback=None)
	password = alemiBot.config.get("spotify", "password", fallback=None)
	try:
		os.mkfifo("data/raw-fifo")
		os.mkfifo("data/music-fifo")
	except FileExistsError:
		pass
	spotify_instance = await asyncio.create_subprocess_exec(
		f"./data/librespot", "--name", device_name, "--backend", "pipe", "--device", "./data/raw-fifo", "-u", username, "-p", password, "--passthrough"
	)
	decoder_instance = ffmpeg.input("data/raw-fifo").output(
		"data/music-fifo",
		format='s16le',
		acodec='pcm_s16le',
		ac=2,
		ar='48k'
	).overwrite_output().run_async()

@alemiBot.on_message(is_superuser & filters.voice_chat_members_invited)
async def invited_to_voice_chat(client, message):
	global group_call
	try:
		await prep_radio()
		group_call = GroupCall(client, path_to_log_file='')
		await group_call.start(message.chat.id)
		group_call.input_filename = "data/music-fifo"
		group_call.restart_playout()
	except:
		logger.exception("Error in .leave command")

HELP.add_help("join", "join call and start radio", "join call and start radio")
@alemiBot.on_message(is_superuser & filterCommand("join", list(alemiBot.prefixes), options={
	"devicename" : ["-n", "--name"]
}))
async def join_call_start_radio(client, message):
	global group_call
	try:
		await prep_radio(device_name=message.command["devicename"] 
									if "devicename" in message.command else "SpotyRobot")
		group_call = GroupCall(client, path_to_log_file='')
		await group_call.start(message.chat.id)
		group_call.input_filename = "data/music-fifo"
		group_call.restart_playout()
		await edit_or_reply(message, "` â†’ ` Connected")
	except Exception as e:
		logger.exception("Error in .leave command")
		await edit_or_reply(message, "`[!] â†’ ` " + str(e))

HELP.add_help("leave", "stop radio and leave call", "stop radio and leave call")
@alemiBot.on_message(is_superuser & filterCommand("leave", list(alemiBot.prefixes)))
async def stop_radio(client, message):
	global spotify_instance
	global decoder_instance
	global group_call
	try:
		await group_call.stop()
		spotify_instance.kill() # I would love to stop this more gracefully but sometimes it just hangs!
		await spotify_instance.wait()
		decoder_instance.send_signal(SIGINT)
		decoder_instance.wait()
		os.remove("data/music-fifo")
		os.remove("data/raw-fifo")
		await edit_or_reply(message, "` â†’ ` Disconnected")
	except Exception as e:
		logger.exception("Error in .leave command")
		await edit_or_reply(message, "`[!] â†’ ` " + str(e))
	await client.set_offline()

HELP.add_help("volume", "join call and start radio", "join call and start radio")
@alemiBot.on_message(is_allowed & filterCommand("volume", list(alemiBot.prefixes)))
async def volume(client, message):
	if "cmd" not in message.command:
		return await edit_or_reply(message, "`[!] â†’ ` No value given")
	val = int(message.command["cmd"][1])
	await group_call.set_my_volume(val)
	await edit_or_reply(message, f"` â†’ ` Volume set to {val}")

HELP.add_help("mute", "join call and start radio", "join call and start radio")
@alemiBot.on_message(is_allowed & filterCommand("mute", list(alemiBot.prefixes)))
async def mute_call(client, message):
	global muted
	group_call.client = client
	muted = not muted
	group_call.set_is_mute(muted)
	if muted:
		await edit_or_reply(message, f"` â†’ ` Muted")
	else:
		await edit_or_reply(message, f"` â†’ ` Unmuted")

# @alemiBot.on_message(main_filter & cmd_filter('rejoin'))
# @init_client_and_delete_message
# async def reconnect(*_):
#	  await group_call.reconnect()

# @alemiBot.on_message(main_filter & cmd_filter('replay'))
# @init_client_and_delete_message
# async def restart_playout(*_):
#	  group_call.restart_playout()

# @alemiBot.on_message(main_filter & cmd_filter('stop'))
# @init_client_and_delete_message
# async def stop_playout(*_):
#	  group_call.stop_playout()

# @alemiBot.on_message(main_filter & cmd_filter('pause'))
# @init_client_and_delete_message
# async def pause(*_):
#	  group_call.pause_playout()

# @alemiBot.on_message(main_filter & cmd_filter('resume'))
# @init_client_and_delete_message
# async def resume(*_):
#	  group_call.resume_playout()
