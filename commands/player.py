import re

from pyrogram import filters

from alemibot import alemiBot
from alemibot.util import is_allowed, sudo, edit_or_reply, filterCommand, report_error, set_offline, HelpCategory
from alemibot.util.command import _Message as Message

from ..session import sess

import logging
logger = logging.getLogger(__name__)

HELP = HelpCategory("PLAYER")

@alemiBot.on_message(sudo & filters.video_chat_members_invited)
@report_error(logger)
async def invited_to_voice_chat(client:alemiBot, message:Message):
	invited = [ u.id for u in message.video_chat_members_invited.users ]
	if client.me.id not in invited:
		return
	if sess.is_connected:
		return await edit_or_reply(message, "`[!] → ` Already in another call")
	await sess.start(client, message.chat.id)

@HELP.add()
@alemiBot.on_message(sudo & filterCommand("join", options={
	"name" : ["-n", "--name"],
	"type" : ["-t", "--type"],
}, flags=["-debug"]))
@report_error(logger)
async def join_call_start_radio_cmd(client:alemiBot, message:Message):
	"""join call and start radio

	Join voice call and start librespot + ffmpeg.
	It will show up as a spotify device, you should select it and play music on it.
	Specify the device name with `-n` and device type with `-t`.
	Available types are : `[ computer, tablet, smartphone, speaker, tv, avr, stb, audiodongle ]`.
	"""
	if sess.is_connected:
		return await edit_or_reply(message, "`[!] → ` Already in another call")
	devicename = message.command["name"] or client.config.get("customization", "playerName", fallback="SpotyRobot")
	devicetype = message.command["type"] or "castaudio"
	quiet = not message.command["-debug"]
	await edit_or_reply(message, "` → ` Starting player session")
	await sess.start(client, message.chat.id, device_name=devicename, device_type=devicetype, quiet=quiet)

voice_chat_invite = filters.create(lambda _, __, msg: msg.web_page.type == "telegram_voicechat")

INVITE_SPLIT = re.compile(r"http(?:s|)://t(?:elegram|).me/(?P<group>.*)\?voicechat(?:=(?P<invite>.*)|)")
@alemiBot.on_message(filters.private & sudo & filters.web_page & voice_chat_invite)
@report_error(logger)
async def invited_to_voice_chat_via_link(client:alemiBot, message:Message):
	if sess.is_connected:
		return await edit_or_reply(message, "`[!] → ` Already in another call")
	match = INVITE_SPLIT.match(message.web_page.url)
	await sess.start(client, match["group"], invite_hash=match["invite"])

@HELP.add()
@alemiBot.on_message(sudo & filterCommand("leave"))
@report_error(logger)
@set_offline
async def stop_radio_cmd(client:alemiBot, message:Message):
	"""stop radio and leave call

	Will try to terminate both librespot and ffmpeg, and then leave the voice call.
	"""
	await edit_or_reply(message, "` → ` Terminating player session")
	await sess.stop()

@HELP.add(sudo=False)
@alemiBot.on_message(is_allowed & filterCommand(["volume", "vol"]))
@report_error(logger)
async def volume_cmd(client:alemiBot, message:Message):
	"""set player volume

	Make bot set its own call volume (must have rights to manage voice call)
	"""
	if len(message.command) < 1:
		return await edit_or_reply(message, "`[!] → ` No input")
	if not sess.chat_member or not sess.chat_member.can_manage_voice_chats:
		return await edit_or_reply(message, "`[!] → ` Can't manage voice chat")
	val = int(message.command[0])
	await sess.group_call.set_my_volume(val)
	await edit_or_reply(message, f"` → ` Volume set to {val}")
