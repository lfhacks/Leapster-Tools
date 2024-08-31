import struct
from PIL import Image
import math

def readbgr555(file, offset, height):
    with open(file, 'rb') as f:
        f.seek(offset)
        paletteData = f.read(16*(height*2))
        print(16*(height))
    return paletteData

def bgr555toRGB(color):
    b = (color & 0b0111110000000000) >> 7
    g = (color & 0b0000001111100000) >> 2
    r = (color & 0b0000000000011111) << 3
    return (r, g, b)

def paletteToImage(paletteData, width, height):
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    for i in range(min(height*16, width * height)):
        color = struct.unpack('<H', paletteData[i*2:i*2+2])[0]
        rgb = bgr555toRGB(color)
        x = i % width
        y = i // width
        pixels[x, y] = rgb
    
    return img

def paletteConverter(file, offset, width, height):
    paletteData = readbgr555(file, offset, height)
    img = paletteToImage(paletteData, width, height)
    return img

def getPalette(file):
    with open(file, "rb") as f:
        f.seek(4)
        spriteCount = struct.unpack("<H", f.read(2))[0]
        paletteOffset = struct.unpack("<H", f.read(2))[0]
        spriteOffset = struct.unpack("<H", f.read(2))[0]
        width = 16
        f.seek(paletteOffset)
        height = struct.unpack("<I", f.read(4))[0]
        paletteOffset = paletteOffset+4
        image = paletteConverter(file, paletteOffset, width, height)
        return image
