import re
import sys

import cv2

from Controller.MapleMoveMode import MapleMoveMode
from Controller.funcs import *
from Controller.Controllers.PotionsController import PotionsController
from Controller.Controllers.MovementController import MovementController


class PlayerController(MovementController, PotionsController):
    def __init__(self, settings_path, log_path='log.txt', resources_path="refs", deathsfolder='deaths'):
        PotionsController.__init__(self, settings_path, log_path=log_path)
        MovementController.__init__(self, settings_path, log_path=log_path, resources_path=resources_path)

        # Settings variables
        self.attack_key = self.get('attack')
        self.attack_interval = self.get('attack_interval', .25)
        self.attack_repeat = self.get('attack_repeat', 5)
        self.buffs_key = self.get('buffs', [])
        self.buffs_period = self.get('buffs_period', 50)
        self.buffs_interval = self.get('buffs_interval', .5)
        self.skills = self.get('skills', [])
        self.skills_interval = self.get('skills_interval', .25)
        self.spawn_skills = self.get('spawn_skills', [])
        self.spawn_skills_interval = self.get('spawn_skills_interval', .25)
        self.interact_key = self.get('interact', 'space')
        self.hyper_teleport_state = self.get('hyper_teleport', True)
        self.attempt_restart_after_crash_state = self.get('attempt_restart_after_crash', True)
        self.console_update_period = self.get('console_update_period', 60)

        # Default variables
        self.deaths = 0
        self.deathsfolder = deathsfolder

    def get_exp_precent(self):
        try:
            box = get_maple_windows()[0].box
            images = ["slash.png", "bracket.png"] + [str(i) + '.png' for i in range(10)]
            pyautogui.moveTo(box.left + 5, box.top + box.height - 5, _pause=False)
            self.grab_frame()
            img = Image.fromarray(self.frame_arr[-30:-5, 5:500])

            if locate(self.get_resource_path('EXP digits/exp.png'), img, confidence=.85):
                results = locate_all_multiple_images(img,
                                                     self.get_resource_path('EXP digits/'),
                                                     images,
                                                     confidence=.85,
                                                     key=lambda x: x[1].left)
                results = re.split('slash|bracket', ''.join(results[:, 0]))[:2]
                results = np.asarray(results, dtype=np.int64)
                exp, max_exp = results
                return exp / max_exp * 100
            else:
                return 0
        except:
            return 0

    def attack(self):
        log('Attacking')
        for i in range(self.attack_repeat):
            if self.pause_state or self.check_channel():
                break
            press_and_release(self.attack_key)
            self.check_direction_and_change()
            sleep(self.attack_interval)

    def interact(self):
        press_and_release(self.interact_key)

    def use_buffs(self):
        self.release_move()

        for key in self.buffs_key:
            if self.pause_state or self.check_channel():
                break
            self.check_health_and_heal()
            self.check_direction_and_change()
            sleep(self.buffs_interval)
            press_and_release(key)

        if self.move_mode == MapleMoveMode.HOLD:
            self.press_move()

    def use_skill(self, skill_settings):
        log('Using skill:' + str(skill_settings))
        for i in range(5):
            if self.pause_state:
                break
            press(skill_settings['key'])
            sleep(skill_settings.get('hold', .1) / 5)
        release(skill_settings['key'])

    def use_uncooldowned_skills(self):
        if any(self.check_cooldown(skill['key'], skill['period']) for skill in self.skills):
            sleep(0.75)  # Wait for any active animations to end
        for skill in self.skills:
            if self.pause_state or self.check_channel():
                break
            if self.check_cooldown(skill['key'], skill['period']):
                self.check_health_and_heal()
                self.check_direction_and_change()
                self.use_skill(skill)
                self.restart_cooldown(skill['key'])
                sleep(self.skills_interval)

    def use_spawn_skills(self):
        for skill in self.spawn_skills:
            self.use_skill(skill)
            sleep(self.spawn_skills_interval)

    def save_last_frames(self, path, fps=10, fourcc='H264'):
        fourcc = cv2.VideoWriter_fourcc(*fourcc)
        writer = cv2.VideoWriter(path, fourcc, fps, self.frames[0].shape[1::-1])

        for frame in self.frames:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            writer.write(frame)

        writer.release()

    def move_channel(self):
        while self.get_status() == MapleState.ACTIVE and not self.pause_state:
            # Make sure player wont die during channel change
            self.check_health_and_heal()

            if self.check_dead():
                log('Player died while trying to change channel')
                self.on_death()
                return False

            while self.check_no_potion_curse():
                if self.pause_state:
                    break
                self.check_direction_and_change()
                self.attack()
                sleep(.5)

            press_and_release('esc')
            sleep(.15)

            if self.check_settings_menu_open():
                log('Change channel - Settings menu opened')
                press_and_release('enter')
                sleep(.15)

                if self.check_ingame_channel_menu_open():
                    log('Change channel - Channel menu opened')
                    press_and_release('right')
                    sleep(.15)

                    # Make sure player wont die during channel change
                    if self.check_health():
                        log('Change channel - Heal')
                        press_and_release('esc')
                        self.attack()
                        self.heal()
                        sleep(.15)
                        continue

                    press_and_release('enter')
                    sleep(1)

                    if self.check_unable_change_channel_dialog_open():
                        log('Change channel - Unable to change channel dialog')
                        press_and_release('enter')
                        continue

                    # Random pixel turns black must mean success
                    # Or if all screen turned black
                    if self.check_black_screen():
                        log('Change channel - Successfully changed channel')
                        if self.move_mode == MapleMoveMode.HOLD:
                            self.check_direction_and_change()
                            self.press_move()

                        return True

    def attempt_rune(self):
        self.grab_frame()
        player = self.get_player_position(.8)
        rune = pyautogui.locate(self.get_resource_path("mini map/Rune.png"), self.frame_pil)

        if player and rune:  # If player and rune are visible in the minimap
            reached_rune = self.reach_rune()

            if reached_rune:
                # Maximum of 10 seconds to attempt activating the rune
                self.restart_cooldown('attempt rune')
                while not self.check_cooldown('attempt rune', 30) and not self.pause_state:
                    log('Moving towards rune - ' + str(abs(player.left - rune.left)) + 'px left')
                    self.check_health_and_heal()
                    self.release_move()
                    self.move()  # Move towards rune

                    activated = self.activate_rune(rune)
                    if activated:
                        log('Activated rune')
                    break

            self.unlock_move()
        return False

    def reach_rune(self):
        log('Attempting to reach rune')

        player = self.get_player_position()
        if not player:
            return False
        rune = pyautogui.locate(self.get_resource_path("mini map/Rune.png"), self.frame_pil)
        direction = -1 if player.left - rune.left > 0 else 1

        self.release_move()
        self.lock_move()
        self.set_move_direction(direction, force_mode=MapleMoveMode.HOLD)

        # Maximum of 10 seconds to reach rune x axis
        self.restart_cooldown('reach rune x axis')

        while not self.check_cooldown('reach rune x axis', 15) and not self.pause_state:
            self.check_health_and_heal()

            player = self.get_player_position()

            if not player:
                continue

            currentDirection = -1 if player.left - rune.left > 0 else 1

            if currentDirection == direction:
                self.press_move()
                if self.doublejump_state:
                    self.doublejump()
                    continue
            else:
                self.unlock_move()
                self.release_move()
                self.set_move_direction(currentDirection, force_mode=MapleMoveMode.HOLD)
                self.press_move()

                while not self.check_cooldown('reach rune x axis', 15) and not self.pause_state:
                    self.check_health_and_heal()
                    player = self.get_player_position()

                    if abs(player.left - rune.left) <= 3:
                        self.release_move()
                        break

            player = self.get_player_position()
            if player.top > rune.top:  # Player below rune
                while not self.check_cooldown('reach rune x axis', 15) and not self.pause_state:
                    self.check_health_and_heal()
                    player = self.get_player_position()

                    if not player:
                        continue

                    if rune.top - 3 <= player.top <= rune.top + 3:  # Check if player reached rune
                        return True

                    self.ascend()
                    sleep(.5)
            else:  # Player above rune
                while not self.check_cooldown('reach rune x axis', 15) and not self.pause_state:
                    self.check_health_and_heal()
                    player = self.get_player_position()

                    if not player:
                        continue

                    if rune.top - 3 <= player.top <= rune.top + 3:  # Check if player reached rune
                        return True

                    press_and_release(self.down_key + "+" + self.jump_key)
                    sleep(.5)

        return False

    def activate_rune(self, rune):
        log('Attempting to activate rune')

        # Help function
        def filter_rune_results(results):
            results = list(results)
            if len(results) == 0: return []
            current_result = results[0]
            yield (current_result[0], current_result[1].left)
            for result in results:
                if not (current_result[1].left - 10 <= result[1].left <= current_result[1].left + 10):
                    current_result = result
                    yield (current_result[0], current_result[1].left)

        player = self.get_player_position()

        if not player:
            return False
        elif rune.left - 3 <= player.left <= rune.left + 3:  # Check if player reached rune
            self.restart_cooldown('activate rune')
            while not self.check_cooldown('activate rune', 15) and not self.pause_state:
                sleep(1.5)
                self.interact()

                sleep(.5)
                self.grab_frame(focus=False)

                rune_keys_pil = self.frame_pil.crop((150, 150, 650, 400))
                keys = locate_all_multiple_images(rune_keys_pil,
                                                  self.get_resource_path('rune keys/'),
                                                  ["Up.png", "Down.png", "Right.png", "Left.png"],
                                                  confidence=.7,
                                                  key=lambda x: x[1].left)

                keys = list(filter_rune_results(keys))

                if len(keys) == 0:
                    return True

                for key, x in keys:
                    press_and_release(key)
                    sleep(.25)

            return False

    def mark_world_map_location(self):
        self.focus_maple()
        if not self.check_world_map_open():
            self.open_world_map()
            sleep(.5)
        self.grab_frame(focus=False)
        if self.check_world_map_open():
            mark = locate(self.get_resource_path('map/Location mark.png'), self.frame_pil, confidence=.85)
            self.open_world_map()  # Press world map key to close it
            sleep(.5)
            return mark

    def teleport_to_mark(self, mark):
        if mark:
            self.focus_maple()
            self.open_world_map()
            sleep(.5)
            for i in range(10):
                pyautogui.doubleClick(self.box.left + mark.left + mark.width // 2,
                                      self.box.top + mark.top + mark.height + i, duration=1 / 3)
                if self.check_world_map_teleport_message():
                    press_and_release('enter')
                    return True
                elif self.check_missing_hyper_message():
                    return False
        return False

    def on_death(self, save_vid=True):
        log('Player died, saving death video')
        if save_vid:
            if not os.path.exists(self.deathsfolder):
                os.makedirs(self.deathsfolder)
            self.save_last_frames(
                self.deathsfolder + '\\' + datetime.datetime.now().strftime("%m-%d-%Y %H-%M-%S") + '.mp4')
        self.deaths += 1
        if self.hyper_teleport_state:
            sleep(2)
            mark = self.mark_world_map_location()
            sleep(1)
            self.click_ok_button()
            sleep(5)
            self.check_health_and_heal()
            if mark:
                if self.teleport_to_mark(mark):
                    sleep(3)
                    self.use_spawn_skills()
                else:
                    raise Exception('Faild respawning after death')
        else:
            sys.exit()

controller = PlayerController("Shade Settings.json", resources_path="../Controller/refs")
