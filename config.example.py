if __name__ == '__main__':
    exit("This was not supposed to be run as a script, this was supposed to be imported!")

doPipInstallReqs = True
# Should the autorun script do 'pip install -r requirements.txt' every time it launches?
doSubdirectoryCleanup = True
# Will clean up and reuse old directory configurations. Disable only if you want the bot to reset after each timeout.
doTransferServerData = True
# Decides whether the bot will keep the servers' data throughout the updates.

reqsTxtUrl = 'https://raw.githubusercontent.com/AtlasC0R3/drop-bot/main/requirements.txt'
# Leave this alone if you don't know what you're doing.
gitHubRepo = 'https://github.com/AtlasC0R3/drop-discord.git'
# Path to the repository it should clone. Again, don't change this if you don't know what you're doing.
confJsonUrl = 'https://raw.githubusercontent.com/AtlasC0R3/drop-bot/main/data/config.json'
# The path to the config.json file. Again again, leave this alone if you don't know what you're doing, dammit.

autoWriteTokens = True
# Automatically writes tokens for the bot. PLEASE LEAVE THIS ON, OTHERWISE YOU WILL HAVE TO MANUALLY INPUT IT EACH TIME!
useDevToken = True
# Will write every config file to pass through the development token instead of the regular one.
token = 'InsertNormalTokenHere'
# The standard bot token.
devToken = 'InsertDevTokenHere'
# The developer bot token.

ownerId = 0
# The user ID of the bot owner.
verbose = False
# Controls whether the bot will use verbose mode.
syncOwnerActivity = True
# Controls whether the bot will imitate the owner's activity.

useSteamRecentlyPlayed = 0
# Change this integer if you'd like the bot to pass through Steam's API for activities.
steamUserId = ""
# Your Steam User ID, if you have set useSteamRecentlyPlayed to 1 or 2. Leave this empty otherwise.
steamApiKey = ""
# Your Steam API key, if you have set useSteamRecentlyPlayed to 1 or 2. Leave this empty otherwise.
excludedGames = []
# The games you don't want the bot to set as its activity. You can leave this empty, it won't matter.

customBotDesc = ""
# Change this string if you'd like to set a custom description for the bot every time it launches.
# If you'd like to stick to the default description, leave this empty.
rawTermOutput = True
# Decides whether the script will clear the terminal and change the window's name.

runtime = 86400
# For how long (in seconds) the script should run. An entire day is 86400
