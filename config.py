import logging
from enum import Enum
import yaml
import time

config = {}
lastCheck = 0

RELOAD_TIME = 60  # in seconds, update every hour


# keys zur settings.yaml file
class Setting(Enum):
    REGISTRATION_ENABLED = ("REGISTRATION_ENABLED", True)
    MAX_UPLOAD_FILES = ("MAX_UPLOAD_FILES", 10)

    def __init__(self, key, def_val):
        self.key = key
        self.def_val = def_val


def loadConfig(force=False):
    global config
    if config and not force:
        return
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

def get(setting):
    global config

    refreshConfig()

    if setting.key in config:
        return config[setting.key]
    return 0


def refreshConfig():
    """ refreshes config if too old """
    global lastCheck
    now = time.time()
    if lastCheck + RELOAD_TIME < now:
        loadConfig(force=True)
        lastCheck = now


loadConfig()

if __name__ == "__main__":
    #loadConfig()
    print(config)
