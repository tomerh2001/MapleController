import collections
import itertools
import json
import re
import shutil
import subprocess
import sys
import cv2
from Controller.MapleState import MapleState
from Controller.MapleMoveMode import MapleMoveMode
from Controller.funcs import *

pyautogui.FAILSAFE = False

nexon_launch_target = "nxl://launch/10100"
steam_launch_target = "steam://rungameid/216150"


class MapleController:
    def __init__(self, settings, logpath='log.txt', deathsfolder='deaths'):
        # Clear deaths folder
        if os.path.exists(deathsfolder):
            shutil.rmtree(deathsfolder)
            os.makedirs(deathsfolder)

        # Load settings.json
        self.move_mode = settings.get('move_mode', 'hold')
        self.jump_key = settings.get('jump', None)
        self.right_key = settings['right']
        self.left_key = settings['left']
        self.up_key = settings['up']
        self.down_key = settings['down']
        self.interact_key = settings.get('interact', 'space')
        self.ascend_key = settings.get('ascend', None)
        self.ascend_period = settings.get('ascend_period', -1)
        self.hold_up_state = settings.get('hold_up', True)
        self.world_map_key = settings.get('world_map', 'w')
        self.direction_period = settings.get('change_direction_period', 10)
        self.smart_direction_state = settings.get('smart_direction', True)
        self.doublejump_state = settings.get('doublejump', True)
        self.channel_period = settings.get('change_channel_period', 600)
        self.attack_key = settings['attack']
        self.attack_interval = settings.get('attack_interval', .25)
        self.attack_repeat = settings.get('attack_repeat', 5)
        self.buffs_key = settings.get('buffs', [])
        self.buffs_period = settings.get('buffs_period', 50)
        self.buffs_interval = settings.get('buffs_interval', .5)
        self.skills = settings.get('skills', [])
        self.skills_interval = settings.get('skills_interval', .25)
        self.spawn_skills = settings.get('spawn_skills', [])
        self.spawn_skills_interval = settings.get('spawn_skills_interval', .25)
        self.install_origin = settings['install_origin']
        self.world = settings['world']
        self.PIC = settings['PIC']
        self.attempt_restart_after_crash_state = settings.get('attempt_restart_after_crash', True)
        self.hyper_teleport_state = settings.get('hyper_teleport', True)
        self.console_update_period = settings.get('console_update_period', 60)

        # Load TELEPORT settings
        if self.move_mode == MapleMoveMode.TELEPORT:
            self.teleport_up_period = settings.get('teleport_up_period', 10)
            self.teleport_down_period = settings.get('teleport_down_period', 30)
            self.teleport_up_key = settings['teleport_up']
            self.teleport_down_key = settings['teleport_down']
            self.teleport_right_key = settings['teleport_right']
            self.teleport_left_key = settings['teleport_left']
            self.hold_up_state = False

        if self.smart_direction_state:
            self.direction_period = 0

        # Default variables
        self.cooldowns = {}
        self.move_key = self.teleport_right_key if self.move_mode == MapleMoveMode.TELEPORT else self.right_key
        self.move_locked = False
        self.deaths = 0
        self.deathsfolder = deathsfolder

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

    def select_world(self, world, channel=1):
        self.grab_frame()
        if self.check_world_menu_open():
            if not locate_on_screen("refs/worlds/{}.png".format(world)):
                self.grab_frame()
                press_and_release('up')
                sleep(.25)
                press_and_release('up')
                sleep(.25)
            if locate_on_screen_and_click("refs/worlds/{}.png".format(world), duration=1):
                sleep(.5)
                if self.check_world_menu_channels_menu_open():
                    for i in range(channel - 1):
                        press_and_release('right')
                        sleep(.3)
                    press_and_release('enter')
                    sleep(1)
                else:
                    raise Exception('Faild selecting world {}, channels menu was not detected.'.format(world))
            else:
                raise Exception('Faild selecting world {}, world button was not detected.'.format(world))

    def enter_PIC(self, PIC):
        self.grab_frame()
        for key in PIC:
            if not locate_on_screen_and_click('refs/PIC keys/{}.png'.format(key), duration=.5):
                raise Exception('Faild entering PIC, unable to find the key for `{}`.'.format(key))
        press_and_release('enter')

    def save_last_frames(self, path, fps=10, fourcc='H264'):
        fourcc = cv2.VideoWriter_fourcc(*fourcc)
        writer = cv2.VideoWriter(path, fourcc, fps, self.frames[0].shape[1::-1])

        for frame in self.frames:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            writer.write(frame)

        writer.release()

    def focus_maple(self):
        focus_maple()

    def get_exp_precent(self):
        try:
            box = get_maple_windows()[0].box
            images = ["slash.png", "bracket.png"] + [str(i) + '.png' for i in range(10)]
            pyautogui.moveTo(box.left + 5, box.top + box.height - 5, _pause=False)
            self.grab_frame()
            img = Image.fromarray(self.frame_arr[-30:-5, 5:500])
            if locate('refs/EXP digits/exp.png', img, confidence=.85):
                results = locate_all_multiple_images(img,
                                                     'refs/EXP digits/',
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

    def release_move(self):
        self.focus_maple()
        release(self.move_key)

    def move(self):
        press_and_release(self.move_key)

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
        moving = keyboard.is_pressed(self.move_key)
        if moving and self.move_mode == MapleMoveMode.HOLD:
            self.release_move()
        self.change_move_direction()
        if moving and self.move_mode == MapleMoveMode.HOLD:
            self.press_move()

    def get_smart_direction(self, mapPercent=.25):
        self.grab_frame()
        try:
            portalPositions = [portalPos.left for portalPos in
                               pyautogui.locateAll('./refs/mini map/Portal.png', self.frame_pil, confidence=.75)]
            x1, x2 = min(portalPositions), max(portalPositions)
            xDiff = x2 - x1
            xMiddle = x1 + xDiff / 2
            winSize = xDiff * mapPercent
            xMin, xMax = int(xMiddle - winSize), int(xMiddle + winSize)
            playerX = self.get_player_position().left
            if not (xMin <= playerX <= xMax):
                return -1 if xMiddle - playerX < 0 else 1
            else:
                return 0
        except:
            return np.random.choice([-1, 1])

    def ascend(self):
        press_and_release(self.ascend_key)

    def get_player_position(self, confidence=.9):
        return pyautogui.locate('./refs/mini map/Player.png', self.frame_pil, confidence=confidence)

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

    def click_ok_button(self, duration=1):
        self.grab_frame()
        button = locate_on_screen('refs/buttons/Ok.png', confidence=.95)
        if button:
            pyautogui.click(button, duration=duration)

    def check_world_menu_open(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/messages/Select a world.png", self.frame_pil) else False

    def check_rune_message_open(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/messages/Rune message 1.png", self.frame_pil) else False

    def check_settings_menu_open(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/menus/Settings menu E.png", self.frame_pil) else False

    def check_ingame_channel_menu_open(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/buttons/Change channel button.png", self.frame_pil) else False

    def check_unable_change_channel_dialog_open(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/messages/Unable to change channel dialog.png", self.frame_pil) else False

    def check_news_window_open(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/buttons/Login news buttons.png", self.frame_pil) else False

    def check_world_menu_channels_menu_open(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/buttons/World menu channels button.png", self.frame_pil) else False

    def check_characters_menu_open(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/buttons/Create character button.png", self.frame_pil) else False

    def check_cashshop_button_inview(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/buttons/Cash shop button.png", self.frame_pil) else False

    def check_black_screen(self):
        self.grab_frame()
        return np.all(self.frame_arr[100:500, 100:500] == 0)

    def check_dead(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/messages/Death message.png", self.frame_pil) else False

    def check_exp_bar_inview(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/bars/EXP bar.png", self.frame_pil) else False

    def check_other_player_in_map(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/mini map/Other player.png", self.frame_pil) else False

    def check_no_potion_curse(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/curses/No potions curse.png", self.frame_pil) else False

    def check_rune_cooldown_message(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/messages/Rune cooldown.png", self.frame_pil, confidence=.5) else False

    def check_rune_cooldown_buff(self):
        self.grab_frame()
        return True if pyautogui.locate("refs/curses/Rune cooldown.png", self.frame_pil, confidence=.75) else False

    def check_world_map_open(self):
        self.grab_frame()
        return True if locate('refs/bars/World map.png', self.frame_pil, confidence=.9) else False

    def check_world_map_teleport_message(self):
        self.grab_frame()
        return True if locate('refs/messages/World map teleport message.png', self.frame_pil, confidence=.75) else False

    def check_missing_hyper_message(self):
        self.grab_frame()
        return True if locate('refs/messages/Missing hyper rock.png', self.frame_pil, confidence=.75) else False

    def close_tabs(self):
        self.grab_frame()
        i = 1
        while locate_and_click('refs/buttons/Close button.png', self.frame_pil, self.box, duration=.5,
                               confidence=.8) and not self.pause_state:
            self.grab_frame()
            log('Closed tab num. ' + str(i))
            press_and_release('enter')
            sleep(.25)
            i += 1

    def check_channel(self):
        return self.check_rune_message_open() or self.check_other_player_in_map() or self.check_cooldown(
            'change_channel', self.channel_period)

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
        rune = pyautogui.locate("refs/mini map/Rune.png", self.frame_pil)

        # Help function
        def filter_rune_results(results, tag):
            results = list(results)
            if len(results) == 0: return []
            current_result = results[0]
            yield (tag, current_result.left)
            for result in results:
                if not (current_result.left - 5 <= result.left <= current_result.left + 5):
                    current_result = result
                    yield (tag, current_result.left)

        if player and rune:  # If player and rune are visible in the minimap
            log('Attempting to activate rune')
            if rune.top - 3 <= player.top <= rune.top + 3:  # Rune is reachable by the player
                direction = -1 if player.left - rune.left > 0 else 1
                self.release_move()
                self.lock_move()
                self.set_move_direction(direction, force_mode=MapleMoveMode.HOLD)
                self.restart_cooldown('attempt rune')
                while not self.check_cooldown('attempt rune',
                                              10) and not self.pause_state:  # Maximum of 10 seconds to attempt activating the rune
                    log('Moving towards rune - ' + str(abs(player.left - rune.left)) + 'px left')
                    self.check_health_and_heal()
                    self.release_move()
                    self.move()  # Move towards rune

                    player = self.get_player_position()
                    if not player:
                        break
                    elif rune.left - 3 <= player.left <= rune.left + 3:  # Check if player reached rune
                        sleep(1.5)
                        self.interact()

                        sleep(.5)
                        self.grab_frame(focus=False)

                        ups = filter_rune_results(locate_all('refs/rune keys/Up.png', self.frame_pil, confidence=.7),
                                                  'up')
                        downs = filter_rune_results(
                            locate_all('refs/rune keys/Down.png', self.frame_pil, confidence=.7), 'down')
                        rights = filter_rune_results(
                            locate_all('refs/rune keys/Right.png', self.frame_pil, confidence=.7), 'right')
                        lefts = filter_rune_results(
                            locate_all('refs/rune keys/Left.png', self.frame_pil, confidence=.7), 'left')

                        for key, x in sorted(itertools.chain(ups, downs, rights, lefts), key=lambda x: x[1]):
                            press_and_release(key)
                            sleep(.25)

                        log('Activated rune')
                        self.unlock_move()
                        return True
                self.unlock_move()
            else:
                log('Rune is unreachable by the player')
        return False

    def open_world_map(self):
        press_and_release(self.world_map_key)

    def mark_world_map_location(self):
        self.focus_maple()
        if not self.check_world_map_open():
            self.open_world_map()
            sleep(.5)
        self.grab_frame(focus=False)
        if self.check_world_map_open():
            mark = locate('refs/map/Location mark.png', self.frame_pil, confidence=.85)
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

    def jump_or_doublejump(self):
        if self.doublejump_state:
            self.doublejump()
        else:
            self.jump()

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
            self.check_direction_and_change()
            self.press_move()

    def restart_cooldown(self, key):
        self.cooldowns[key] = time.time()

    def check_cooldown(self, key, cooldown):
        if cooldown == -1 or cooldown == None: return False
        if key in self.cooldowns:
            return True if time.time() - self.cooldowns[key] > cooldown else False
        else:
            return True

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