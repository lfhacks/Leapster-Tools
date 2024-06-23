#A script that aims to accurately parse the LeapFrog AppTable ("RIB") header format and extract assets
import struct
import tkinter as tk #Used to kill the extra tkinter window
import os
from tkinter import filedialog
root = tk.Tk()#Create a root window
root.withdraw()#Hide the root window
files = filedialog.askopenfilenames()
root.destroy()#Destroy the root window
def createTXTH(path):
    with open(path+".bin.TXTH", "w+") as txthGen:
        txthGen.write(txth)

def getString_(file, offset): #Gets any 0 terminated string at any given offset. Useful for stuff like title info.
    string = ""
    scan = b'99'
    with open(file, "rb") as rom:
        rom.seek(offset)
        while scan != b'\x00':
            scan = rom.read(1)
            if scan != b'\x00':
                string = string+scan.decode("UTF-8")
    return string

def getRAW(file, offset, end_offset, deviceStartAddress):
    RAW_size = end_offset-offset
    with open(file, "rb") as rom:
        rom.seek(offset)
        RAW = rom.read(RAW_size)
    return RAW

def getLPC(file, offset, deviceStartAddress): #Incomplete!
    lpcEndCheck = b'\xC0'
    continueScanning = True
    with open(file, "rb") as rom:
        rom.seek(offset)
        outData = b''
        while continueScanning == True:
            data = rom.read(1)
            outData = outData+data
            if data == lpcEndCheck:
                data2 = rom.read(1)
                outData = outData+data2
                if data2 == b'\x0F':
                    continueScanning == False
                    break
                else:
                    "" #Keep going
    return outData

def getSYN(file, offset, deviceStartAddress):
    trackEndCheck = b'\xFF'
    hits = 0
    with open(file, "rb") as rom:
        rom.seek(offset)
        SYN = rom.read(4)
        header, tracks = struct.unpack("<HH",SYN)
        while hits != tracks:
            readForCheck = rom.read(1)
            SYN = SYN+readForCheck
            if readForCheck == trackEndCheck:
                SYN = SYN+rom.read(1) #Be sure to add the extra 0 so this SYN file is complete
                hits+=1
    return SYN

def getSWF(file, offset, deviceStartAddress):
    with open(file, "rb") as rom:
        rom.seek(offset)
        FWS, size = struct.unpack("<II",rom.read(8))
        rom.seek(-8, 1)
        SWF = rom.read(size)
    return SWF

def getSample(file, start_offset, end_offset, loop_start, loop_end, ID, sample, paths):
    with open(file, "rb") as rom:
        rom.seek(start_offset)
        data = b''
        length = end_offset-start_offset
        for byte in range(length):
            sound_byte = rom.read(1)
            data = data+sound_byte
        return data
    
def parseInstrumentInfo(file, offset, deviceStartAddress, ID): #Parse the actual instrument data
    fullInstrument = []
    end_note = 0x1
    last_note = 0
    sample_start = 0x9999
    sample = 0
    data_Final = b''
    with open(f"{paths[2]}Instrument_{ID}_Samples.bin", "w+b") as samples:
        with open(f"{paths[2]}Instrument_{ID}_Info.txt", "w+") as doc:
            with open(file, "rb") as rom:
                rom.seek(offset)
                while sample_start in range(0x300,0xFFFFFF): #I need to figure out how the pitch works before actually converting anything
                    sample_start = struct.unpack("<I",rom.read(4))[0]-deviceStartAddress
                    sample_end = struct.unpack("<I",rom.read(4))[0]-deviceStartAddress+1
                    loop_start = struct.unpack("<H",rom.read(2))[0]
                    loop_end = struct.unpack("<H",rom.read(2))[0]
                    pitchBytes = rom.read(4)
                    pitch = struct.unpack("<I",pitchBytes)[0]
                    start_note = rom.read(1)[0]
                    end_note = rom.read(1)[0]
                    decay_rate = struct.unpack("<H",rom.read(2))[0]
                    if sample_start in range(0x300,0xFFFFFF):
                        instrument = [sample_start,sample_end,loop_start,loop_end,pitch,start_note,end_note,decay_rate]
                        fullSample = getSample(file, sample_start, sample_end, loop_start, loop_end, ID, sample, paths)
                        samples.write(fullSample)
                        data_Final = data_Final + fullSample  
                        instrumentInfo = f"Sample ID - {sample}\nSample Start - {hex(sample_start)}\nSample End - {hex(sample_end)}\nLoop Start - {hex(loop_start)}\nLoop End - {hex(loop_end)}\nPitch - {hex(pitch)}\nStart Note - {hex(start_note)}\nEnd Note - {hex(end_note)}\nDecay Rate - {hex(decay_rate)}\n\n"
                        doc.write(instrumentInfo)
                    if end_note == 0x7F: #End of instrument, break free from the loop
                        break
    fullInstrument.append(instrument)

    return fullInstrument

