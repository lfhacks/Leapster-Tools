# Leapster-Tools
A replacement for LeapFrog-Tools with an end goal of having the highest accuracy possible with each tool. This repository is only for the Leapster, Leapster TV, Leapster L-Max and Leapster 2!


# LeapSplit
Currently, LeapSplit only extracts the following:
- Product info (stuff like the name, version number, compiler name and build date)
- Instruments (don't ask how to use these! I don't know yet due to the pitch format being unknown) (not all games have unique instruments in them, so don't expect there to be instruments in every game you run this on)
- RAW audio (the A-Law stuff you can find by opening the ROMs in audacity)
- LPC audio (the codec is unknown and the extraction code is incomplete. There's more to the format than just ending on C00F.)
- SYN sequences (the music format used on the Leapster)
- SWF files (the Flash files used for stuff like cutscenes and gameplay in a ton of games)

How to use LeapSplit:
- Double click the script
- Navigate to and double click your ROM
- Dig through the assets that have been extracted from your ROM (should be in {script folder}/Split_ROMs/{game name}/)

How to open the bin files in the Instruments and RAW folders:
- Get Foobar2000.
- Get the VGMStream plugin.
- Go to file -> preferences -> playback -> decoding -> vgmstream
- Check if the "Enable unknown exts" and "Enable common exts" options are enabled. If not, enable them and hit "Apply"
- You can now drag and drop the bin files into Foobar2000 for playback and conversion.

This will not work on the bin files in the LPC folder! Those use an unknown, custom codec that has yet to be reverse engineered.

# LF SYN to MIDI
This (work in progress) script converts SYN files to MIDI files. Anything that uses command 0x82 *will* desync!

How to use LF SYN to MIDI:
- Be sure mido is installed (run "pip install mido")
- Double click the script
- Navigate to your SYN files
- Select them all and hit enter or the "open" button

Known errors (in other words, do not report these bugs. They're already known!)
- Some SYN files make the script lock up during conversion
- Some tracks (mainly those that use command 0x82) will start at the wrong time
- The converted MIDIs are a bit slower than what would play on an actual Leapster
- Anything with pitch bends breaks or stops converting early
