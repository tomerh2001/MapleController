# In[14]:
import collections
import os
import sys
import time
import traceback
import numpy as np

sys.path.append('..')
sys.path.append('..\\Dependencies')
sys.path.append('..\\Controller')

from Controller.BaseController import *
from Dependencies import admin

# In[3]:


print("Created by tomergt45 (Tomergt89@gmail.com or github.com/tomergt45) ")

if not admin.isUserAdmin():
    print("Note: You must run this application as administrator")
    admin.runAsAdmin(wait=False)
    sys.exit()

print("Note: You must play on windowed 800x600 (4:3)")
print(
    "Note: You must change your windows UAC settings to 'Never Notify' (don't forget to turn it back after using the bot!)")


# In[4]:

def get_json_files(path='.'):
    return [f for f in os.listdir(".") if f.endswith(".json")]


files = get_json_files()

if len(files) == 0:
    raise Exception('No settings.json file was found.')
elif len(files) == 1:
    settingsPath = files[0]
else:
    print('Found multiple .json files, please select the one you want to use:')
    for i, file in enumerate(files):
        print(str(i + 1) + ')', file)
    selection = int(input("I select: "))
    settingsPath = files[selection - 1]

controller = MapleController(settingsPath)

# In[4]:

start_time = datetime.datetime.now()
maxlen = 10
history = {
    'last_verbose': time.time(),
    'exp_per_minute_history': collections.deque(maxlen=maxlen),
}
controller.restart_cooldown('change_channel')


# In[5]:
def clear():
    s = os.system("cls")


def pretty_delta(delta, granularity=2):
    result = []
    intervals = (('weeks', 604800), ('days', 86400), ('hours', 3600), ('minutes', 60), ('seconds', 1))
    seconds = delta.seconds
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


def refresh_exp_history(current_exp, t_diff):
    if current_exp < history.get('last_exp', current_exp):
        history['last_exp'] = 0
        history['exp_per_minute_history'] = collections.deque(maxlen=maxlen)
    current_exp_diff = current_exp - history.get('last_exp', current_exp)  # Gained EXP
    current_exp_per_minute = current_exp_diff * (1 / t_diff) * 60
    current_exp_per_hour = current_exp_per_minute * 60
    history['exp_per_minute_history'].append(current_exp_per_minute)
    history['last_exp'] = current_exp


def verbose():
    if controller.check_black_screen():
        sleep(1)
        return False

    t_diff = time.time() - history['last_verbose']

    # Calculate EXP
    if not controller.pause_state:
        current_exp = controller.get_exp_precent()
        refresh_exp_history(current_exp, t_diff)
        exp_per_minute = np.mean(history['exp_per_minute_history'])
        exp_per_hour = exp_per_minute * 60
        exp_diff = exp_per_minute / 60 * t_diff
        estimated_time_rankup = pretty_delta(datetime.timedelta(
            minutes=(100 - current_exp) / exp_per_minute)) if exp_per_minute != 0 else "Gain more EXP for estimation"
    else:
        current_exp = history['last_exp']
        exp_diff = exp_per_minute = exp_per_hour = 0
        estimated_time_rankup = 'Unable to estimate while paused'

    clear()
    print(f"""
    Elapsed time:\t\t {str((datetime.datetime.now() - start_time))}
    Paused:\t\t\t {controller.pause_state}
    Deaths:\t\t\t {controller.deaths}
    HP Potions used:\t\t {controller.hp_potions_used}
    MP Potions used:\t\t {controller.mp_potions_used}
    EXP per {round(t_diff, 1)}s/1m/1h: \t {str(round(exp_diff, 2))}% / {str(round(exp_per_minute, 2))}% / {str(round(exp_per_hour, 2))}%
    Estimated time till rankup:\t {estimated_time_rankup}
    """)
    history['last_verbose'] = time.time()


# In[6]:


def login_bot():
    close_news = select_character = select_world = False
    controller.restart_cooldown('wait_for_ingame_view')

    if controller.get_status() != MapleState.ACTIVE:
        log('Launching maplestory', console=True)
        controller.launch_maple()
        sleep(30)  # Give at least 30 seconds for maple to launch
        while 1:
            if controller.pause_state:
                continue
            try:
                if controller.check_world_menu_open() or controller.check_cooldown('wait_for_ingame_view', 180):
                    break
            except Exception as e:
                log(str(e), console=True)
                sleep(5)

    while not controller.check_cooldown('wait_for_ingame_view', 60 * 5):
        if controller.pause_state:
            continue
        if controller.get_status() == MapleState.ACTIVE:
            if controller.check_world_menu_open() and not select_world:
                log('Maplestory launched and detected', console=True)
                select_world = True
                controller.select_world(controller.world)
                sleep(3)

            elif controller.check_characters_menu_open() and not select_character:
                log('Entered characters menu', console=True)
                select_character = True
                press_and_release('enter')
                controller.enter_PIC(controller.PIC)
                sleep(3)

            elif controller.check_news_window_open() and not close_news:
                sleep(1)
                log('Closing annoying news window', console=True)
                close_news = True
                press_and_release('esc')
                sleep(2)

            elif controller.check_exp_bar_inview():
                log('Player spawned', console=True)
                if not close_news:
                    log('Pressing safeguard ESC', console=True)
                    press_and_release('esc')
                    sleep(.5)
                    if controller.check_settings_menu_open():
                        press_and_release('esc')
                        sleep(1)
                if select_world or select_character:
                    sleep(1)
                    controller.use_spawn_skills()
                return True
    return False


