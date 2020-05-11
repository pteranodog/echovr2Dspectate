# echovr2Dspectate
This python file reads from the EchoVR API to spectate matches.
Credit to @bust in the EchoVR Discord server for the original program, which can be found [here](https://github.com/qlyoung/echovr-replay/blob/master/replay2d/replay.py).

# USAGE

To run the program as an .exe file, download the Source Code.zip from Releases and run the .exe file within it.

**The config file is required and must be in the same directory**

# Changes

Changes from original by @bust:
- Now reads from the API instead of a saved match.
- Shows height of players and disc using a varying white to black circle
- Moved possession indicator to the outside of the player circle
- Disc outlined in white so height indicator doesn't make it invisible sometimes
- Stuns will cause the stunned player to flash
- Changed goals to appear where the goal actually is when the size of the window changes
- Host player displays as purple
- Added midfield lines
- Probably something else that I forgot...

Planned changes:
- 3 point circle or disc changes color when inside 3 point sphere
