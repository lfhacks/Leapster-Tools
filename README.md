# Leapster-Tools
A replacement for LeapFrog-Tools with an end goal of having the highest accuracy possible with each tool. This repository is only for the Leapster, Leapster TV, Leapster L-Max and Leapster 2!

Feel free to reimplement, borrow or use this documentation for your own research and tools.

# LeapSplit
Currently, LeapSplit only extracts the following:
- Product info (stuff like the name, version number, compiler name and build date)
- Instruments (don't ask how to use these! I don't know yet due to the pitch format being unknown) (not all games have unique instruments in them, so don't expect there to be instruments in every game you run this on)
- RAW audio (the A-Law stuff you can find by opening the ROMs in audacity)
- LPC audio (the codec is unknown and the extraction code is incomplete. There's more to the format than just ending on C00F.) (Used to be known as LFC before the Batman source code released)
- SYN sequences (the music format used on the Leapster)
- SWF files (the Flash files used for stuff like cutscenes and gameplay in a ton of games)

How to use LeapSplit:
- Double click the script
- Navigate to and double click your ROM
- Dig through the assets that have been extracted from your ROM (should be in {script folder}/Split_ROMs/{game name}/)

How to open the bin files in the Instruments and RAW folders:
- Get Foobar2000 (the latest version is preferred).
- Get the VGMStream plugin.
- Go to file -> preferences -> playback -> decoding -> vgmstream
- Check if the "Enable unknown exts" and "Enable common exts" options are enabled. If not, enable them and hit "Apply"
- You can now drag and drop the bin files into Foobar2000 for playback and conversion.

This will not work on the bin files in the LPC folder! Those use an unknown, custom codec that has yet to be reverse engineered.

Known issues with LeapSplit:
- A few ROMs make the script throw an error
- LPC extraction is incomplete and the format still needs to be figured out

# LF SYN to MIDI
This script converts SYN files to MIDI files. It's near-perfect now, but the implementation of pitch bends and volume commands could use some work.

How to use LF SYN to MIDI:
- Be sure mido is installed (run "pip install mido")
- Double click the script
- Navigate to your SYN files
- Select them all and hit enter or the "open" button

Known errors (in other words, do not report these bugs. They're already known!)
- Pitch bends are a bit janky
- Volume commands start a bit late, making some stuff sound off

If you try to play these with Foobar2000, use this plugin since it natively supports LeapFrog looping information:

https://github.com/stuerp/foo_midi

If the plugin crashes on the 64-Bit version or fails to install, get the 32-Bit version of Foobar. All important settings are in File > preferences > Playback > Decoding > MIDI Player. The best plugin for this is BASSMIDI, as it supports soundfonts.

Foobar download page:

https://www.foobar2000.org/download

Incomplete (but usable) Leapster soundfont:

[Latest Trash-Font.zip](https://github.com/user-attachments/files/16256546/Latest.Trash-Font.zip)

While all instruments are mapped to the right preset numbers, not all of them hake their root keys mapped right yet. Some are also game-specific and need to be removed and put into their own soundfonts in the future.
