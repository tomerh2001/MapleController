from Controller.Controllers.GameController import GameController
from Controller.MapleMoveMode import MapleMoveMode
from Controller.funcs import *


class MovementController(GameController):
    def __init__(self, settings_path, log_path='log.txt', resources_path="refs"):
        super().__init__(settings_path, log_path=log_path, resources_path=resources_path)

        self.move_mode = self.get('move_mode', 'hold')
        self.right_key = self.get('right')
        self.left_key = self.get('left')
        self.up_key = self.get('up')
        self.down_key = self.get('down')
        self.jump_key = self.get('jump', None)
        self.doublejump_state = self.get('doublejump', True)
        self.ascend_key = self.get('ascend', None)
        self.ascend_period = self.get('ascend_period', -1)
        self.hold_up_state = self.get('hold_up', True)
        self.direction_period = self.get('change_direction_period', 10)
        self.smart_direction_state = self.get('smart_direction', True)

        # Load TELEPORT settings
        if self.move_mode == MapleMoveMode.TELEPORT:
            self.teleport_up_period = self.get('teleport_up_period', 10)
            self.teleport_down_period = self.get('teleport_down_period', 30)
            self.teleport_up_key = self.get('teleport_up')
            self.teleport_down_key = self.get('teleport_down')
            self.teleport_right_key = self.get('teleport_right')
            self.teleport_left_key = self.get('teleport_left')
            self.hold_up_state = False

        if self.smart_direction_state:
            self.direction_period = 0

        # Default variables
        self.move_key = self.teleport_right_key if self.move_mode == MapleMoveMode.TELEPORT else self.right_key
        self.move_locked = False
        self.moving = False

    def jump(self):
        press_and_release(self.jump_key)

    def doublejump(self):
        press_and_release(self.jump_key, repeat=2)

    def press_right(self):
        press(self.right_key)

    def release_right(self):
        release(self.right_key)

    def right(self):
        press_and_release(self.right_key)

    def press_left(self):
        press(self.left_key)

    def release_left(self):
        release(self.left_key)

    def left(self):
        press_and_release(self.left_key)

    def press_up(self):
        press(self.up_key)

    def release_up(self):
        release(self.up_key)

    def up(self):
        press_and_release(self.up_key)

    def press_down(self):
        press(self.down_key)

    def release_down(self):
        release(self.down_key)

    def down(self):
        press_and_release(self.down_key)

    def teleport_right(self):
        press_and_release(self.teleport_right_key)

    def teleport_left(self):
        press_and_release(self.teleport_left_key)

    def teleport_up(self):
        press_and_release(self.teleport_up_key)

    def teleport_down(self):
        press_and_release(self.teleport_down_key)

    def press_move(self):
        press(self.move_key)
        self.moving = True

    def release_move(self):
        self.focus_maple()
        release(self.move_key)
        self.moving = False

    def move(self):
        self.moving = True
        press_and_release(self.move_key)
        self.moving = False

    def toggle_move_direction(self):
        if self.move_mode == MapleMoveMode.HOLD:
            self.move_key = self.left_key if self.move_key == self.right_key else self.right_key
        elif self.move_mode == MapleMoveMode.TELEPORT:
            self.move_key = self.teleport_left_key if self.move_key == self.teleport_right_key else self.teleport_right_key

    def set_move_direction(self, direction_num, force_mode=None):
        if abs(direction_num) != 1:
            return
        elif self.move_mode == MapleMoveMode.HOLD or force_mode == MapleMoveMode.HOLD:
            self.move_key = self.left_key if direction_num == -1 else self.right_key
        elif self.move_mode == MapleMoveMode.TELEPORT or force_mode == MapleMoveMode.TELEPORT:
            self.move_key = self.teleport_left_key if direction_num == -1 else self.teleport_right_key

    def change_move_direction(self):
        if self.smart_direction_state:
            direction = self.get_smart_direction()
            self.set_move_direction(direction)
        else:
            self.toggle_move_direction()

    def lock_move(self):
        self.move_locked = True

    def unlock_move(self):
        self.move_locked = False

    def is_move_locked(self):
        return self.move_locked

    def check_direction_and_change(self):
        if self.check_cooldown("change_direction", self.direction_period) and not self.is_move_locked():
            self.change_direction()
            self.restart_cooldown("change_direction")

    def change_direction(self):
        moving = self.moving
        if moving and self.move_mode == MapleMoveMode.HOLD:
            self.release_move()
        self.change_move_direction()
        if moving and self.move_mode == MapleMoveMode.HOLD:
            self.press_move()

    def get_smart_direction(self, winPrecent=.5):
        button = self.get_npc_button()
        if not button:
            button = self.get_world_button()

        max_left = button.left + button.width + 10
        center_left = max_left // 2
        win_size = round(center_left * winPrecent)
        xMin, xMax = center_left - win_size, center_left + win_size

        try:
            player_left = self.get_player_position().left
            if player_left < xMin:
                return 1
            elif player_left > xMax:
                return -1
            else:
                return 0
        except:
            return np.random.choice([-1, 1])

    def ascend(self):
        press_and_release(self.ascend_key)

    def jump_or_doublejump(self):
        if self.doublejump_state:
            self.doublejump()
        else:
            self.jump()

controller = MovementController("Shade Settings.json", resources_path="../Controller/refs")
