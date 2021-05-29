import asyncio

from pyrogram import filters
from pyrogram.types import Message

from spotipy import SpotifyOAuth, SpotifyStateError, Spotify

from bot import alemiBot

from util.permission import is_allowed, is_superuser
from util.message import edit_or_reply
from util.command import filterCommand
from util.decorators import report_error
from util.help import HelpCategory

from plugins.spotyrobot.common import join_artists, format_track, progress_bar
from plugins.spotyrobot.session import sess

import logging
logger = logging.getLogger(__name__)

HELP = HelpCategory("SPOTIFY")

auth = SpotifyOAuth(username=alemiBot.config.get("spotify", "username", fallback=None),
                    scope="user-modify-playback-state user-read-currently-playing",
                    client_id=alemiBot.config.get("spotify", "clientId", fallback=None),
                    client_secret=alemiBot.config.get("spotify", "clientSecret", fallback=None),
                    redirect_uri='https://alemi.dev/spotify.html',
                    open_browser=False)
spotify = Spotify(auth_manager=auth)
logger.debug(str(spotify.current_user()))

@HELP.add(cmd="<query>", sudo=False)
@alemiBot.on_message(is_allowed & filterCommand("queue", list(alemiBot.prefixes), flags=["-preview"]))
@report_error(logger)
async def add_to_queue_cmd(client, message):
	"""add song to queue

	Add a track to spotify queue.
	Accepts both a search query or a spotify URI.
	Use `search` command to first lookup songs if you are unsure of your query.
	Add `-preview` flag to include spotify track url and embedded preview.
	"""
	if not sess.group_call or not sess.group_call.is_connected:
		return await edit_or_reply(message, "`[!] → ` No active call")
	if len(message.command) < 1:
		return await edit_or_reply(message, "`[!] → ` No input")
	preview = message.command["-preview"]
	q = message.command.text
	if q.startswith("spotify:") or q.startswith("http://open.spotify.com"):
		spotify.add_to_queue(q)
		await edit_or_reply(message, "` → ` Added to queue")
	else:
		res = spotify.search(q, limit=1)
		if len(res) < 1:
			return await edit_or_reply(message, "`[!] → ` No results")
		spotify.add_to_queue(res["tracks"]["items"][0]["uri"])
		text = format_track(res["tracks"]["items"][0], preview=preview)
		await edit_or_reply(message, f"` → ` Added to queue : {text}", disable_web_page_preview=True)

@HELP.add(sudo=False)
@alemiBot.on_message(is_allowed & filterCommand("playing", list(alemiBot.prefixes), flags=["-preview"]))
@report_error(logger)
async def show_current_song_cmd(client, message):
	"""show track currently played

	Shows track currently being played, with a progress bar.
	Add flag `-preview` to include spotify track url and embedded preview.
	"""
	if not sess.group_call or not sess.group_call.is_connected:
		return await edit_or_reply(message, "`[!] → ` No active call")
	preview = message.command["-preview"]
	res = spotify.current_user_playing_track()
	if not res:
		return await edit_or_reply(message, "`[!] → ` Not playing anything")
	text = format_track(res["item"], preview=preview) + '\n' + progress_bar(res["progress_ms"], res['item']['duration_ms'])
	await edit_or_reply(message, f"` → ` {text}")

@HELP.add(sudo=False)
@alemiBot.on_message(is_allowed & filterCommand("skip", list(alemiBot.prefixes)))
@report_error(logger)
async def skip_track_cmd(client, message):
	"""skip current track

	Skip current track. Since playout is buffered (for resampling), skip may take up to 5s.
	"""
	if not sess.group_call or not sess.group_call.is_connected:
		return await edit_or_reply(message, "`[!] → ` No active call")
	spotify.next_track()
	await edit_or_reply(message, "` → ` Skipped")

@HELP.add(cmd="<query>", sudo=False)
@alemiBot.on_message(is_allowed & filterCommand("search", list(alemiBot.prefixes), options={
	"limit" : ["-l", "--limit"],
}, flags=["-preview"]))
@report_error(logger)
async def search_track_cmd(client, message):
	"""search a song on spotify

	Search tracks on spotify. Will return first 10 results (change with `-l`).
	Song URIs will be returned, use this before queuing uncommon songs
	"""
	if len(message.command) < 1:
		return await edit_or_reply(message, "`[!] → ` No input")
	limit = int(message.command["limit"] or 10)
	preview = message.command["-preview"]
	q = message.command.text
	res = spotify.search(q, limit=1)
	if len(res) < 1:
		return await edit_or_reply(message, "`[!] → ` No results")
	text = ""
	for i, track in enumerate(res["tracks"]["items"]):
		text += f"`→ ` {format_track(track, preview=preview)}\n` → ` **URI** `{track['uri']}`\n"
		if i >= limit:
			break
	await edit_or_reply(message, f"` → ` {text}")