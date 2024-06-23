import struct
import tkinter as tk
from tkinter import filedialog
import mido
import os

# Set up the tkinter file dialog
root = tk.Tk()
root.withdraw()
files = filedialog.askopenfilenames()
root.destroy()
currentTrack = 0
# Create a new MIDI file with one track

# Function to add MIDI messages to the track
def add_midi_message(message_type, channel, data1, data2, delta_time):
    global current_time
    if message_type == 'program_change':
        track.append(mido.Message('program_change', program=data1, channel=channel, time=delta_time))
    elif message_type == 'control_change':
        track.append(mido.Message('control_change', channel=channel, control=data1, value=data2, time=0))
    elif message_type == 'note_on':
        track.append(mido.Message('note_on', note=data1, velocity=data2, channel=channel, time=delta_time))
    elif message_type == 'note_off':
        track.append(mido.Message('note_off', note=data1, velocity=0, channel=channel, time=delta_time))
        
for file_path in files:
    mid = mido.MidiFile(type=1)
    with open(file_path, "rb") as syn:
        header, track_count = struct.unpack("<HH",syn.read(4))
        print(track_count)
        for synTrack in range(track_count):
            tracks = 0
            trackoffset, trackID = struct.unpack("<HH",syn.read(4))
            print(trackoffset)
            lastTrack = syn.tell()
            track = mido.MidiTrack()
            mid.tracks.append(track)
            track.append(mido.MetaMessage('set_tempo', tempo=10000))
            syn.seek(trackoffset)
            while True:
                
                data = syn.read(1)
                try:
                    if data[0] == 0x81: #PitchShift required.
                        add_midi_message('control_change', synTrack, 108, 0, 0)
                    if data[0] == 0x82: #PitchShift not required.
                        add_midi_message('control_change', synTrack, 106, 0, 0)
                    if data[0] == 0x83: #Reserve voice
                        add_midi_message('control_change', synTrack, 107, 0, 0)
                    if data[0] == 0x84: #Release voice
                        add_midi_message('control_change', synTrack, 109, 0, 0)
                
                    
                    if data[0] == 0x88: #Set volume
                        volume = syn.read(1)[0]
                        add_midi_message('control_change', synTrack, 7, volume, 0)
                    
                    if data[0] == 0x89: #Program change
                        instrument = syn.read(1)[0]
                        if instrument < 0x80:
                            add_midi_message('program_change', synTrack, instrument, None, 0)
                        else: #This SYN gets instruments from the cartridge instead (prefix 0xC0)
                            instrument = syn.read(1)[0]
                            add_midi_message('program_change', synTrack, instrument, None, 0)

                    if data[0] == 0x8A: #Pitch bend
                        break #Not implemented, will break the output and kill the conversion with an error anyways.
                            
                    if data[0] == 0x8E: #Start of loop
                        loopCount = syn.read(1)[0]
                        add_midi_message('control_change', synTrack, 110, loopCount, 0)
                        
                    if data[0] == 0x8F: #End of loop
                        zero = syn.read(1)[0]
                        add_midi_message('control_change', synTrack, 111, zero, 0)
                        
                    if data[0] in range(0x00, 0x7F):
                        note = data[0]
                        duration = syn.read(1)[0]
                        if duration == 0x80:
                            duration -= 0x7F
                            duration_2 = syn.read(1)[0]
                            duration += duration_2
                        elif duration >= 0x81:
                            duration -= 0x80
                            main = str(hex(duration))[2:3]
                            duration_2 = str(hex(syn.read(1)[0]))[2:4]
                            if len(duration_2) == 2:
                                duration = int(str("0x"+main+duration_2), 16)
                            else:
                                duration = int(str("0x"+main+"0"+duration_2), 16)
                        if note >= 1:
                            add_midi_message('note_on', synTrack, note, 127, 0)
                        add_midi_message('note_off', synTrack, note, 127, duration*200) #Now end the note

                    if data[0] == 0xFF: #End of sequence
                        break
                except:
                    if syn.tell() == os.path.getsize(file_path):
                        break
            syn.seek(lastTrack)
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_converted.mid"
        mid.save(output_path)
        print(f"Conversion complete! MIDI file saved as {output_path}")
