import struct
import tkinter as tk
try:
    import mido
except:
    import GetDepends #If the import fails, import the GetDepends script to get everything
    import mido

import os
currentTrack = 0
# Function to add MIDI messages to the track


def convertSYN(file, path, loadedLoopCount, pitchBendStrength):
    if loadedLoopCount > 127: #This is where the cap mentioned in the settings file is implemented.
        loadedLoopCount = 127
    track = mido.MidiTrack()
    def add_midi_message(message_type, channel, data1, data2, delta_time):
        if message_type == 'program_change':
            track.append(mido.Message('program_change', program=data1, channel=channel, time=delta_time))
        elif message_type == 'control_change':
            track.append(mido.Message('control_change', channel=channel, control=data1, value=data2, time=0))
        elif message_type == 'note_on':
            track.append(mido.Message('note_on', note=data1, velocity=data2, channel=channel, time=delta_time))
        elif message_type == 'note_off':
            track.append(mido.Message('note_off', note=data1, velocity=0, channel=channel, time=delta_time))
        elif message_type == 'pitch_wheel':
            track.append(mido.Message('pitchwheel', channel=channel, pitch=data1, time=delta_time))
        elif message_type == 'set_range':
            track.append(mido.Message('control_change', control=101, value=0, channel=channel, time=0))
            track.append(mido.Message('control_change', control=100, value=0, channel=channel, time=0))
            track.append(mido.Message('control_change', control=6, value=data1, channel=channel, time=0))
            track.append(mido.Message('control_change', control=38, value=data2, channel=channel, time=0))
    mid = mido.MidiFile(type=1)
    with open(file, "rb") as syn:
        header, track_count = struct.unpack("<HH",syn.read(4))
        currentSynTrack = 0
        track = mido.MidiTrack()#This track is exclusively for the tempo
        track.append(mido.MetaMessage('set_tempo', tempo=1925000))
        mid.tracks.append(track)
        for synTrack in range(track_count):
            
            lastDuration = -1 #Store the last note duration here
            lastNote = -1     #Store the last note here
            tracks = 0
            trackoffset, trackID = struct.unpack("<HH",syn.read(4))
            lastTrack = syn.tell()
            track = mido.MidiTrack()
            mid.tracks.append(track)
            syn.seek(trackoffset)
            currentSynTrack += 1
            current_bend = 0
            volume = 127
            hasLoop = False
            hasLoopEnd = False
            if currentSynTrack == 9: #The bothersome "percussion" channel must be stopped. It has ruined countless lives and - oh, wait. I can just skip it.
                currentSynTrack += 1
            while True:
                data = syn.read(1)
                if len(data) == 0:
                    break
                if data[0] == 0x81: #PitchShift required.
                    add_midi_message('control_change', currentSynTrack, 108, 0, 0)
                if data[0] == 0x82: #PitchShift not required.
                    add_midi_message('control_change', currentSynTrack, 106, 0, 0)
                if data[0] == 0x83: #Reserve voice
                    add_midi_message('control_change', currentSynTrack, 107, 0, 0)
                if data[0] == 0x84: #Release voice
                    add_midi_message('control_change', currentSynTrack, 109, 0, 0)
            
                
                if data[0] == 0x88: #Set volume
                    volume = syn.read(1)[0]
                
                if data[0] == 0x89: #Program change
                    instrument = syn.read(1)[0]
                    if instrument < 0x80:
                        add_midi_message('program_change', currentSynTrack, instrument, None, 0)
                    else: #This SYN gets instruments from the cartridge instead (prefix 0xC0)
                        instrument = syn.read(1)[0]
                        add_midi_message('program_change', currentSynTrack, instrument, None, 0)

                if data[0] == 0x8A: #Pitch bend
                    bend = struct.unpack("<B", syn.read(1))[0]
                    duration = syn.read(1)[0]
                    if duration >= 0x80 and duration < 0xFF:
                        duration -= 0x80
                        if duration <= 0xF:
                            main = str(hex(duration))[2:3]
                        else:
                            main = str(hex(duration))[2:4]
                        duration_2 = str(hex(syn.read(1)[0]))[2:4]
                        
                        if len(duration_2) == 2:
                            duration = int(str("0x"+main+duration_2), 16)
                        else:
                            duration = int(str("0x"+main+"0"+duration_2), 16)
                    current_bend = (bend-127)*64
                    
                    #print(current_bend)
                    #input()
                    if current_bend > 8192 or current_bend < -8191:
                        print(current_bend)
                        current_bend =0
                    add_midi_message('pitch_wheel', currentSynTrack, current_bend, 127, duration)
                    


                if data[0] == 0x8E: #Start of loop
                    loopCount = syn.read(1)[0]
                    hasLoop = True #Loop points are now added after the previous note ends to ensure that they're timed right
                    loopPoint = syn.tell()
                    
                    loops = loadedLoopCount #Change this to make the MIDIs loop a certain amount of times (disable looping in Foobar first though! These are done by parsing the entire track again.)
                    try:
                        if instrument < 0x80:
                            add_midi_message('program_change', currentSynTrack, instrument, None, 0)
                        else: #This SYN gets instruments from the cartridge instead (prefix 0xC0)
                            instrument = syn.read(1)[0]
                            add_midi_message('program_change', currentSynTrack, instrument, None, 0)
                    except:
                        "" #Instrument value not assigned yet.
                    
                if data[0] == 0x8F: #End of loop
                    zero = syn.read(1)[0]
                    if loops >= 1:
                        syn.seek(loopPoint)
                        loops -= 1
                    hasLoopEnd = True #Loop points are now added after the previous note ends to ensure that they're timed right
                    
                if data[0] in range(0x00, 0x7F):
                    note = data[0]
                    duration = syn.read(1)[0]
                    current_bend = 0 #Reset the pitch bend for every note (mainly because figuring out how they work is still a work in progress)
                    if duration >= 0x80 and duration < 0xFF:
                        duration -= 0x80
                        if duration <= 0xF:
                            main = str(hex(duration))[2:3]
                        else:
                            main = str(hex(duration))[2:4]
                        duration_2 = str(hex(syn.read(1)[0]))[2:4]
                        
                        if len(duration_2) == 2:
                            duration = int(str("0x"+main+duration_2), 16)
                        else:
                            duration = int(str("0x"+main+"0"+duration_2), 16)
                    if lastDuration != -1:
                        add_midi_message('note_off', currentSynTrack, lastNote, volume, lastDuration) #Now end the note
                        if hasLoop == True:
                            add_midi_message('control_change', currentSynTrack, 110, loopCount, 0)
                            hasLoop = False
                    if note >= 1:
                        add_midi_message('note_on', currentSynTrack, note, volume, 0) #Start the note
                    
                    
                    lastDuration = duration
                    lastNote = note

                if data[0] == 0xFF: #End of sequence
                    add_midi_message('note_off', currentSynTrack, lastNote, 127, lastDuration)
                    if hasLoopEnd == True:
                        add_midi_message('control_change', currentSynTrack, 111, zero, 0)
                        hasLoopEnd = False
                    break
            add_midi_message('set_range', channel=currentSynTrack, data1=pitchBendStrength, data2=0, delta_time=0)
            syn.seek(lastTrack)
        base, ext = os.path.splitext(file)
        base = base.split("/")[-1]
        base = base.split("\\")[-1] #In case the last one does nothing
        output_path = f"{base}_converted.mid"
        mid.save(path+base+".mid")
        #print(f"Converted MIDI file saved as {path+base}.mid")
