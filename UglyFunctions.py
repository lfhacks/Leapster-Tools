#Any functions that take up too much space, are janky or need cleaning will go here.
import struct
import os
global file

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
    instrumentKey = 90-round((pitchValue - 0x41a72f8a)/0xB5000)
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
