# Drop
A drop-mod frontend built with Discord.py, and also my main programming project.

# Notice regarding the bot's future
I know no one really cares or knows about this bot, but it was my own project since September 2020. Sometimes I'd just open up VSCodium and work on it a bit more.
Then that project evolved into an actual Discord bot. And then I kept working on it. And I had fun. Until recently where I've looked at Matrix.org, an open source Discord alternative
that is more consumer-friendly. So the project fell back a bit, plus new ideas weren't popping up anymore.

Until today. Rapptz was announcing that [Discord.py was going to be discontinued](https://gist.github.com/Rapptz/4a2f62751b9600a31a0d3c78100287f1).
And so, I don't see much motivation to keep working on a creation that I know will just stop working no matter what I do.

**It's been fun**, but seriously fuck Discord. They've proven, in my eyes, to be anti-consumer more than anything. I'm really sad that this is the only conclusion I can reach.
If I can, I'll try working on other projects, but for now, I'll keep Drop up as much as I can.
I'm so sorry.

Update, as of September 18th 2021: **drop-discord will no longer be receiving updates**, this whole situation has been pretty demoralizing and I find no purpose to work on something that'll just die anyway, on a shitty platform.
I will attempt to recreate this bot in [Matrix](https://matrix.org), but for now, please don't use this bot. I might also stop hosting the bot.

## What the hell is this? 
~~Didn't you read the text above?~~ This is a Python bot that was built from scratch that was meant to be as free as possible, while still retaining utility in mind. 
## How do I use it?
There are two ways: you can self-host it (recommended), or use the already hosted version, that I am personally hosting.

*Note: I don't mind if you just try the already hosted version just to see if the bot functions. If you do end up using the bot, consider self-hosting it; the one I'm already hosting might not always work or be online.*


### Self-hosting the bot
There are two ways of self-hosting the bot: the autorun script way, or the manual way.

#### Using the autorun script
Please move to the [Autorun branch](https://github.com/AtlasC0R3/drop-discord/tree/autorun) of this repository if you want to proceed this way.

#### Manually hosting the bot
1. Make sure Python3 is installed *(minimum recommended version is Python 3.7, though you may be able to get away with 3.6 or even 3.5. If you do, please note that you are on your own with this, I can not help you)* and that you have a functioning pip install. **Python 2 will not work.**
2. Download the bot's files; you may clone this repository using Git.
3. Install the required dependencies. To do so, you may use `pip install -r requirements.txt` *(or pip3, depending on your install)*
4. Make sure your `config.json` is configured correctly, and that `token.txt` has the correct bot token (if the bot cannot find it, it will ask the user for the token). *If you do not know how to get a bot token, you may search it on Google, Bing, DuckDuckGo or whatever your preferred search engine may be.*
5. Run `main.py`
6. ~~Profit.~~ You now have self-hosted this bot.

### Using the already hosted bot
The self-hosted version works, and is updated every day, though it may not be available 24/7; some blackouts may occur, it may be slow, or your data could *very rarely* vanish.
If you are willing to look past those issues, [you can invite the bot using this link](https://discord.com/oauth2/authorize?client_id=749623401706029057&permissions=60518&scope=bot). Please read the [privacy notice](https://atlasc0r3.github.io/drop-discord/#privacy-notice) before proceeding.

## Frequently Asked Questions ~~even though no one asked any questions~~

### Q: Do I _have_ to self-host this bot? Is there no online hosted version?
Well, you can use the online version, but please consider self-hosting it unless you *really* can't.

### Q: How can I contribute?
You can use a pull request to do so, or open an issue.

### Q: I found a bug/have suggestions for this bot! 
You may open an issue describing what you would like to suggest or report. Please be descriptive though, or else I can't really help if I only have 10-15 words just vaguely talking about something. 

### Q: Is this just someone's meme garbage?
No, and surprisingly yes.

### Q: How can I add cogs/extensions?
Simply create a \*.py file in the `cogs` directory, make it look like an actual Discord.py cog, and the bot *should* load it on start-up!

### Q: What is `cogs/mistakes.py.bak`?
Basically just some commands I had made for the bot that turned out to be extremely experimental, or simply mistakes.

### Q: What does `WARNING:discord.client:PyNaCl is not installed, voice will NOT be supported` mean?
Not much in this case, it's just Discord.py warning you that voice won't be supported. I'm saying that it isn't really an issue, because drop-discord has no voice commands or functions.

### Q: Can I make the bot say suggestive things? 
_Okay, why?_

## Credits
Dependencies, people who have helped...

**[Discord.py](https://github.com/Rapptz/discord.py)** by [Rapptz](https://github.com/Rapptz/)

**[discord-pretty-help](https://github.com/stroupbslayen/discord-pretty-help)** by [StroupBSlayen](https://github.com/stroupbslayen)

**[parsedatetime](https://github.com/bear/parsedatetime)** by [bear](https://github.com/bear)

For more licenses, check the `license` command in the bot.

***

**[EvieePy on GitHub Gist](https://gist.github.com/EvieePy)**, has provided a ton of very helpful examples that I used throughout this project

**[Discord](https://discord.com)** for existing

**Countless other Discord bots** that I took inspiration from

**You** for checking this out, you're amazing
