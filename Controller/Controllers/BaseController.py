import collections
import subprocess

from Controller.Controllers.SettingsController import SettingsController
from Controller.funcs import *

pyautogui.FAILSAFE = False

nexon_launch_target = "nxl://launch/10100"
steam_launch_target = "steam://rungameid/216150"

class BaseController(SettingsController):
    def __init__(self, settings_path, log_path='log.txt'):
        super().__init__(settings_path)
        clearlog(path=log_path)

        # Settings variables
        self.pause_key = self.get('pause', 'f5')
        self.install_origin = self.get('install_origin')

        # Default variables
        self.log_path = log_path
        self.frames = collections.deque(maxlen=600)
        self.cooldowns = {}

        # Keyboard events
        self.pause_state = False

        def onpause(e):
            self.pause_state = not self.pause_state
            log('Paused' if self.pause_state else 'Unpaused')
            print('Paused' if self.pause_state else 'Unpaused')

        keyboard.unhook_all()
        keyboard.on_release_key(self.pause_key, onpause)

    def grab_frame(self, focus=True):
        if self.get_status() == MapleState.ACTIVE:
            self.frame_pil, self.box = grab_maple(focus=(focus and not self.pause_state))
            self.frame_arr = np.asarray(self.frame_pil)
            self.frames.append(self.frame_arr)
            return self.frame_pil, self.frame_arr, self.box
        else:
            raise Exception('Unable to grab a screenshot from maplestory because maplestory isn\'t running.')

    def get_status(self):
        return get_maple_status()

    def launch_maple(self):
        launch_target = steam_launch_target if self.install_origin == 'steam' else nexon_launch_target
        subprocess.run("start {}".format(launch_target), shell=True)

    def close_maple(self):
        for process in psutil.process_iter():
            name = process.name().lower()
            if 'werfault' in name.lower() or 'maplestory' in name.lower():
                process.kill()

    def toggle_fullscreen(self):
        focus_maple()
        press_and_release('alt+enter')

    def focus_maple(self):
        focus_maple()

    def restart_cooldown(self, key):
        self.cooldowns[key] = time.time()

    def check_cooldown(self, key, cooldown):
        if cooldown == -1 or cooldown is None:
            return False
        if key in self.cooldowns:
            return True if time.time() - self.cooldowns[key] > cooldown else False
        else:
            return True
