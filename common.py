def join_artists(artists):
	return ", ".join([artist["name"] for artist in artists])

def format_track(track, html=False, preview=False):
	if html:
		if preview:
			return f"<b>{join_artists(track['artists'])}</b> - <a href=\"{track['external_urls']['spotify']}\">{track['name']}</a>"
		return  f"<b>{join_artists(track['artists'])}</b> - {track['name']}"
	if preview:
		return f"**{join_artists(track['artists'])}** - [{track['name']}]({track['external_urls']['spotify']})"
	return  f"**{join_artists(track['artists'])}** - {track['name']}"
		

def format_time(ms):
	return f"{(ms//1000)//60:01}:{(ms//1000)%60:02}"

def progress_bar(curr, tot, length=12):
	index = int((curr*length)/tot)
	return f"`{format_time(curr)}` {'━'*index}◉{'─'*(length-index-1)} `{format_time(tot)}`"