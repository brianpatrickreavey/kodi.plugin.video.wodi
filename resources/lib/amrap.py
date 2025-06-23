import math
import threading
import time
import xbmcgui  # type: ignore
import xbmcaddon  # type: ignore
import xbmc  # type: ignore
import os
import sys

from base_timer import BaseTimerWindow, SETUP_ID

class AMRAPWindow(BaseTimerWindow):
    window_title = "AMRAP - As Many Rounds/Reps As Possible"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        addon = xbmcaddon.Addon()
        self.countdown = True
        self.countdown_seconds = int(addon.getSetting("amrap_minutes") or 20) * 60

    def onInit(self, *args, **kwargs):
        super().onInit(*args, **kwargs)
        self.update_timer_label(self.countdown_seconds)
        self.update_summary()

    def onClick(self, controlId):
        self.log(f"onClick called with controlId={controlId}")
        if controlId == SETUP_ID:  # Setup
            self.setup_amrap()
        else:
            super().onClick(controlId)

    def run_timer(self):
        start_time = time.time() - self.elapsed  # Adjust for paused time
        while self.running:
            now = time.time()
            self.elapsed = now - start_time
            remaining = self.countdown_seconds - self.elapsed
            if remaining <= 0:
                self.update_timer_label(0, now=now)
                break
            self.update_timer_label(remaining, now=now)

            # Align to next 500ms boundary
            ms = int((now * 1000) % 1000)
            sleep_ms = 500 - (ms % 500)
            xbmc.sleep(sleep_ms)
        self.running = False

        # Only play ending logic if not cancelled
        if not getattr(self, "cancelled", False):
            self.stop_timer()

    def setup_amrap(self):
        self.log("setup_amrap called")
        self.running = False
        self.elapsed = 0.0
        dialog = xbmcgui.Dialog()
        mins = dialog.numeric(0, "Length of AMRAP (minutes):", "")
        try:
            if mins != "":
                self.countdown_seconds = int(mins) * 60
            self.update_timer_label(self.countdown_seconds)
        except Exception:
            self.log("Invalid input for AMRAP timer")
        self.update_summary()

    def update_summary(self):
        mins = self.countdown_seconds // 60
        summary = f"AMRAP\nAs Many Rounds/Reps As Possible\n{mins} min"
        self.text_area.setText(summary)


