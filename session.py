import subprocess
import os

from signal import SIGINT

# import ffmpeg

from bot import alemiBot

class Session:
	def __init__(self):
		self.spotify_process = None
		self.ffmpeg_process = None
		self.group_call = None
		self.muted = False
		self.spoty_log = None
		self.ffmpeg_log = None

	def start(self, device_name="SpotyRobot", device_type="speaker", quiet=True):
		username = alemiBot.config.get("spotify", "username", fallback=None)
		password = alemiBot.config.get("spotify", "password", fallback=None)
		try:
			os.mkfifo("data/raw-fifo")
			os.mkfifo("data/music-fifo")
		except FileExistsError:
			pass
		if quiet:
			self.spoty_log = open("data/spoty.log", "w")
			self.ffmpeg_log = open("data/ffmpeg.log", "w")
		self.spotify_process = subprocess.Popen(
			["./data/librespot", "--name", device_name, "--device-type", device_type, "--backend", "pipe",
			 "--device", "./data/raw-fifo", "-u", username, "-p", password, "--passthrough"],
			stderr=subprocess.STDOUT, stdout=self.spoty_log # if it's none it inherits stdout from parent
		)
		# # option "quiet" still sends output to pipe, need to send it to DEVNULL!
		# self.ffmpeg_process = ffmpeg.input("data/raw-fifo").output(
		# 	"data/music-fifo",
		# 	format='s16le',
		# 	acodec='pcm_s16le',
		# 	ac=2,
		# 	ar='48k'
		# ).overwrite_output().run_async(quiet=quiet)
		self.ffmpeg_process = subprocess.Popen(
			["ffmpeg", "-y", "-i", "data/raw-fifo", "-f", "s16le", "-ac", "2",
			 "-ar", "48000", "-acodec", "pcm_s16le", "data/music-fifo"],
			stderr=subprocess.STDOUT, stdout=self.ffmpeg_log,
		)

	def stop(self):
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
		os.remove("data/music-fifo")
		os.remove("data/raw-fifo")

sess = Session()