def parseInstrumentTable(file, offset, deviceStartAddress): #Parse the instrument table
    with open(file, "rb") as rom:
        rom.seek(offset+0x8)
        initialHandleValue = struct.unpack("<I",rom.read(4))[0]
        instrument_count = struct.unpack("<I",rom.read(4))[0]
        instruments = []
        for pointer in range(int(instrument_count)): #Get the offsets of the instruments
            instrument_offset = struct.unpack("<I",rom.read(4))[0]-deviceStartAddress
            #rom.seek(-4,1)
            if instrument_offset+deviceStartAddress != 0: #Pointers that are just 0 are placeholders
                instrument = parseInstrumentInfo(file, instrument_offset, deviceStartAddress, pointer) #The "pointer" variable is used as the ID
                instruments.append(instrument)
        return instruments

def parseRawTable(file, offset, deviceStartAddress): #Parse the RAW table
    with open(file, "rb") as rom:
        rom.seek(offset+0x8)
        initialHandleValue = struct.unpack("<I",rom.read(4))[0]
        raw_count = struct.unpack("<I",rom.read(4))[0]
        for pointer in range(int(raw_count)): #Get the offsets of the RAW files
            raw_offset = struct.unpack("<I",rom.read(4))[0]-deviceStartAddress
            raw_offset_2 = struct.unpack("<I",rom.read(4))[0]-deviceStartAddress
            RAW = getRAW(file, raw_offset, raw_offset_2, deviceStartAddress)
            with open(f"{paths[4]}RAW_{pointer}.bin", "w+b") as raw:
                raw.write(RAW)

def parseLpcTable(file, offset, deviceStartAddress): #Parse the LPC table
    with open(file, "rb") as rom:
        rom.seek(offset+0x8)
        initialHandleValue = struct.unpack("<I",rom.read(4))[0]
        lpc_count = struct.unpack("<I",rom.read(4))[0]
        for pointer in range(int(lpc_count)): #Get the offsets of the LPC files
            lpc_offset = struct.unpack("<I",rom.read(4))[0]-deviceStartAddress
            LPC = getLPC(file, lpc_offset, deviceStartAddress)
            with open(f"{paths[3]}LPC_{pointer+initialHandleValue}.bin", "w+b") as lpc:
                lpc.write(LPC)
                
def parseSynTable(file, offset, deviceStartAddress): #Parse the SYN table
    with open(file, "rb") as rom:
        rom.seek(offset+0x8)
        initialHandleValue = struct.unpack("<I",rom.read(4))[0]
        syn_count = struct.unpack("<I",rom.read(4))[0]
        for pointer in range(int(syn_count)): #Get the offsets of the SYN files
            syn_offset = struct.unpack("<I",rom.read(4))[0]-deviceStartAddress
            SYN = getSYN(file, syn_offset, deviceStartAddress)
            with open(f"{paths[5]}SYN_{pointer+initialHandleValue}.bin", "w+b") as syn:
                syn.write(SYN)

