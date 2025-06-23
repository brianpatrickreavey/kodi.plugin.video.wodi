import xbmcgui  # type: ignore
import xbmcaddon  # type: ignore
import xbmc  # type: ignore
import threading
import time
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources/lib'))

from select_workout import WorkoutSelectWindow
from fortime import TIMEWindow
from amrap import AMRAPWindow
from emom import EMOMWindow
from tabata import TABATAWindow
from utils import log

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')

log("Starting WODI main loop")

if __name__ == "__main__":
    while True:
        select_window = WorkoutSelectWindow("WorkoutSelect.xml", ADDON_PATH, "default", "720p")
        select_window.doModal()
        selected = getattr(select_window, "selected", None)
        del select_window

        if selected == "time":
            window = TIMEWindow("WOD-UI.xml", ADDON_PATH, "default", "720p")
        elif selected == "amrap":
            window = AMRAPWindow("WOD-UI.xml", ADDON_PATH, "default", "720p")
        elif selected == "emom":
            window = EMOMWindow("WOD-UI.xml", ADDON_PATH, "default", "720p")
        elif selected == "tabata":
            window = TABATAWindow("WOD-UI.xml", ADDON_PATH, "default", "720p")
        else:
            break  # User cancelled or closed the selection window

        window.doModal()
        del window




