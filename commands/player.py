import asyncio
import os
import re

from signal import SIGINT

# import ffmpeg

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import UserNotParticipant

from pytgcalls import GroupCall

from bot import alemiBot

from util.permission import is_allowed, is_superuser
from util.message import edit_or_reply
from util.command import filterCommand
from util.decorators import report_error, set_offline
from util.help import HelpCategory

from plugins.spotyrobot.session import sess

import logging
logger = logging.getLogger(__name__)

HELP = HelpCategory("PLAYER")

@alemiBot.on_message(is_superuser & filters.voice_chat_members_invited)
async def invited_to_voice_chat(client, message):
	invited = [ u.id for u in message.voice_chat_members_invited.users ]
	if client.me.id not in invited:
		return
	if sess.group_call and sess.group_call.is_connected:
		return await edit_or_reply(message, "`[!] → ` Already in another call")
	try:
		sess.start()
		sess.group_call = GroupCall(client, "plugins/spotyrobot/data/music-fifo",
							path_to_log_file="plugins/spotyrobot/data/tgcalls.log")
		sess.chat_member = await client.get_chat_member(message.chat.id, "me")
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
	devicename = message.command["name"] or "SpotyRobot"
	devicetype = message.command["type"] or "speaker"
	quiet = not message.command["-debug"]
	sess.start(device_name=devicename, device_type=devicetype, quiet=quiet)
	sess.group_call = GroupCall(client, "plugins/spotyrobot/data/music-fifo",
							path_to_log_file="plugins/spotyrobot/data/tgcalls.log")
	sess.chat_member = await client.get_chat_member(message.chat.id, "me")
	await sess.group_call.start(message.chat.id)
	await edit_or_reply(message, "` → ` Connected")

voice_chat_invite = filters.create(lambda _, __, msg: msg.web_page.type == "telegram_voicechat")

INVITE_SPLIT = re.compile(r"http(?:s|)://t(?:elegram|).me/(?P<group>.*)\?voicechat=(?P<invite>.*)")
@alemiBot.on_message(filters.private & is_superuser & filters.web_page & voice_chat_invite)
@report_error(logger)
async def invited_to_voice_chat_via_link(client, message):
	if sess.group_call and sess.group_call.is_connected:
		return await edit_or_reply(message, "`[!] → ` Already in another call")
	match = INVITE_SPLIT.match(message.web_page.url)
	sess.start()
	sess.group_call = GroupCall(client, "plugins/spotyrobot/data/music-fifo",
						path_to_log_file="plugins/spotyrobot/data/tgcalls.log")
	try:
		sess.chat_member = await client.get_chat_member(match["group"], "me")
	except UserNotParticipant: # Might not be a member of target chat
		pass
	await sess.group_call.start(match["group"], invite_hash=match["invite"])

HELP.add_help("leave", "stop radio and leave call",
				"will first stop playback, then try to terminate both librespot and ffmpeg, " +
				"and then leave the voice call.")
@alemiBot.on_message(is_superuser & filterCommand("leave", list(alemiBot.prefixes)))
@report_error(logger)
@set_offline
async def stop_radio_cmd(client, message):
	sess.group_call.stop_playout()
	await sess.group_call.stop()
	sess.stop()
	await edit_or_reply(message, "` → ` Disconnected")

HELP.add_help("volume", "set player volume",
				"make bot set its own call volume (must have rights to manage voice call)")
@alemiBot.on_message(is_allowed & filterCommand("volume", list(alemiBot.prefixes)))
@report_error(logger)
async def volume_cmd(client, message):
	if len(message.command) < 1:
		return await edit_or_reply(message, "`[!] → ` No input")
	if not sess.chat_member or not sess.chat_member.can_manage_voice_chats:
		return await edit_or_reply(message, "`[!] → ` Can't manage voice chat")
	val = int(message.command[0])
	await sess.group_call.set_my_volume(val)
	await edit_or_reply(message, f"` → ` Volume set to {val}")