def parseSwfTable(file, offset, deviceStartAddress): #Parse the SWF table
    with open(file, "rb") as rom:
        rom.seek(offset+0x8)
        initialHandleValue = struct.unpack("<I",rom.read(4))[0]
        swf_count = struct.unpack("<I",rom.read(4))[0]
        for pointer in range(int(swf_count)): #Get the offsets of the SWF files
            swf_offset = struct.unpack("<I",rom.read(4))[0]-deviceStartAddress
            SWF = getSWF(file, swf_offset, deviceStartAddress)
            with open(f"{paths[7]}{pointer+initialHandleValue}.swf", "w+b") as swf:
                swf.write(SWF)

def parsePegBitmapTable(file, offset, deviceStartAddress): #Parse the PEG Bitmap table
    with open(file, "rb") as rom:
        rom.seek(offset+0x8)
        initialHandleValue = struct.unpack("<I",rom.read(4))[0]
        bitmap_count = struct.unpack("<I",rom.read(4))[0]
        for pointer in range(int(bitmap_count)): #Get the offsets of the Bitmap files
            bitmap_offset = struct.unpack("<I",rom.read(4))[0]-deviceStartAddress
            Bitmap = getBitmap(file, bitmap_offset, deviceStartAddress)
            with open(f"{paths[8]}Bitmap_{pointer+initialHandleValue}.bmp", "w+b") as bitmap:
                bitmap.write(Bitmap)

def parseChorusRIBTable(file): #The ROM info starts here.
    with open(file, "rb") as rom:
        rom.seek(0x100) #Seek to "Copyright LeapFrog     "
        signature = rom.read(0x17).decode("UTF-8")
        rom.read(1) #There's 1 extra byte that isn't text here (it's always 00 though)
        if signature == "Copyright LeapFrog     ":
            ChorusRIBTableMinorVersion = rom.read(1)
            ChorusRIBTableMajorVersion = rom.read(1)
            ribCount = struct.unpack("<H", rom.read(2))[0]
            deviceStartAddress = struct.unpack("<I", rom.read(4))[0] #Use this as the ROM base offset (where in memory the ROM is mapped to)
            deviceEndAddress = struct.unpack("<I", rom.read(4))[0]
            pFullChecksum = struct.unpack("<I", rom.read(4))[0]
            pSparseChecksum = struct.unpack("<I", rom.read(4))[0]
            pBootSafeFcnTable = struct.unpack("<I", rom.read(4))[0] #Fcn stands for function and this is the real name for this variable before anyone makes any jokes about this.
            reserved0 = rom.read(4)
            reserved1 = rom.read(4)
            reserved2 = rom.read(4)
            reserved3 = rom.read(4)
            ribTable = struct.unpack("<I", rom.read(4))[0] #Where the "LEAP" (actual RIB) table starts
            print(f"ROM info:\nDevice start address: {deviceStartAddress}\nDevice end address: {deviceEndAddress}\n")
        else:
            print("Not a Leapster ROM.")
            quit()
        return deviceStartAddress, ribTable

