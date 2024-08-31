import os
import struct

try:
    import numpy as np
    from scipy.io import wavfile
    from g711 import * 
except:
    import GetDepends #If the import fails, import the GetDepends script to get everything this relies on (including mido)
    import numpy as np
    from scipy.io import wavfile
    from g711 import *
    
def ALAWtoWAV_Instrument(alaw_file, loop_start, loop_end, output_path):
    v3 = alaw_file
    alaw_audio = load_alaw(v3)
    pcm_audio = (alaw_audio * 32767).astype(np.int16)
    sample_rate, num_channels, bits_per_sample = 8000, 1, 16
    loop_size = loop_end-loop_start
    loop_end = int(len(pcm_audio))
    loop_start = loop_end-loop_size #How loops work is a work in progress here... They appear to directly map to the A-Law data, but using them in the output WAV files doesn't work because the resulting numbers are way too large.
    packedLoopInfo = struct.pack("<i", int(loop_start))+struct.pack("<i", int(loop_end))
    byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
    block_align = num_channels * (bits_per_sample // 8)
    wavfile.write(output_path, sample_rate, pcm_audio)
    with open(output_path, "ab") as wav:
        wav.write(b'\x73\x6D\x70\x6C\x3C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x48\xE8\x01\x00\x3C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'+
                  packedLoopInfo+b'\x00\x00\x00\x00\x00\x00\x00\x00')
    with open(output_path, "r+b") as wav:
        wav.seek(4)
        size = struct.pack("<I", os.path.getsize(output_path)-8)
        wav.write(size)

def ALAWtoWAV_SFX(alaw_file, output_path):
    v3 = alaw_file
    alaw_audio = load_alaw(v3)
    pcm_audio = (alaw_audio * 32767).astype(np.int16)
    sample_rate, num_channels, bits_per_sample = 8000, 1, 16
    byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
    block_align = num_channels * (bits_per_sample // 8)
    wavfile.write(output_path, sample_rate, pcm_audio)
    with open(output_path, "r+b") as wav:
        wav.seek(4)
        size = struct.pack("<I", os.path.getsize(output_path)-8)
        wav.write(size)
