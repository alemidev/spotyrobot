# spotify plugin
This is a plugin for my userbot ([alemibot](https://github.com/alemigliardi/alemibot)) to stream spotify music into Group Calls. This is mostly intended for a third party userbot, used as "music player". You can run this on your own account but you will not be able to play music in a Voice Chat and, at the same time, listen to it or even speak. You should configure another userbot (cannot be a bot account), with `alemibot` and include only this plugin (I recommend including `core` too).

## Installation

You should first set up [alemibot](https://github.com/alemigliardi/alemibot). Once that is done, just run

	git submodule add -b dev git@github.com:alemigliardi/spoty-robot.git plugins/spoty-robot
	
in bot's root folder.

If you configured an account different than yours, you should put your user id in its `data/perms.json` like this:
```json
{"SUPERUSER": [1234]}
```
to be able to issue superuser commands to it.

After that, just update your bot normally and the submodule will be tracked too.

### Streaming audio
To be able to stream audio from spotify, you will need [librespot](https://github.com/librespot-org). Compile a binary and put it inside `data` folder. You will also need to put your spotify username and password in the `config.ini` under `[spotify]` category:
```ini
[spotify]
username = longAlphaNumericStringPossibly
password = NoNeedFor"ifYourPasswordDoesn'tHaveThemInside
```

## Commands
You can find spoty-robot commands in main help. As of now, invite your music bot to the voice call to have it join, and use `/leave` to make it disconnect.