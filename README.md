# spotify plugin
This is a plugin for my userbot ([alemibot](https://github.com/alemigliardi/alemibot)) to stream spotify music into Group Calls. This is mostly intended for a third party userbot, used as "music player". You can run this on your own account but you will not be able to play music in a Voice Chat and, at the same time, listen to it or even speak. You should configure another userbot (cannot be a bot account), with `alemibot` and include only this plugin (I recommend including `core` too).

## Installation

You should first set up [alemibot](https://github.com/alemigliardi/alemibot). Once that is done, just run

	git submodule add -b dev git@github.com:alemigliardi/spotyrobot.git plugins/spotyrobot
	
in bot's root folder.

If you configured an account different than yours, you should put your user id in its `data/perms.json` like this:
```json
{"SUPERUSER": [1234]}
```
to be able to issue superuser commands to it.

After that, just update your bot normally and the submodule will be tracked too.

You can include either the `player` module, the `control` module or both. They are independant and require different setups.

### Streaming audio
To be able to stream audio from spotify, you will need [librespot](https://github.com/librespot-org). Compile a binary and put it inside `data` folder. You will also need to put your spotify username and password in the `config.ini` under `[spotify]` category:
```ini
[spotify]
username = longAlphaNumericStringPossibly
password = doesntNeedToBeQuotedIfYouDontHaveQuotesInPwd
```

### Controlling spotify
To be able to control spotify playback, you need to create an application in your spotify dashboard. Find your `clientId` and `clientSecret` and add them to your config file under the `[spotify]` category:
```ini
[spotify]
clientId = longstring
clientSecret = longstring
```
When you first boot the bot with `control` enabled, you will need to generate an authentication token. A token is needed to manage playback. Once acquired, it can be refreshed.

You will be prompted on the terminal open an URL, authorize on spotify page and paste back the URL you get redirected to.

# Commands
You can find spoty-robot commands in main help, with more details on flags and arguments

### Player
All these commands are reserved to superusers.
* `/join [-debug] [-n <name>] [-t <type>]` will start a session: connect to voice call, start spotify player and wait for audio. You can specify spotify device name and type. You can also just invite the player to the group call.
* `/leave` will stop spotify player and leave group call
* `/volume <n>` will set bot volume to specified value. Only works if bot has "Manage Voice Call" permission
* `/mute` will toggle mute

### Control
All these commands are available to trusted users, and will only work while in a group call
* `/queue [-preview] <url/uri/query>` will add a track to the queue. It can be a spotify URI, url or search query, with optional preview and album art
* `/playing [-preview]` will show current playing track with progress, with optional preview and album art
* `/skip` will skip to next track