# In[7]:


def afk_bot():
    if controller.hold_up_state:
        controller.press_up()
    if controller.move_mode == MapleMoveMode.HOLD:
        controller.press_move()

    # Check that maplestory is running and that the cashshop button is in view (indicating that you are in game)
    while controller.get_status() == 1:
        try:  # Sanity check: Failing to grab frame means app is not running properly
            verbose()

            if controller.pause_state:
                continue
            if controller.check_unable_change_channel_dialog_open():
                press_and_release('enter')
            if controller.check_dead():
                controller.on_death()
                sleep(1)
                break

            controller.check_health_and_heal()
            controller.close_tabs()

            if controller.check_mana():
                controller.fill_mana()
                sleep(.15)
            controller.check_direction_and_change()

            if controller.check_cooldown("pet_food", controller.pet_food_period):
                controller.feed_pet()
                controller.restart_cooldown('pet_food')

            if controller.pause_state:
                continue
            controller.check_health_and_heal()

            # Attempt to activate rune only if not on cooldown
            if not controller.check_rune_cooldown_buff() and controller.attempt_rune():
                pass
            # Change channel if:
            # Faild to activate rune / Rune is blocking EXP / Another player in map / Channel timeout exceeded
            elif controller.check_channel():
                # Release move / up keys if on hold
                if controller.hold_up_state:
                    controller.release_up()
                if controller.move_mode == MapleMoveMode.HOLD:
                    controller.release_move()

                status = controller.move_channel()
                if not status:  # Exit bot if faild to change channel
                    break

                sleep(2)
                controller.restart_cooldown('change_channel')

                # Press move / up keys if on hold
                if controller.hold_up_state:
                    controller.press_up()
                if controller.move_mode == MapleMoveMode.HOLD:
                    controller.press_move()

            while controller.check_no_potion_curse():
                controller.jump_or_doublejump()
                controller.attack()
                controller.check_direction_and_change()
                sleep(.5)

            if controller.pause_state:
                continue
            controller.check_health_and_heal()

            if controller.check_cooldown('buffs', controller.buffs_period):
                controller.attack()
                controller.use_buffs()
                controller.restart_cooldown('buffs')
            # Periodical HP check
            if controller.check_cooldown('period hp', 30):
                controller.heal()
                controller.restart_cooldown('period hp')
            if controller.pause_state:
                continue

            if controller.move_mode == MapleMoveMode.TELEPORT:
                controller.grab_frame()
                if controller.check_cooldown('teleport down', controller.teleport_down_period):
                    controller.restart_cooldown('teleport down')
                    controller.teleport_down()
                    sleep(.25)
                elif controller.check_cooldown('teleport up', controller.teleport_up_period):
                    controller.restart_cooldown('teleport up')
                    controller.teleport_up()
                    sleep(.25)
                controller.move()

            controller.jump_or_doublejump()
            controller.check_health_and_heal()
            controller.use_uncooldowned_skills()
            controller.check_health_and_heal()
            controller.check_direction_and_change()
            controller.attack()
        except:
            import traceback
            log('AFK Bot crashed attempting restart')
            log(''.join(traceback.format_exception(*sys.exc_info())), console=True)
            break

    # Release keys left pressed
    if controller.hold_up_state:
        controller.release_up()
    if controller.move_mode == MapleMoveMode.HOLD:
        controller.release_move()


# In[8]:
while 1:
    if controller.pause_state:
        continue
    if controller.get_status() == MapleState.CRASHED:  # Check if maple crashed
        if controller.attempt_restart_after_crash_state:  # Close crashed maple
            clear()
            log('Maplestory has crashed... closing program', console=True)
            controller.close_maple()
            log('Maplestory closed, waiting 10 seconds and then launching back', console=True)
            sleep(10)  # Wait a bit for maplestory to close properly
        else:
            log(
                'Maplestory has crashed, exiting program... (If you want to auto restart maple in future crashes, set "attempt_restart_after_crash=true" in the settings.json file)',
                console=True)

    # launch the game, select world, enter PIC and conddddinue fighting
    status = login_bot()
    try:
        if status:
            afk_bot()
            clear()
        else:
            log(
                'Maplestory attempt to launch and login has faild after 5 minutes of wait time (this includes attempting to launch the game, select a world, channel, character and enter PIC).',
                console=True)
            break
    except:
        import tracebackddd

        log(''.join(traceback.format_exception(*sys.exc_info())), console=True)
