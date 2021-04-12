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
	else:
		entry = dict(os.environ)
	
	data = []
	if os.path.isfile("plugins/spotyrobot/events.json"):
		with open("plugins/spotyrobot/events.json") as f:
			data = json.load(f)
	
	if not type(data) is list:
		data = []
	
	data.append(entry)
	
	with open("plugins/spotyrobot/events.json", "w") as f:
		json.dump(data, f)

