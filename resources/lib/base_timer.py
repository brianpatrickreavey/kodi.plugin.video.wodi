import math
import threading
import time
import xbmcgui    # type: ignore
import xbmc       # type: ignore
import xbmcaddon  # type: ignore
import xbmcvfs  # Add this import at the top with the others
from resources.lib.utils import log as global_log

START_STOP_ID = 100
RESET_ID = 101
SETUP_ID = 102
TEXT_AREA_ID = 200

SEVEN_SEGMENT_BASE = "special://home/addons/plugin.video.wodi/resources/media/seven_segment_display"
MAIN_COLOR = "red"
LAP_WORK_COLOR = "red"
LAP_REST_COLOR = "green"

class BaseTimerWindow(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = False
        self.timer_thread = None
        self.start_time = None
        self.elapsed = 0.0
        self.countdown = False # Default to "Time" mode
        self.countdown_seconds = 0
        self.lap_countdown_seconds = 0
        self.start_stop_button = None
        self.reset_button = None
        self.setup_button = None
        self.text_area = None
        self.cancelled = False

    def onInit(self, *args, **kwargs):
        self.start_stop_button = self.getControl(START_STOP_ID)
        self.reset_button = self.getControl(RESET_ID)
        self.setup_button = self.getControl(SETUP_ID)
        self.text_area = self.getControl(TEXT_AREA_ID)
        self.update_timer_label()
        # Set the window title if defined
        if hasattr(self, "window_title") and self.window_title:
            self.text_area.setText(self.window_title)

    def start_timer(self):
        self.running = True
        self.start_time = time.time() - self.elapsed
        # Play workout playlist if enabled
        addon = xbmcaddon.Addon()
        if addon.getSettingBool("enable_workout_playlist"):
            playlist_name = addon.getSetting("workout_playlist") or "workout.m3u"
            shuffle = addon.getSettingBool("shuffle_workout_playlist")
            playlist_path = xbmcvfs.translatePath(f"special://profile/playlists/music/{playlist_name}")
            self.play_playlist(playlist_path, shuffle)
        self.timer_thread = threading.Thread(target=self.run_timer)
        self.timer_thread.start()

    def pause_timer(self):
        """Pause the timer, keeping elapsed time for resume."""
        self.running = False
        if self.start_time:
            self.elapsed = time.time() - self.start_time

    def stop_timer(self):
        """Completely stop and reset the timer."""
        self.running = False
        self.elapsed = 0.0
        self.update_timer_label(self.countdown_seconds)
        self.update_lap_timer_label(remaining=None)
        # Only play timesup SFX if not cancelled
        if not getattr(self, "cancelled", False):
            self.log("Timer stopped, stopping music and playing timesup sound")
            xbmc.Player().stop()  # Stop any playing music
            self.play_timesup()
            xbmc.sleep(5000)  # Wait for SFX to finish before scontinuing
        # Play cooldown playlist if enabled
        addon = xbmcaddon.Addon()
        if addon.getSettingBool("enable_cooldown_playlist"):
            playlist_name = addon.getSetting("cooldown_playlist") or "cooldown.m3u"
            shuffle = addon.getSettingBool("shuffle_cooldown_playlist")
            playlist_path = xbmcvfs.translatePath(f"special://profile/playlists/music/{playlist_name}")
            self.play_playlist(playlist_path, shuffle)
        self.cancelled = False  # Reset for next run

    def reset_timer(self):
        self.running = False
        self.elapsed = 0.0
        self.update_timer_label(self.countdown_seconds)

    def update_timer_label(self, remaining=None, now=None):
        if now is None:
            now = time.time()
        ms = int((now * 1000) % 1000)

        # Always show colon if timer hasn't started yet (elapsed == 0)
        if (not self.running and self.elapsed == 0.0) or remaining is None:
            colon_display = True
        else:
            colon_display = ms < 500

        if self.countdown and remaining is not None:
            if remaining < 0:
                remaining = 0
            mins, secs = divmod(math.ceil(remaining), 60)
        else:
            if self.running:
                elapsed = now - self.start_time
            else:
                elapsed = self.elapsed
            mins, secs = divmod(int(elapsed), 60)

        min1, min2 = divmod(mins, 10)
        sec1, sec2 = divmod(secs, 10)

        self.getControl(10).setImage(f"{SEVEN_SEGMENT_BASE}/{MAIN_COLOR}/{min1}.png")
        self.getControl(11).setImage(f"{SEVEN_SEGMENT_BASE}/{MAIN_COLOR}/{min2}.png")
        if colon_display:
            self.getControl(12).setImage(f"{SEVEN_SEGMENT_BASE}/{MAIN_COLOR}/colon.png")
        else:
            self.getControl(12).setImage(f"{SEVEN_SEGMENT_BASE}/blank_colon.png")
        self.getControl(13).setImage(f"{SEVEN_SEGMENT_BASE}/{MAIN_COLOR}/{sec1}.png")
        self.getControl(14).setImage(f"{SEVEN_SEGMENT_BASE}/{MAIN_COLOR}/{sec2}.png")

    def update_lap_timer_label(self, remaining=None, now=None, rest_phase=False):
        if now is None:
            now = time.time()
        ms = int((now * 1000) % 1000)
        # Always show colon if timer hasn't started yet (elapsed == 0) or remaining is None
        if (not self.running and self.elapsed == 0.0) or remaining is None:
            colon_display = True
        else:
            colon_display = ms < 500

        # Choose color directory for digits
        color = LAP_REST_COLOR if rest_phase else LAP_WORK_COLOR

        if remaining is not None:
            if remaining < 0:
                remaining = 0
            mins, secs = divmod(math.ceil(remaining), 60)
            min1, min2 = divmod(mins, 10)
            sec1, sec2 = divmod(secs, 10)
        else:
            min1 = min2 = sec1 = sec2 = 0

        self.getControl(20).setImage(f"{SEVEN_SEGMENT_BASE}/{color}/{min1}.png")
        self.getControl(21).setImage(f"{SEVEN_SEGMENT_BASE}/{color}/{min2}.png")
        if colon_display:
            self.getControl(22).setImage(f"{SEVEN_SEGMENT_BASE}/{color}/colon.png")
        else:
            self.getControl(22).setImage(f"{SEVEN_SEGMENT_BASE}/blank_colon.png")
        self.getControl(23).setImage(f"{SEVEN_SEGMENT_BASE}/{color}/{sec1}.png")
        self.getControl(24).setImage(f"{SEVEN_SEGMENT_BASE}/{color}/{sec2}.png")

    def start_with_countdown(self):
        """Play countdown sound and start timer when ready."""
        self.log(f"start_with_countdown called, elapsed={self.elapsed}")
        if self.elapsed == 0.0:
            self.log("Playing countdown sound")
            self.play_countdown()
        else:
            self.log("Skipping countdown sound, timer already started")
        self.start_stop_button.setLabel("Stop")
        self.start_timer()
        xbmc.sleep(50)  # On start, wait a bit to ensure the timer is running before updating the label

    def play_sound(self, filename):
        xbmc.playSFX(filename)

    def play_countdown(self):
        self.play_sound("special://home/addons/plugin.video.wodi/resources/media/countdown.wav")
        xbmc.sleep(3450)

    def play_beep(self):
        self.play_sound("special://home/addons/plugin.video.wodi/resources/media/beep.wav")

    def play_timesup(self):
        self.play_sound("special://home/addons/plugin.video.wodi/resources/media/timesup.wav")

    def onClick(self, controlId):
        if controlId == START_STOP_ID:  # Pause/Resume
            if not self.running:
                self.start_with_countdown()
                self.start_stop_button.setLabel("Pause")
            else:
                self.pause_timer()
                self.start_stop_button.setLabel("Resume")
        elif controlId == RESET_ID:  # Stop/Reset
            self.stop_timer()
            self.start_stop_button.setLabel("Start")
        # "Setup" and other workout-specific controls should be handled in the subclass

    def onAction(self, action):
        if action.getId() in (9, 10, 92):  # Back/Escape
            if self.running:
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Exit Workout?", "The timer is still running. Exit and stop the workout?"):
                    self.cancelled = True
                    self.running = False
                    self.close()
            else:
                self.close()
        else:
            super().onAction(action)

    def play_playlist(self, playlist_path, shuffle=True):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        playlist.clear()
        playlist.load(playlist_path)
        if shuffle and playlist.size() > 1:
            playlist.shuffle()
        if playlist.size() > 0:
            xbmc.Player().play(playlist)

    def log(self, msg, level="INFO"):
        global_log(msg, level)

