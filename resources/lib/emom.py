import time
import xbmcgui  # type: ignore
import xbmcaddon  # type: ignore
import xbmc  # type: ignore

from resources.lib.base_timer import BaseTimerWindow, SETUP_ID

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')

class EMOMWindow(BaseTimerWindow):
    window_title = "EMOM - Every Minute On the Minute"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        addon = xbmcaddon.Addon()
        self.countdown = True # EMOM is a countdown-style timer
        self.countdown_seconds = int(addon.getSetting("emom_total_minutes") or 20) * 60
        self.lap_countdown_seconds = int(addon.getSetting("emom_lap_minutes") or 1) * 60

    def onInit(self, *args, **kwargs):
        super().onInit(*args, **kwargs)
        # Pass the correct initial values
        self.update_timer_label(self.countdown_seconds)
        self.update_lap_timer_label(self.lap_countdown_seconds)
        self.update_summary()

    def onClick(self, controlId):
        self.log(f"onClick called with controlId={controlId}")
        if controlId == SETUP_ID:
            self.setup_emom()
        else:
            super().onClick(controlId)

    def run_timer(self):
        start_time = time.time() - self.elapsed
        lap_start = start_time
        last_lap = -1
        while self.running:
            now = time.time()
            self.elapsed = now - start_time
            remaining = self.countdown_seconds - self.elapsed

            # Lap/interval logic
            lap_elapsed = now - lap_start
            current_lap = int(lap_elapsed // self.lap_countdown_seconds)
            lap_remaining = self.lap_countdown_seconds - (lap_elapsed % self.lap_countdown_seconds)
            if remaining <= 0:
                self.update_timer_label(0, now=now)
                self.update_lap_timer_label(0, now=now)
                break
            self.update_timer_label(remaining, now=now)
            self.update_lap_timer_label(lap_remaining, now=now)
            if current_lap > last_lap and current_lap != 0:
                self.play_beep()
                last_lap = current_lap
            ms = int((now * 1000) % 1000)
            sleep_ms = 500 - (ms % 500)
            xbmc.sleep(sleep_ms)
        self.running = False
        self.update_timer_label()

    def setup_emom(self):
        self.log("setup_emom called")
        self.running = False
        self.elapsed = 0.0
        dialog = xbmcgui.Dialog()
        mins = dialog.numeric(0, "Length of EMOM (minutes):", "")
        lap_mins = dialog.numeric(0, "Length of each lap (minutes):", "")
        try:
            if mins != "":
                self.countdown_seconds = int(mins) * 60
            if lap_mins != "":
                self.lap_countdown_seconds = int(lap_mins) * 60
            self.countdown = True
            self.update_timer_label(self.countdown_seconds)
            self.update_lap_timer_label(self.lap_countdown_seconds)
        except Exception:
            self.log("Invalid input for EMOM timer")
        self.update_summary()

    # Example for EMOM
    def update_summary(self):
        mins = self.countdown_seconds // 60
        lap = self.lap_countdown_seconds // 60
        summary = f"EMOM\nEvery Minute On the Minute\n{mins} min total, {lap} min per round"
        self.text_area.setText(summary)