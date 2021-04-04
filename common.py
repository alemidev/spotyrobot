

def join_artists(artists):
	return ",".join([artist["name"] for artist in artists])


def format_track(track):
	return  f"**{join_artists(track['artists'])}** - " + \
			f"[{track['name']}]({track['external_urls']['spotify']}) (*{track['album']['name']}*)"

def progress_bar(curr, tot, length=20):
	index = int((curr*length)/tot)
	return "─"*index + "|" + (length-index-1)*"─"