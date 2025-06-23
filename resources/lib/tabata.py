import time
import xbmcgui  # type: ignore
import xbmcaddon  # type: ignore
import xbmc  # type: ignore

from resources.lib.base_timer import BaseTimerWindow, SETUP_ID

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')

class TABATAWindow(BaseTimerWindow):
    window_title = "TABATA - HIIT (Work/Rest Intervals)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        addon = xbmcaddon.Addon()
        # Read defaults from settings.xml
        self.rounds = int(addon.getSetting("tabata_rounds") or 8)
        self.work_seconds = int(addon.getSetting("tabata_work") or 20)
        self.rest_seconds = int(addon.getSetting("tabata_rest") or 10)
        self.countdown = True

    def onInit(self, *args, **kwargs):
        super().onInit(*args, **kwargs)
        # Set timer and lap timer to initial values based on settings
        total_seconds = self.rounds * (self.work_seconds + self.rest_seconds)
        self.update_timer_label(total_seconds)
        self.update_lap_timer_label(self.work_seconds)
        self.update_summary()

    def onClick(self, controlId):
        self.log(f"onClick called with controlId={controlId}")
        if controlId == SETUP_ID:  # Setup
            self.setup_tabata()
        else:
            super().onClick(controlId)

    def run_timer(self):
        start_time = time.time() - self.elapsed
        total_seconds = self.rounds * (self.work_seconds + self.rest_seconds)
        last_phase = None  # Track last phase to prevent double beep
        last_cycle = -1    # Track last cycle for accurate beeping

        while self.running:
            now = time.time()
            elapsed = now - start_time
            remaining = total_seconds - elapsed
            if remaining <= 0:
                self.update_timer_label(0, now=now)
                self.update_lap_timer_label(0, now=now, rest_phase=False)
                break

            # Calculate which phase we're in based on total elapsed time
            cycle_length = self.work_seconds + self.rest_seconds
            current_cycle = int(elapsed // cycle_length)
            cycle_elapsed = elapsed % cycle_length

            in_rest = cycle_elapsed >= self.work_seconds
            # Lap remaining time
            if in_rest:
                lap_remaining = self.rest_seconds - (cycle_elapsed - self.work_seconds)
            else:
                lap_remaining = self.work_seconds - cycle_elapsed

            # Update lap timer with correct color
            self.update_lap_timer_label(lap_remaining, now=now, rest_phase=in_rest)
            self.update_timer_label(remaining, now=now)

            # Only beep when phase changes
            phase = "rest" if in_rest else "work"
            if phase != last_phase:
                if last_phase is not None:  # Don't beep on very first loop
                    self.play_beep()
                last_phase = phase

            # Align to next 500ms boundary
            ms = int((now * 1000) % 1000)
            sleep_ms = 500 - (ms % 500)
            xbmc.sleep(sleep_ms)

        self.running = False

    def setup_tabata(self):
        self.log("setup_tabata called")
        self.running = False
        self.elapsed = 0.0
        dialog = xbmcgui.Dialog()
        rounds = dialog.numeric(0, "Number of rounds:", "")
        work = dialog.numeric(0, "Work seconds per round:", "")
        rest = dialog.numeric(0, "Rest seconds per round:", "")
        try:
            # Only update if the user entered something (not empty string)
            if rounds != "":
                self.rounds = int(rounds)
            if work != "":
                self.work_seconds = int(work)
            if rest != "":
                self.rest_seconds = int(rest)
            total_seconds = self.rounds * (self.work_seconds + self.rest_seconds)
            self.update_timer_label(total_seconds)
            self.update_lap_timer_label(self.work_seconds)
        except Exception:
            self.log("Invalid input for Tabata timer")
        self.update_summary()

    def update_summary(self):
        summary = (
            f"TABATA\n"
            f"Rounds: {self.rounds}\n"
            f"Work: {self.work_seconds}s  Rest: {self.rest_seconds}s"
        )
        self.text_area.setText(summary)