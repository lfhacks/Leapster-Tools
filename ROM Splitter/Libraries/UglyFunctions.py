#Any functions that take up too much space, are janky or need cleaning will go here.
import struct
import os
global file
import numpy as np
from numpy.polynomial.polynomial import Polynomial

integers = np.array([0x4414f209, #33
                     1136371934, #41
                     0x437a7eb7, #48
                     1128714604, #52
                     1127983326, #53
                     1127293072, #54
                     0x42fa7eb7, #60
                     1120326036, #64
                     1117637974, #68
                     1115992599, #71
                     0x427a7ed6, #72
                     1108121083, #82
                     1107603973, #83
                     1106014128, #85
                     ])
keys = np.array([33,41,48,52,53,54,60,64,68,71,72,82,83,85
                 ])
p = Polynomial.fit(integers, keys, 2)

def lfPitchToKey(pitch):
    key = p(pitch)
    if pitch == 1123712695:
        key = 60
    return key

def getString(file, offset): #Gets any 0 terminated string at any given offset. Useful for stuff like title info.
    string = ""
    scan = b'99'
    with open(file, "rb") as rom:
        rom.seek(offset)
        while scan != b'\x00':
            scan = rom.read(1)
            if scan != b'\x00':
                string = string+scan.decode("UTF-8")
    return string

def convertPitch(pitchValue): #A function for converting the Leapster's pitch format to notes (needs more research)
    instrumentKey = lfPitchToKey(pitchValue)
    return instrumentKey
    

def getModuleInfo(file, offset, deviceStartAddress, paths): #Needs to be cleaned and documented better.
    moduleInfo = "Name:\n"
    with open(file, "rb") as rom:
        rom.seek(offset)
        count = rom.read(4)[2]
        rom.seek(8, 1)
        print(count)
        nameOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
        moduleOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
        functionCount1, functionCount2 = struct.unpack("<HH", rom.read(4))
        offsets = "\nCurrently undefined code offsets:\n"
        moduleOffset1 = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
        moduleOffset2 = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
        rom.seek(moduleOffset1)
        for function in range(functionCount1): #Get first set of addresses
            functionOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
            if functionOffset > 0:
                functionOffset = str(hex(functionOffset))
                offsets += functionOffset+"\n"
        rom.seek(moduleOffset2)
        for function in range(functionCount2): #Get second set of addresses
            functionOffset = struct.unpack("<I", rom.read(4))[0]-deviceStartAddress
            if functionOffset > 0:
                functionOffset = str(hex(functionOffset))
                offsets += functionOffset+"\n"   
        rom.seek(nameOffset)
        moduleName = getString(file, nameOffset)
        moduleExtra = getString(file, moduleOffset)
        print(moduleExtra)
        
            
        moduleInfo += f"{moduleName}\nDescription:\n{moduleExtra}\n{offsets}\n\n"
    return moduleInfo

def parseModuleSubTable(file, offset, deviceStartAddress, paths): #Parse the module index table (specifically for names)
    with open(file, "rb") as rom:
        rom.seek(offset)
        versionNumber = rom.read(2)
        module_count = struct.unpack("<H",rom.read(2))[0]
        rom.seek(8, 1)
        with open(f"{paths[0]}Modules.txt", "w+") as modules:
            modules.write(f"Start offset of module table:\n"+str(hex(offset))+"\n\n")
            for pointer in range(int(module_count)): #Get the offsets of the modules
                module_offset = struct.unpack("<I",rom.read(4))[0]-deviceStartAddress
                Module = getModuleInfo(file, module_offset, deviceStartAddress, paths)
                modules.write(Module)
                
def parseModuleTable(file, offset, deviceStartAddress, paths): #Parse the module RIB table
    with open(file, "rb") as rom:
        rom.seek(offset)
        module_count = struct.unpack("<I",rom.read(4))[0]
        for pointer in range(int(module_count)):
            module_offset = struct.unpack("<I",rom.read(4))[0]-deviceStartAddress
            parseModuleSubTable(file, module_offset, deviceStartAddress, paths)
