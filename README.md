# Leapster-Tools
A replacement for LeapFrog-Tools with an end goal of having the highest accuracy possible with each tool. This repository is only for the Leapster, Leapster TV, Leapster L-Max and Leapster 2!

Feel free to reimplement, borrow or use this documentation for your own research and tools.

# LeapSplit
### How to use LeapSplit
- Double click the "LeapSplit" script
- Navigate to and double click your ROM
- Dig through the assets that have been extracted from your ROM (should be in {script folder}/Split_ROMs/{game name}/)

If the GetDepends script fails to grab all of the libraries for you (the thing that opens CMD windows the first time you run the script), you'll need to install them yourself (or you're on Linux. A fix for that is planned when this is more complete.)

Needed libraries:
- g711 (for A-Law encoded audio)
- mido (for the SYN to MIDI conversions)
- pillow (for extracting palettes from games made by Torus and the eventual extraction of sprites)
- scipy (for the WAV conversions)
- numpy (used alongside scipy)

### Known issues with LeapSplit
- Pitch bends aren't properly implemented in the SYN to MIDI script
- First-time setup can be a bit annoying thanks to the g711 library not being pre-compiled
- LPC extraction is incomplete and the format still needs to be figured out
- It either doesn't work on Linux or needs a ton of workarounds to get it working on Linux

Foobar download page:

https://www.foobar2000.org/download

Get the official MIDI plugin from the Foobar2000 website, as looping is handled better in the script than it was in the updated foo_midi plugin.

Incomplete (but usable) Leapster soundfont:

Latest Leap-Font rip update:
[LeapFrog Leap-Font.zip](https://github.com/user-attachments/files/18633090/LeapFrog.Leap-Font.zip)



While all instruments are mapped to the right preset numbers, not all of them have their root keys mapped right yet. Some are also game-specific and need to be removed and put into their own soundfonts in the future.

Be sure to go to the settings, load the Leapster SF2 and change the interpolation mode to linear interpolation! Any other interpolation mode is inaccurate to the hardware.

(The hardware only makes it sound interpolated because the Leap-Font sound driver caps the audio output to 8000Hz. The hardware itself is able to go up to 12000Hz.)

# Additional information
[Work in progress Leapster documentation](https://gist.github.com/BLiNXthetimesweeperGOD/cc98ea1ddb439c886f1921a7fb9312ba)
