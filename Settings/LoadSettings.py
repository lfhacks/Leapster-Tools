def parseSettings(file, option):
    with open(file, "r") as settings:
        settingsList = settings.readlines()
        for setting in settingsList:
            if setting.startswith("?") == True:
                continue
            elif option in setting:
                value = int(setting.split("=")[1].split("_")[0])
                return value
