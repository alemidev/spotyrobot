from pyrogram.enums import ParseMode

from spotipy import SpotifyOAuth, Spotify

from alemibot import alemiBot
from alemibot.util import is_allowed, edit_or_reply, filterCommand, report_error, HelpCategory
from alemibot.util.command import _Message as Message

from ..common import format_track, progress_bar
from ..session import sess

import logging
logger = logging.getLogger(__name__)

HELP = HelpCategory("SPOTIFY")

SPOTIFY : Spotify

@alemiBot.on_ready()
async def setup_spotify_oauth_api_cb(client:alemiBot):
	global SPOTIFY
	auth = SpotifyOAuth(
		username=client.config.get("spotify", "username", fallback=None),
		scope="user-modify-playback-state user-read-currently-playing",
		client_id=client.config.get("spotify", "clientId", fallback=None),
		client_secret=client.config.get("spotify", "clientSecret", fallback=None),
		redirect_uri='https://alemi.dev/spotify.html',
		open_browser=False
	)
	SPOTIFY = Spotify(auth_manager=auth)
	logger.debug(str(SPOTIFY.current_user()))

@HELP.add(cmd="<query>", sudo=False)
@alemiBot.on_message(is_allowed & filterCommand("queue", list(alemiBot.prefixes), flags=["-preview"]))
@report_error(logger)
async def add_to_queue_cmd(client:alemiBot, message:Message):
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
		SPOTIFY.add_to_queue(q)
		await edit_or_reply(message, "` → ` Added to queue")
	else:
		res = SPOTIFY.search(q, limit=1)
		if len(res) < 1:
			return await edit_or_reply(message, "`[!] → ` No results")
		SPOTIFY.add_to_queue(res["tracks"]["items"][0]["uri"])
		text = format_track(res["tracks"]["items"][0], preview=preview)
		await edit_or_reply(message, f"` → ` Added to queue : {text}", disable_web_page_preview=True)

@HELP.add(sudo=False)
@alemiBot.on_message(is_allowed & filterCommand("playing", list(alemiBot.prefixes), flags=["-preview"]))
@report_error(logger)
async def show_current_song_cmd(client:alemiBot, message:Message):
	"""show track currently played

	Shows track currently being played, with a progress bar.
	Add flag `-preview` to include spotify track url and embedded preview.
	"""
	if not sess.group_call or not sess.group_call.is_connected:
		return await edit_or_reply(message, "`[!] → ` No active call")
	preview = message.command["-preview"]
	res = SPOTIFY.current_user_playing_track()
	if not res:
		return await edit_or_reply(message, "`[!] → ` Not playing anything")
	text = format_track(res["item"], preview=preview) + '\n' + progress_bar(res["progress_ms"], res['item']['duration_ms'])
	await edit_or_reply(message, f"` → ` {text}")

@HELP.add(sudo=False)
@alemiBot.on_message(is_allowed & filterCommand("skip", list(alemiBot.prefixes)))
@report_error(logger)
async def skip_track_cmd(client:alemiBot, message:Message):
	"""skip current track

	Skip current track. Since playout is buffered (for resampling), skip may take up to 5s.
	"""
	if not sess.group_call or not sess.group_call.is_connected:
		return await edit_or_reply(message, "`[!] → ` No active call")
	SPOTIFY.next_track()
	await edit_or_reply(message, "` → ` Skipped")

@HELP.add(cmd="<query>", sudo=False)
@alemiBot.on_message(is_allowed & filterCommand("search", list(alemiBot.prefixes), options={
	"limit" : ["-l", "--limit"],
}, flags=["-preview"]))
@report_error(logger)
async def search_track_cmd(client:alemiBot, message:Message):
	"""search a song on spotify

	Search tracks on spotify. Will return first 5 results (change with `-l`).
	Song URIs will be returned, use this before queuing uncommon songs
	"""
	if len(message.command) < 1:
		return await edit_or_reply(message, "`[!] → ` No input")
	limit = int(message.command["limit"] or 5)
	preview = message.command["-preview"]
	q = message.command.text
	res = SPOTIFY.search(q, limit=limit)["tracks"]["items"]
	if len(res) < 1:
		return await edit_or_reply(message, "`[!] → ` No results")
	text = f"<code>→ </code> Results for \"<i>{q}</i>\"\n"
	for track in res:
		text += f"<code> → </code> {format_track(track, html=True, preview=preview)}\n\t\t\t\t<code>{track['uri']}</code>\n"
	await edit_or_reply(message, text, parse_mode=ParseMode.HTML, disable_web_page_preview=(len(res) > 1))