def parseRIB(file, deviceStartAddress, ribTable): #Using the information obtained from parseRIBTable, parse the RIB. I don't know what RIB stands for yet, so don't ask what it means.
    with open(file, "rb") as rom:
        rom.seek(ribTable-deviceStartAddress)
        signature = rom.read(4).decode("UTF-8")
        if signature == "LEAP":
            RIBMinorVersion = rom.read(1)
            RIBMajorVersion = rom.read(1)
            resourceGroupCount = struct.unpack("<H", rom.read(2))[0]
            reserved0 = rom.read(4)
            reserved1 = rom.read(4)
            reserved2 = rom.read(4)
            reserved3 = rom.read(4)
            reserved4 = rom.read(4)
            reserved5 = rom.read(4)
            for resource in range(resourceGroupCount):
                RIB_Group_ID = struct.unpack("<H", rom.read(2))[0]
                #print(hex(rom.tell()), hex(RIB_Group_ID))

                if RIB_Group_ID == 0x1000: #Boot
                    bootCount = struct.unpack("<H", rom.read(2))[0]
                    bootOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    
                elif RIB_Group_ID == 0x1001: #Modules
                    moduleCount = struct.unpack("<H", rom.read(2))[0]
                    moduleOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    
                elif RIB_Group_ID == 0x1003: #Product info group
                    productInfoCount = struct.unpack("<H", rom.read(2))[0]
                    productInfoOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    parseProductInfo(file, deviceStartAddress, productInfoOffset, productInfoCount)
                    
                elif RIB_Group_ID == 0x1005: #"Group"
                    groupCount = struct.unpack("<H", rom.read(2))[0]
                    groupOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    
                elif RIB_Group_ID == 0x1006: #Asset group
                    assetTableCount = struct.unpack("<H", rom.read(2))[0]
                    assetTableOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    parseAssetTable(file, deviceStartAddress, assetTableOffset, assetTableCount)

                elif RIB_Group_ID == 0x1009: #Leapster System Apps
                    systemAppCount = struct.unpack("<H", rom.read(2))[0]
                    systemAppOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    
                elif RIB_Group_ID == 0x100C: #Leapster Datasets
                    datasetCount = struct.unpack("<H", rom.read(2))[0]
                    datasetOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress

                elif RIB_Group_ID == 0x100D: #C-Style Datasets
                    cDatasetCount = struct.unpack("<H", rom.read(2))[0]
                    cDatasetOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    
                elif RIB_Group_ID == 0x2000: #Leapster Apps
                    appCount = struct.unpack("<H", rom.read(2))[0]
                    appOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress

                elif RIB_Group_ID == 0x3001: #"Group"
                    groupCount = struct.unpack("<H", rom.read(2))[0]
                    groupOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress

                else: #Unknown group
                    print(f"This group ({hex(RIB_Group_ID)}) is undocumented and as a result, completely unknown.")
                    unknownCount = struct.unpack("<H", rom.read(2))[0]
                    unknownOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    
