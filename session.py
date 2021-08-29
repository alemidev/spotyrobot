import subprocess
import os

from signal import SIGINT

# import ffmpeg
from pyrogram import Client
from pyrogram.utils import MAX_CHANNEL_ID
from pyrogram.errors import UserNotParticipant
from pyrogram.raw.types import InputGroupCall
from pyrogram.raw.functions.phone import EditGroupCallTitle

from pytgcalls import GroupCallFactory

from bot import alemiBot

class Session:
	def __init__(self):
		self.spotify_process = None
		self.ffmpeg_process = None
		self.group_call = None
		self.muted = False
		self.spoty_log = None
		self.ffmpeg_log = None
		self.chat_member = None

	@property
	def is_connected(self) -> bool:
		if not self.group_call:
			return False
		return self.group_call.is_connected

	async def set_title(self, title):
		call = InputGroupCall(
				id=self.group_call.group_call.id,
				access_hash=self.group_call.group_call.access_hash)
		raw_fun = EditGroupCallTitle(call=call, title=title)
		await self.group_call.client.send(raw_fun)

	async def start(
			self,
			client:Client,
			chat_id:int,
			device_name:str = "SpotyRobot",
			device_type:str = "speaker",
			quiet:bool = True,
			network_updates:bool = True,
	) -> None:
		username = alemiBot.config.get("spotify", "username", fallback=None)
		password = alemiBot.config.get("spotify", "password", fallback=None)
		cwd = os.getcwd()
		if not os.path.isfile("plugins/spotyrobot/data/raw-fifo"):
			os.mkfifo("plugins/spotyrobot/data/raw-fifo")
		if not os.path.isfile("plugins/spotyrobot/data/music-fifo"):
			os.mkfifo("plugins/spotyrobot/data/music-fifo")
		if quiet:
			self.spoty_log = open("plugins/spotyrobot/data/spoty.log", "w")
			self.ffmpeg_log = open("plugins/spotyrobot/data/ffmpeg.log", "w")
		self.spotify_process = subprocess.Popen(
			[
				"./plugins/spotyrobot/data/librespot", "--name", device_name, "--device-type", device_type,
				"--backend", "pipe", "--device", "plugins/spotyrobot/data/raw-fifo", "-u", username, "-p", password,
				"--passthrough", "--onevent", f"{cwd}/plugins/spotyrobot/on_event.py"
			],
			stderr=subprocess.STDOUT, stdout=self.spoty_log # if it's none it inherits stdout from parent
		)
		self.ffmpeg_process = subprocess.Popen(
			[
				"ffmpeg", "-y", "-i", "plugins/spotyrobot/data/raw-fifo", "-f", "s16le", "-ac", "2",
				"-ar", "48000", "-acodec", "pcm_s16le", "plugins/spotyrobot/data/music-fifo"
			],
			stderr=subprocess.STDOUT, stdout=self.ffmpeg_log,
		)
		self.group_call = (
			GroupCallFactory(client, path_to_log_file="plugins/spotyrobot/data/tgcalls.log")
				.get_file_group_call('plugins/spotyrobot/data/music-fifo')
		)
		if network_updates:
			@self.group_call.on_network_status_changed
			async def on_network_changed(context, is_connected):
				chat_id = MAX_CHANNEL_ID - context.full_chat.id
				if is_connected:
					await client.send_message(chat_id, '` → ` Connected to group call')
				else:
					await client.send_message(chat_id, '` → ` Disconnected from group call')
		try:
			self.chat_member = await client.get_chat_member(chat_id, "me")
		except UserNotParticipant: # Might not be a member of target chat
			pass

		await self.group_call.start(chat_id)

	async def stop(self):
		try:
			self.spotify_process.send_signal(SIGINT)
			self.spotify_process.wait(timeout=5)
		except subprocess.TimeoutExpired:
			self.spotify_process.kill()
		if self.spoty_log is not None:
			self.spoty_log.close()
			self.spoty_log = None
		try:
			self.ffmpeg_process.send_signal(SIGINT)
			self.ffmpeg_process.wait(timeout=5)
		except subprocess.TimeoutExpired:
			self.ffmpeg_process.kill()
		if self.ffmpeg_log is not None:
			self.ffmpeg_log.close()
			self.ffmpeg_log = None
		self.chat_member = None
		await self.group_call.stop()

sess = Session()
