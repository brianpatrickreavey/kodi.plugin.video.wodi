import xbmcgui # type: ignore
import xbmcaddon # type:ignore
from utils import log

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')

class WorkoutSelectWindow(xbmcgui.WindowXML):
    def onInit(self):
        log("WorkoutSelectWindow initialized")
        self.getControl(100).setLabel("FOR TIME")
        self.getControl(101).setLabel("AMRAP")
        self.getControl(102).setLabel("EMOM")
        self.getControl(103).setLabel("TABATA")
        self.setFocusId(100)

    def onClick(self, controlId):
        log(f"WorkoutSelectWindow onClick: controlId={controlId}")
        if controlId == 100:
            self.selected = "time"
            self.close()
        elif controlId == 101:
            self.selected = "amrap"
            self.close()
        elif controlId == 102:
            self.selected = "emom"
            self.close()
        elif controlId == 103:
            self.selected = "tabata"
            self.close()