def parseProductInfo(file, deviceStartAddress, productInfoOffset, productInfoCount):
    with open(f"{paths[0]}Product info.txt", "w+") as ProductInfo:
        with open(file, "rb") as rom:
            rom.seek(productInfoOffset)
            for info in range(productInfoCount):
                infoID = struct.unpack("<H", rom.read(2))[0]
                infoMinorVersion = rom.read(1)
                infoMajorVersion = rom.read(1)
                if infoID == 1:
                    productID = struct.unpack("<I", rom.read(4))[0]
                    info = f"Product ID: {hex(productID)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 2:
                    neededProductIDs = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Needed product IDs offset: {hex(neededProductIDs)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 3:
                    providedProductIDs = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Provided product IDs offset: {hex(providedProductIDs)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 4:
                    Copyright = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Copyright offset: {hex(Copyright)}\nCopyright string: {getString_(file, Copyright)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 5:
                    Security = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Security offset: {hex(Security)}\nSecurity string: {getString_(file, Security)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 6:
                    baseSystemBoot = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Base System Boot offset: {hex(baseSystemBoot)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 7:
                    productVersion = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Product version: {hex(productVersion)}\nVersion: {getString_(file, productVersion)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 8:
                    ROMVersion = struct.unpack("<I", rom.read(4))[0]
                    info = f"ROM version: {hex(ROMVersion)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 0xA:
                    partNumber = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Part number offset: {hex(partNumber)}\nPart number: {getString_(file, partNumber)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 0xB:
                    partName = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Part name offset: {hex(partName)}\nPart name: {getString_(file, partNumber)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 0xC:
                    buildTool = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Build tool name offset: {hex(buildTool)}\nBuild tool name: {getString_(file, buildTool)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 0xD:
                    buildUserName = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Build user name offset: {hex(buildUserName)}\nBuild user name: {getString_(file, buildUserName)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 0xE:
                    buildMachineName = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Build machine name offset: {hex(buildMachineName)}\nBuild machine name: {getString_(file, buildMachineName)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 0xF:
                    dateAndTimestamp = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Date and Timestamp offset: {hex(dateAndTimestamp)}\nDate and Timestamp: {getString_(file, dateAndTimestamp)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                elif infoID == 0x10:
                    buildValidation = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                    info = f"Build Validation offset: {hex(buildValidation)}"
                    ProductInfo.write(info+'\n\n')
                    print(info)
                else:
                    rom.read(4)
                    print(f"This product info ({hex(infoID)}) is undocumented and as a result, completely unknown.")

def parseAssetTable(file, deviceStartAddress, assetTableOffset, assetTableCount):
    with open(file, "rb") as rom:
        rom.seek(assetTableOffset)
        for info in range(assetTableCount):
            infoID = struct.unpack("<H", rom.read(2))[0]
            infoMinorVersion = rom.read(1)
            infoMajorVersion = rom.read(1)
            if infoID == 1:
                fonts = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                print(f"Flash Player Fonts offset: {hex(fonts)}")
            elif infoID == 2:
                instrumentTable = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                print(f"Instrument Index Table offset: {hex(instrumentTable)}")
                parseInstrumentTable(file, instrumentTable, deviceStartAddress)
                createTXTH(paths[2])
            elif infoID == 3:
                gasTable = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                print(f"GAS Index Table offset: {hex(gasTable)}")
            elif infoID == 4:
                lpcTable = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                print(f"LPC Index Table offset: {hex(lpcTable)}")
                parseLpcTable(file, lpcTable, deviceStartAddress)
            elif infoID == 5:
                rawTable = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                print(f"RAW Index Table offset: {hex(rawTable)}")
                parseRawTable(file, rawTable, deviceStartAddress)
                createTXTH(paths[4])
            elif infoID == 6:
                synTable = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                print(f"SYN Index Table offset: {hex(synTable)}")
                parseSynTable(file, synTable, deviceStartAddress)
            elif infoID == 7:
                swfTable = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                print(f"SWF Index Table offset: {hex(swfTable)}")
                parseSwfTable(file, swfTable, deviceStartAddress)
            elif infoID == 9:
                pegBitmapTable = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                print(f"PEG Bitmap Index Table offset: {hex(pegBitmapTable)}")
            elif infoID == 0xD:
                flashBitmapTable = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                print(f"Flash Bitmap Index Table offset: {hex(flashBitmapTable)}")
            elif infoID == 0x10:
                cursorTable = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
                print(f"Cursor Index Table: {hex(cursorTable)}")
            else:
                rom.read(4)
                print(f"This asset type ({hex(infoID)}) is undocumented and as a result, completely unknown.")
                

#All variables used by the following function show up after it.
def leapParse(file, paths): #LeapFrog header parser
    deviceStartAddress, ribTable = parseChorusRIBTable(file)
    RIBContents = parseRIB(file, deviceStartAddress, ribTable)

for file in files:
    #The following contains every path we'll save files to when the script is ready.
    ROMName = os.path.basename(file).split(".")[0]
    paths = [os.getcwd()+f"/Split_ROMs/{ROMName}/",                  #Index = 0, root folder (title info goes here)
             os.getcwd()+f"/Split_ROMs/{ROMName}/Audio/GAS/",        #Index = 1, Audio GAS folder
             os.getcwd()+f"/Split_ROMs/{ROMName}/Audio/Instruments/",#Index = 2, Audio Instrument folder
             os.getcwd()+f"/Split_ROMs/{ROMName}/Audio/LPC/",        #Index = 3, Audio LPC/LFC folder
             os.getcwd()+f"/Split_ROMs/{ROMName}/Audio/RAW/",        #Index = 4, Audio RAW folder
             os.getcwd()+f"/Split_ROMs/{ROMName}/Audio/SYN/",        #Index = 5, Audio SYN folder
             os.getcwd()+f"/Split_ROMs/{ROMName}/Flash/Fonts/",      #Index = 6, Flash font folder
             os.getcwd()+f"/Split_ROMs/{ROMName}/Flash/SWF/",        #Index = 7, Flash SWF folder
             os.getcwd()+f"/Split_ROMs/{ROMName}/PEG/BMP/",          #Index = 8, PEG Bitmap folder
             ]
    txth = "codec = ALAW\nsample_rate = 8000\nchannels = 1\nstart_offset = 0\nnum_samples = data_size" #For creating the TXTH used for the instruments and sound effects
    for path in paths:
        if os.path.exists(path) == False:
            os.makedirs(path)
    leapParse(file, paths)
