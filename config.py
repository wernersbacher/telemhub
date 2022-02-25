import logging
from enum import Enum
import yaml

config = {}


# keys zur settings.yaml file
class Setting(Enum):
    REGISTRATION_ENABLED = ("REGISTRATION_ENABLED", True)
    MAX_UPLOAD_FILES = ("MAX_UPLOAD_FILES", 10)

    def __init__(self, key, def_val):
        self.key = key
        self.def_val = def_val


def loadConfig():
    global config
    print("Loading config...")
    try:  # try to open settings yaml
        with open("settings.yaml", 'r') as f:
            settings = yaml.safe_load(f)
    except FileNotFoundError:
        settings = {}

    # if none found, load example.
    # example will be overwritten on install, while settings.yaml won't.
    if not settings:
        logging.warning("settings.yaml file was not found or empty, using default values.")

    for s in Setting:
        # print(s.key, s.def_val)
        if s.key in settings:
            config[s.key] = settings[s.key]
        else:
            config[s.key] = s.def_val

loadConfig()

if __name__ == "__main__":
    #loadConfig()
    print(config)
