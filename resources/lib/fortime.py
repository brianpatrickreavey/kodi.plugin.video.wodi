import time
import xbmcgui  # type: ignore
import xbmcaddon  # type: ignore
import xbmc  # type: ignore

from resources.lib.base_timer import BaseTimerWindow

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')

class TIMEWindow(BaseTimerWindow):
    window_title = "FOR TIME - Stopwatch Mode"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.countdown = False  # Stopwatch counts up

    def onInit(self, *args, **kwargs):
        super().onInit(*args, **kwargs)

        # Hide setup button for stopwatch mode
        self.setup_button.setVisible(False)
        self.setup_button.setEnabled(False)

        self.update_timer_label()

    def onClick(self, controlId):
        self.log(f"onClick called with controlId={controlId}")
        super().onClick(controlId)

    def run_timer(self):
        start_time = time.time() - self.elapsed
        # To play countdown at start:
        self.play_countdown()
        while self.running:
            now = time.time()
            self.elapsed = now - start_time
            self.update_timer_label(now=now)
            ms = int((now * 1000) % 1000)
            sleep_ms = 500 - (ms % 500)
            xbmc.sleep(sleep_ms)
        self.running = False
