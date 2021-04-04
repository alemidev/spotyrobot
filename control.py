import asyncio

from pyrogram import filters
from pyrogram.types import Message

from spotipy import SpotifyOAuth, SpotifyStateError, Spotify

from bot import alemiBot

from util.permission import is_allowed, is_superuser
from util.message import edit_or_reply
from util.command import filterCommand

from plugins.help import HelpCategory

from .common import join_artists, format_track, progress_bar

import logging
logger = logging.getLogger(__name__)

HELP = HelpCategory("SPOTIFY")

auth = SpotifyOAuth(username=alemiBot.config.get("spotify", "username", fallback=None),
                    scope="user-modify-playback-state user-read-currently-playing",
                    client_id=alemiBot.config.get("spotify", "clientId", fallback=None),
                    client_secret=alemiBot.config.get("spotify", "clientSecret", fallback=None),
                    redirect_uri='https://alemi.dev/spotify',
                    open_browser=False)
spotify = Spotify(auth_manager=auth)
logger.debug(str(spotify.current_user()))

HELP.add_help("queue", "add song to queue",
				"add a track to spotify queue. A song URI can be given or a query to search for.",
				args="<q>")
@alemiBot.on_message(is_superuser & filterCommand("queue", list(alemiBot.prefixes)))
async def add_to_queue(client, message):
	try:
		if "arg" not in message.command:
			return await edit_or_reply(message, "`[!] → ` No input")
		q = message.command["arg"]
		if q.startswith("spotify:") or q.startswith("http://open.spotify.com"):
			spotify.add_to_queue(q)
			await edit_or_reply(message, "` → ` Added to queue")
		else:
			res = spotify.search(q, limit=1)
			spotify.add_to_queue(res["tracks"]["items"][0]["uri"])
			text = format_track(res["tracks"]["items"][0])
			await edit_or_reply(message, f"` → ` Added:\n{text}")
	except Exception as e:
		logger.exception("Error in .queue command")
		await edit_or_reply(message, "`[!] → ` " + str(e))


HELP.add_help("playing", "show current track", "print `<artist> - <title> [<album>]`")
@alemiBot.on_message(is_superuser & filterCommand("playing", list(alemiBot.prefixes)))
async def show_current_song(client, message):
	try:
		res = spotify.current_user_playing_track()
		text = format_track(res["item"]) + '\n' + progress_bar(res["progress_ms"], res['item']['duration_ms'])
		await edit_or_reply(message, f"` → ` {text}")
	except Exception as e:
		logger.exception("Error in .playing command")
		await edit_or_reply(message, "`[!] → ` " + str(e))

HELP.add_help("skip", "skip current track", "skip current track")
@alemiBot.on_message(is_superuser & filterCommand("skip", list(alemiBot.prefixes)))
async def skip_track(client, message):
	try:
		spotify.next_track()
		await edit_or_reply(message, "` → ` Skipped")
	except Exception as e:
		logger.exception("Error in .skip command")
		await edit_or_reply(message, "`[!] → ` " + str(e))