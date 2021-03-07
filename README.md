# Drop Autorun
A little script I made together that I use on the online-hosted version. 
Meant to be as straightforward as possible: adjust configurations, run the script, and you're up and running.
Sounds cool? Awesome. Now you may be wondering "how do I start?", and for that, well...

## How do I start?
**NOTE: This script only works on Posix/Linux, as it was designed to be run on servers!**
While it could be possible for me to edit my script to work natively on Windows,
I don't *really* see the point in doing that, and if the script *does* work for you on Windows (not WSL), you're on your own.
For now, the only supported way of running this script on Windows is by using [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10).
For macOS/Darwin users, ~~I'm too broke to test my script on this platform~~ the script *may* or *may not* work, and I don't have any ideas for a workaround other than virtualization.

1. Make sure Python3 is installed *(minimum recommended version is Python 3.7, though you may be able to get away with 3.6 or even 3.5, but please note that you are on your own with this, I can not help you)* and that you have a functioning pip install. **Python 2 will not work.**
2. Download this branch's files; you may do so using Git, SSH or SVN. Example for command-line Git: `git clone -b autorun https://github.com/AtlasC0R3/drop-discord.git`
3. Create a `config.py` file base off `config.example.py`; edit it so that the script will behave as you please.
4. Run `autorun.py`, and the script shall do its work by itself.
