import pathlib

from Controller.Controllers.BaseController import BaseController
from Controller.funcs import *


class GameController(BaseController):
    def __init__(self, settings_path, log_path='log.txt', resources_path="refs"):
        super().__init__(settings_path, log_path)

        self.world = self.get('world')
        self.PIC = self.get('PIC')
        self.world_map_key = self.get('world_map', 'w')
        self.channel_period = self.get('change_channel_period', 600)

        # Default variables
        self.resources_path = pathlib.Path(resources_path)
        if not self.resources_path.exists():
            raise Exception("Unable to locate the refs folder at '" + resources_path + "'")

    def select_world(self, world, channel=1):
        self.grab_frame()
        if self.check_world_menu_open():
            if not locate_on_screen(self.get_resource_path("worlds/{}.png".format(world))):
                self.grab_frame()
                press_and_release('up')
                sleep(.25)
                press_and_release('up')
                sleep(.25)
            if locate_on_screen_and_click(self.get_resource_path("worlds/{}.png".format(world)), duration=1):
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
            if not locate_on_screen_and_click(self.get_resource_path('PIC keys/{}.png'.format(key)), duration=.5):
                raise Exception('Faild entering PIC, unable to find the key for `{}`.'.format(key))
        press_and_release('enter')

    def get_player_position(self, confidence=.9, minimap=None):
        if not minimap:
            minimap = self.get_mini_map()
        return locate(self.get_resource_path('mini map/Player.png'), minimap, confidence=confidence)

    def get_rune_position(self, confidence=.9, minimap=None):
        if not minimap:
            minimap = self.get_mini_map()
        return locate(self.get_resource_path('mini map/Rune.png'), minimap, confidence=confidence)

    def get_mini_map(self, padding=5, confidence=.98):
        self.grab_frame()

        left_edge = locate(self.get_resource_path("mini map/Left edge.png"), self.frame_pil, confidence=confidence)
        right_edge = locate(self.get_resource_path("mini map/Right edge.png"), self.frame_pil, confidence=confidence)

        try:
            return self.frame_pil.crop((left_edge.left, left_edge.top, right_edge.left + padding, right_edge.top + padding))
        except:
            print("Faild to find minimap")
            button = self.get_npc_button()
            if not button:
                button = self.get_world_button()
            if button:
                width, height = self.frame_pil.size
                return self.frame_pil.crop((0, 0, button.left + button.width + 10, height))
            else:
                return self.frame_pil

    def get_world_button(self):
        self.grab_frame()
        return locate(self.get_resource_path("mini map/World.png"), self.frame_pil)

    def get_npc_button(self):
        self.grab_frame()
        return locate(self.get_resource_path("mini map/Npc.png"), self.frame_pil)

    def click_ok_button(self, duration=1):
        self.grab_frame()
        button = locate_on_screen(self.get_resource_path('buttons/Ok.png'), confidence=.95)
        if button:
            pyautogui.click(button, duration=duration)

    def close_tabs(self):
        self.grab_frame()
        i = 1
        while locate_and_click(self.get_resource_path('buttons/Close button.png'), self.frame_pil, self.box, duration=.5,
                               confidence=.8) and not self.pause_state:
            self.grab_frame()
            log('Closed tab num. ' + str(i))
            press_and_release('enter')
            sleep(.25)
            i += 1

    def open_world_map(self):
        press_and_release(self.world_map_key)

    def get_resource_path(self, resource):
        path = self.resources_path / resource
        if not path.exists():
            raise Exception("Unable to locate resource at " + str(path))
        return str(path)

    def check_frame_for_resource(self, resource, confidence=.99):
        path = self.get_resource_path(resource)
        return True if locate(path, self.frame_pil, confidence=confidence) else False

    def check_world_menu_open(self):
        self.grab_frame()
        return self.check_frame_for_resource("messages/Select a world.png")

    def check_rune_message_open(self):
        self.grab_frame()
        return self.check_frame_for_resource("messages/Rune message 1.png")

    def check_settings_menu_open(self):
        self.grab_frame()
        return self.check_frame_for_resource("menus/Settings menu E.png")

    def check_ingame_channel_menu_open(self):
        self.grab_frame()
        return self.check_frame_for_resource("buttons/Change channel button.png")

    def check_unable_change_channel_dialog_open(self):
        self.grab_frame()
        return self.check_frame_for_resource("messages/Unable to change channel dialog.png")

    def check_news_window_open(self):
        self.grab_frame()
        return self.check_frame_for_resource("buttons/Login news buttons.png")

    def check_world_menu_channels_menu_open(self):
        self.grab_frame()
        return self.check_frame_for_resource("buttons/World menu channels button.png")

    def check_characters_menu_open(self):
        self.grab_frame()
        return self.check_frame_for_resource("buttons/Create character button.png")

    def check_cashshop_button_inview(self):
        self.grab_frame()
        return self.check_frame_for_resource("buttons/Cash shop button.png")

    def check_black_screen(self):
        self.grab_frame()
        return np.all(self.frame_arr[100:500, 100:500] == 0)

    def check_dead(self):
        self.grab_frame()
        return self.check_frame_for_resource("messages/Death message.png")

    def check_exp_bar_inview(self):
        self.grab_frame()
        return self.check_frame_for_resource("bars/EXP bar.png")

    def check_other_player_in_map(self, minimap=None):
        if not minimap:
            minimap = self.get_mini_map()
        return locate(self.get_resource_path("mini map/Other player.png"), minimap)

    def check_no_potion_curse(self):
        self.grab_frame()
        return self.check_frame_for_resource("curses/No potions curse.png")

    def check_rune_cooldown_message(self):
        self.grab_frame()
        return self.check_frame_for_resource("messages/Rune cooldown.png", confidence=.5)

    def check_rune_cooldown_buff(self):
        self.grab_frame()
        return self.check_frame_for_resource("curses/Rune cooldown.png", confidence=.75)

    def check_world_map_open(self):
        self.grab_frame()
        return self.check_frame_for_resource('bars/World map.png', confidence=.9)

    def check_world_map_teleport_message(self):
        self.grab_frame()
        return self.check_frame_for_resource('messages/World map teleport message.png', confidence=.75)

    def check_missing_hyper_message(self):
        self.grab_frame()
        return self.check_frame_for_resource('messages/Missing hyper rock.png', confidence=.75)

    def check_channel(self):
        return self.check_rune_message_open() \
               or self.check_other_player_in_map() \
               or self.check_cooldown('change_channel', self.channel_period)

