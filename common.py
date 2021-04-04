

def join_artists(artists):
	return ",".join([artist["name"] for artist in artists])


def format_track(track):
	return  f"**{join_artists(track['artists'])}** - " + \
			f"[{track['name']}]({track['external_urls']['spotify']}) (*{track['album']['name']}*)"

def progress_bar(curr, tot, len=20):
	index = int((curr*len)/tot)
	out = "─"*len
	out[index] = '|'
	return out