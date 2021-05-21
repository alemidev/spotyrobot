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

from .common import join_artists, format_track, progress_bar
from .session import sess

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

HELP.add_help("queue", "add song to queue",
				"add a track to spotify queue. A song URI can be given or a query to search for. " +
				"Add `-preview` flag to include spotify track url and embedded preview.",
				args="[-preview] <uri/song>", public=True)
@alemiBot.on_message(is_allowed & filterCommand("queue", list(alemiBot.prefixes), flags=["-preview"]))
@report_error(logger)
async def add_to_queue_cmd(client, message):
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
		spotify.add_to_queue(res["tracks"]["items"][0]["uri"])
		text = format_track(res["tracks"]["items"][0], preview=preview)
		await edit_or_reply(message, f"` → ` Added to queue : {text}", disable_web_page_preview=True)

HELP.add_help("playing", "show current track",
				"shows track currently being played, a progress bard and a preview. Add flag " +
				"`-preview` to include spotify track url and embedded preview.", args="[-preview]", public=True)
@alemiBot.on_message(is_allowed & filterCommand("playing", list(alemiBot.prefixes), flags=["-preview"]))
@report_error(logger)
async def show_current_song_cmd(client, message):
	if not sess.group_call or not sess.group_call.is_connected:
		return await edit_or_reply(message, "`[!] → ` No active call")
	preview = message.command["-preview"]
	res = spotify.current_user_playing_track()
	if not res:
		return await edit_or_reply(message, "`[!] → ` Not playing anything")
	text = format_track(res["item"], preview=preview) + '\n' + progress_bar(res["progress_ms"], res['item']['duration_ms'])
	await edit_or_reply(message, f"` → ` {text}")

HELP.add_help("skip", "skip current track", "skip current track", public=True)
@alemiBot.on_message(is_allowed & filterCommand("skip", list(alemiBot.prefixes)))
@report_error(logger)
async def skip_track_cmd(client, message):
	if not sess.group_call or not sess.group_call.is_connected:
		return await edit_or_reply(message, "`[!] → ` No active call")
	spotify.next_track()
	await edit_or_reply(message, "` → ` Skipped")

HELP.add_help(["search"], "search a song on spotify",
				"will use your query to search a song on spotify and retrieve the URI. Use this to " +
				"search the song you want before queing if it's not a common one", args="[-preview] <song>", public=True)
@alemiBot.on_message(is_allowed & filterCommand("search", list(alemiBot.prefixes), flags=["-preview"]))
@report_error(logger)
async def search_track_cmd(client, message):
	if len(message.command) < 1:
		return await edit_or_reply(message, "`[!] → ` No input")
	preview = message.command["-preview"]
	q = message.command.text
	res = spotify.search(q, limit=1)
	text = format_track(res["tracks"]["items"][0], preview=preview)
	text += f"\nURI | `{res['tracks']['items'][0]['uri']}`"
	await edit_or_reply(message, f"` → ` {text}")