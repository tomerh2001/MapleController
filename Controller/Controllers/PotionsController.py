import numpy as np

from Controller.Controllers.BaseController import BaseController
from Controller.funcs import *


class PotionsController(BaseController):
    def __init__(self, settings_path, logpath='log.txt'):
        super().__init__(settings_path, logpath)

        self.hp_potion_key = self.get('hp_potion', None)
        self.min_potion_hp = self.get('min_potion_hp', 50)
        self.mana_potion_key = self.get('mana_potion', None)
        self.min_potion_mp = self.get('min_potion_mp', 50)
        self.potions_per_use = self.get('potions_per_use', 1)
        self.delay_per_potion = self.get('delay_per_potion', 0)
        self.pet_food_key = self.get('pet_food', None)
        self.pet_food_period = self.get('pet_food_period', 100)

        self.hp_potions_used = 0
        self.mp_potions_used = 0

    def get_hp_precent(self):
        try:
            self.grab_frame()
            img = self.frame_arr[575:586, 441:571]
            img = img.copy()
            img[np.where(img < 200)] = 0
            imax = 0
            for row in img:
                r, g, b = row.T
                cond = (r > 240) & (g == 0) & (b == 0)
                i = np.where(cond)[0].max()
                if i > imax:
                    imax = i
            return imax / img.shape[1] * 100
        except:
            return 0

    def get_mp_precent(self):
        self.grab_frame()
        img = self.frame_arr[591:602, 441:578]
        img = img.copy()
        r, g, b = img.T
        cond = (r < 200) & (g > 200) & (b > 200)
        try:
            mp = np.where(cond)[0].max()
        except:
            mp = 0
        return mp / img.shape[1] * 100

    def check_health(self):
        return self.get_hp_precent() < self.min_potion_hp

    def check_health_and_heal(self, after_delay=0):
        if self.check_health():
            self.heal()
            sleep(after_delay)

    def check_mana(self):
        return self.get_mp_precent() < self.min_potion_mp

    def heal(self):
        self.grab_frame()
        for i in range(self.potions_per_use):
            press_and_release(self.hp_potion_key)
            self.hp_potions_used += 1
            log('Healing')
            if i > 0: sleep(self.delay_per_potion)

    def fill_mana(self, delay_per_fill=.25):
        self.grab_frame()
        for i in range(self.potions_per_use):
            press_and_release(self.mana_potion_key)
            self.mp_potions_used += 1
            log('Filling mana')
            if i > 0: sleep(self.delay_per_potion)

    def feed_pet(self):
        press_and_release(self.pet_food_key)

controller = PotionsController("Shade Settings.json")