# Drop
A simple Discord server utility bot. Drop is meant to be a server utility bot that tries to be as privacy-aware and simple as possible, while also retaining usability. It is also free: not as in priceless, but as in freedom. Alan please add details.

## Commands
### Basic
- 8ball: Plain old 8ball commands, present on almost every utility bot, and Drop is no exception.
- embed: Sends an embed, based off user response.
- hostinfo: Returns info about the current bot host. No IP addresses of course, I'm not *that* braindead yet.
- owofy: "Translates" sentences to "owospeak". I'm going to be honyest, this isn't my pwoudest wowk.
- ping: No, not the M1 Garand's ping unfortunately. It's simply a command to check the bot's latency.
- say: Repeats what the user has inputted. *Repeats what the user has inputted.*
- storepins: ~~I don't know why I never put that in the Moderation category, but oh well.~~ It's simply a command that stores pinned messages from a channel to another inputted channel, for those of you who just can't stop pinning messages.
### Configuration
- anonymouslogs: Toggles whether or not the bot should automatically upload error logs to the bot host. *Note: may raise privacy concerns among certain users, please read privacy notice down below*
- banword: Prevents a certain word from being said. Useful for servers that doesn't allow the N word, or something like that.
- configinfo: Prints all info retained in the configuration file. 
- toggle_inactivity: Toggles the inactivity function of this bot. If there haven't been a lot of messages in a specific amount of time, the bot will send a random message. *This will only occur if the channel has that feature enabled*
- inactivitychannel: Toggles whether or not the inactivity function should happen in a specified channel.
- togglecommand: Toggles a command's usability in a server. In case you don't want warn commands, mute commands, ~~or the owofy command,~~ you can disable those commands.
### Moderation
- ban: Bans a user. *Honestly, why wouldn't you just want to ban the user yourself.*
- kick: Kicks a user. *Again, why wouldn't you want to do it yourself.*
- unban: Unbans a user. *Seriously, just do it yourself, it's not that hard.*
- purge: Deletes an amount of messages in a channel ~~so you can remove all evidence of your antifur crime plans or whatever~~.
- set_rule: Sets a rule for your server, so users can then use the `rules` command to make the bot say that specific rule. Doesn't matter if it already exists, too.
- remove_rule: Removes a rule.
- rules: Prints a specified rule. Useful to show to people that they are breaking a rule.
### Mute
- mute: Mutes a user temporarily, so that they can not talk in the server. *Of course, that depends on the role that is defined as the "mute role".*
- mute_status: Retrieves info about a user's current mute, if there is one.
- unmute: Removes a user's mute.
### Warn
- warn: All *good* utility bots have this command, and again, Drop is no exception. Hands out a warn to someone, useful for someone is breaking the rules.
- edit_warn: Edits a warn's reason.
- remove_warn: Removes a user's warn.
- warns: Returns all of a user's warns, if there are any.


## Pre-hosted version
While I do have a pre-hosted version of the bot, it may not be the most reliable option, hence why I tend to discourage it.
If you're just looking to try out the bot's functionalities, casually use its commands or test its capabilities, I don't find anything wrong with this usage; if you rely on the bot as your server's "backbone", please consider self hosting it. The pre-hosted version may have latency issues, slowdowns, temporary outages or ~~memory loss~~ config file deletion. (I'm terrible at explaining)

### Privacy notice
The pre-hosted version shall always be the same software as the one available on the GitHub repository, main branch. Your data belongs to you, and the data that the bot collects about your server shall never be shared with anyone else other than your own server.

What info this bot may collect is:
- **Configuration data**, you may use the `configinfo` command to view the config data;
- **Bot mentions**, if a user mentions the bot with no command, only the user's ID will be stored and nothing else: this is to help the bot know if it should say the prefix or not;
- **Rule information**, the "rules" that have been set shall be stored, though the ones that shall be removed will be, well, removed entirely;
- **Warn data**, what will be stored is:
  - the date and time where the warn has occured;
  - the name and ID of the one who has been warned;
  - the name and ID of the one who has issued a warn;
  - the reason as to why the warn has been issued;
  - the channel where the warn has been issued
- **Mute data**, what will be stored is:
  - The time where the user will be unmuted;
  - The user who has requested the mute;
  - The mute role
- **Anonymous error logs**, if, and only if, a server manager has opted in to the automatic submission of error logs to the bot host. This is disabled by default.

This notice is subject to change without any warning, so please proceed with that in mind.
If you wish to delete all data from a specific server, please contact me. I am working on a command to delete all data from a server upon request.
