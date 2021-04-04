

def join_artists(artists):
	return ",".join([artist["name"] for artist in artists])


def format_track(track):
	return  f"**{join_artists(track['artists'])}** - " + \
			f"[{track['name']}]({track['external_urls']['spotify']})"

def format_time(ms):
	return f"{(ms//1000)//60}:{(ms//1000)%60}"

def progress_bar(curr, tot, length=20):
	index = int((curr*length)/tot)
	return f"`{format_time(curr)}` {'─'*index}|{'─'*(length-index-1)} `{format_time(tot)}`"