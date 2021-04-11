#!/usr/bin/env python
import os
import json

if __name__ == "__main__":
	entry = dict(os.environ)
	try:
		event = os.environ["PLAYER_EVENT"]
		track_id = os.environ["TRACK_ID"]
		old_track_id = os.environ["OLD_TRACK_ID"]
		entry = {"event": event, "track": track_id, "previous": old_track_id}
	except:
		pass
	
	data = []
	if os.path.isfile("plugins/spotyrobot/events.json"):
		with open("plugins/spotyrobot/events.json") as f:
			data = json.load(f)
	
	if not type(data) is list:
		data = []
	
	data.append(entry)
	
	with open("plugins/spotyrobot/events.json", "w") as f:
		json.dump(data, f)

