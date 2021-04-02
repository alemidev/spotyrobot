import subprocess
import os

from signal import SIGINT

import ffmpeg

from bot import alemiBot

class Session:
	def __init__(self):
		self.spotify_process = None
		self.ffmpeg_process = None
		self.group_call = None
		self.muted = False
		self.logfile = None

	def start(self, device_name="SpotyRobot", device_type="speaker", quiet=True):
		username = alemiBot.config.get("spotify", "username", fallback=None)
		password = alemiBot.config.get("spotify", "password", fallback=None)
		try:
			os.mkfifo("data/raw-fifo")
			os.mkfifo("data/music-fifo")
		except FileExistsError:
			pass
		if quiet:
			self.logfile = open("data/spotify.log", "w")
		self.spotify_process = subprocess.Popen(
			["./data/librespot", "--name", device_name, "--device-type", device_type, "--backend", "pipe",
			 "--device", "./data/raw-fifo", "-u", username, "-p", password, "--passthrough"],
			stderr=subprocess.STDOUT, stdout=self.logfile # if it's none it inherits stdout from parent
		)
		self.ffmpeg_process = ffmpeg.input("data/raw-fifo").output(
			"data/music-fifo",
			format='s16le',
			acodec='pcm_s16le',
			ac=2,
			ar='48k'
		).overwrite_output().run_async(quiet=quiet)

	def stop(self):
		try:
			self.spotify_process.send_signal(SIGINT)
			self.spotify_process.wait(timeout=5)
		except TimeoutError:
			self.spotify_process.kill()
		try:
			self.ffmpeg_process.send_signal(SIGINT)
			self.ffmpeg_process.wait(timeout=5)
		except TimeoutError:
			self.ffmpeg_process.kill()
		os.remove("data/music-fifo")
		os.remove("data/raw-fifo")
		if self.logfile is not None:
			self.logfile.close()
			self.logfile = None

sess = Session()