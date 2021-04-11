import asyncio
import os

from signal import SIGINT

import ffmpeg

from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import GroupCall

from bot import alemiBot

from util.permission import is_allowed, is_superuser
from util.message import edit_or_reply
from util.command import filterCommand
from util.decorators import report_error
from util.help import HelpCategory

from plugins.spotyrobot.session import sess

import logging
logger = logging.getLogger(__name__)

HELP = HelpCategory("PLAYER")

@alemiBot.on_message(is_superuser & filters.voice_chat_members_invited)
async def invited_to_voice_chat(client, message):
	if sess.group_call and sess.group_call.is_connected:
		return await edit_or_reply(message, "`[!] → ` Already in another call")
	try:
		sess.start()
		sess.group_call = GroupCall(client, "plugins/spotyrobot/data/music-fifo",
							path_to_log_file="plugins/spotyrobot/data/tgcalls.log")
		await sess.group_call.start(message.chat.id)
	except:
		logger.exception("Error while joining voice chat")

HELP.add_help("join", "join call and start radio",
				"join voice call and start librespot + ffmpeg. It will show up as " +
				"a spotify device, you should select it and play music on it. It will " +
				"be played by the bot. You can specify the device name with `-n` and the " +
				"device type with `-t`. Available types are : `[ computer, tablet, " +
				"smartphone, speaker, tv, avr, stb, audiodongle ]`.", args="[-n <name>] [-t <type>] [-debug]")
@alemiBot.on_message(is_superuser & filterCommand("join", list(alemiBot.prefixes), options={
	"name" : ["-n", "--name"],
	"type" : ["-t", "--type"],
}, flags=["-debug"]))
@report_error(logger)
async def join_call_start_radio_cmd(client, message):
	if sess.group_call and sess.group_call.is_connected:
		return await edit_or_reply(message, "`[!] → ` Already in another call")
	devicename = message.command["name"] if "name" in message.command else "SpotyRobot"
	devicetype = message.command["type"] if "type" in message.command else "speaker"
	quiet = "-debug" not in message.command["flags"]
	sess.start(device_name=devicename, device_type=devicetype, quiet=quiet)
	sess.group_call = GroupCall(client, "plugins/spotyrobot/data/music-fifo",
							path_to_log_file="plugins/spotyrobot/data/tgcalls.log")
	await sess.group_call.start(message.chat.id)
	await edit_or_reply(message, "` → ` Connected")

HELP.add_help("leave", "stop radio and leave call",
				"will first stop playback, then try to terminate both librespot and ffmpeg, " +
				"and then leave the voice call.")
@alemiBot.on_message(is_superuser & filterCommand("leave", list(alemiBot.prefixes)))
@report_error(logger)
async def stop_radio_cmd(client, message):
	sess.group_call.stop_playout()
	sess.stop()
	await sess.group_call.stop()
	await edit_or_reply(message, "` → ` Disconnected")

HELP.add_help("volume", "set player volume",
				"make bot set its own call volume (must have rights to manage voice call)")
@alemiBot.on_message(is_superuser & filterCommand("volume", list(alemiBot.prefixes)))
@report_error(logger)
async def volume_cmd(client, message):
	if "cmd" not in message.command:
		return await edit_or_reply(message, "`[!] → ` No value given")
	val = int(message.command["cmd"][1])
	await sess.group_call.set_my_volume(val)
	await edit_or_reply(message, f"` → ` Volume set to {val}")

HELP.add_help("mute", "toggle player mute", "make bot mute/unmute itself")
@alemiBot.on_message(is_superuser & filterCommand("mute", list(alemiBot.prefixes)))
@report_error(logger)
async def mute_call_cmd(client, message):
	sess.muted = not sess.muted
	sess.group_call.set_is_mute(sess.muted)
	if sess.muted:
		await edit_or_reply(message, f"` → ` Muted")
	else:
		await edit_or_reply(message, f"` → ` Unmuted")
