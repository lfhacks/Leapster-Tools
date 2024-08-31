#Extracts the DPAK from a Torus Games ROM
import struct
def DPAKExtract(file, offset):
    files = []
    chunks = []
    headerPostTorus = b''#Holds the header data from after the "Torus" string
    dataChunks = b''     #Where the data chunks go
    completeDPAK = b''   #Where everything gets combined to
    with open(file, "rb") as rom:
        rom.seek(offset)
        identifier = rom.read(4)
        entries = rom.read(2)
        torus = rom.read(0xA)
        for entry in range(struct.unpack("<H", entries)[0]):
            chunkType = struct.unpack("<I", rom.read(4))[0]
            dataOffset = struct.unpack("<I", rom.read(4))[0]+offset
            dataSize = struct.unpack("<I", rom.read(4))[0]
            nothing = rom.read(4)
            headerPostTorus += struct.pack("<III", chunkType, dataOffset, dataSize)+nothing
            currentOffset = rom.tell()
            rom.seek(dataOffset)
            data = rom.read(dataSize)
            dataChunks += data
            files.append(data)
            chunks.append(chunkType)
            rom.seek(currentOffset)
    fullData = [identifier, entries, torus, headerPostTorus, dataChunks]
    
    for data in fullData:
        completeDPAK += data
    return files, chunks, completeDPAK
