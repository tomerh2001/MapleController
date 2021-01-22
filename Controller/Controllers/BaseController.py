import collections

from Controller.Controllers.SettingsController import SettingsController
from Controller.funcs import *


class BaseController(SettingsController):
    def __init__(self, settings_path, logpath='log.txt'):
        super().__init__(settings_path)
        clearlog(path=logpath)

        # Settings fields
        self.pause_key = self.get('pause', 'f5')

        # Default fields
        self.logpath = logpath
        self.frames = collections.deque(maxlen=600)

        # Keyboard events
        self.pause_state = False

        def onpause(e):
            self.pause_state = not self.pause_state
            log('Paused' if self.pause_state else 'Unpaused')

        keyboard.on_press_key(self.pause_key, onpause)

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
