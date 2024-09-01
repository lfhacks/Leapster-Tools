import subprocess
import os
import sys
print("Python"+sys.version.split(".")[0]+sys.version.split(".")[1])
version = sys.version.split(".")[0]+sys.version.split(".")[1]
username = os.getenv("USERNAME") #Needed for the alternative method if pip wasn't added to PATH
print(username)
def install_package(package_name):
    try:
        subprocess.check_call(['pip', 'install', package_name])
        print(f"Successfully installed {package_name}")
    except:
        print(f"Error installing {package_name}. Trying alternative method (Windows only!)")
        
        try:
            subprocess.check_call([f'C:/users/{username}/AppData/Local/Programs/Python/Python{version}/Scripts/pip.exe', 'install', package_name])
            print(f"Successfully installed {package_name}")
        except:
            print(f"Error installing {package_name}. There's either no version available for your OS/Python version or you installed Python in a location that isn't the default one.")

install_package('mido')    #For handling music (sequences)
install_package('g711')    #For handling audio (the A-Law stuff) (I would use a built in library, but audioop was depricated for whatever reason and that's the only one I know of that does this stuff correctly)
install_package('pillow')  #For handling graphics
install_package('numpy')   #Needed for some math-related stuff
install_package('scipy')   #Used for the WAV conversion
