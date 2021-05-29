#!/usr/bin/env python
import os
import json

if __name__ == "__main__":
	event = os.environ["PLAYER_EVENT"]
	if event in ("playing", "paused"):
		entry = {"event": event,
				 "duration": int(os.environ["DURATION_MS"]),
				 "position": int(os.environ["POSITION_MS"]),
				 "track": os.environ["TRACK_ID"]}
	elif event == "started":
		entry = {"event": event, "track": os.environ["TRACK_ID"]}
	elif event == "stopped":
		envry = dict(os.environ) # never seen this actually
	elif event == "volume_set":
		entry = {"event": event, "volume" : int(os.environ["VOLUME"])}
	elif event == "changed":
		entry = {"event": event, "from": os.environ["OLD_TRACK_ID"], "to": os.environ["TRACK_ID"]}
	else:
		entry = dict(os.environ)
	
	data = []
	if os.path.isfile("plugins/spotyrobot/data/events.json"):
		with open("plugins/spotyrobot/data/events.json") as f:
			data = json.load(f)
		if type(data) is not list:
			data = [data]
	
	data.append(entry)
	
	with open("plugins/spotyrobot/data/events.json", "w") as f:
		json.dump(data, f, indent=2)

