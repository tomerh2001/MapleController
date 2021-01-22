import datetime
import os
import time

import keyboard
import mss
import numpy as np
import psutil
import pyautogui
import win32gui
from PIL import Image
from win32com.client import Dispatch
from Controller.MapleState import MapleState


def get_maple_hwnd():
    return win32gui.FindWindowEx(None, None, None, 'MapleStory')


def get_maple_processes():
    for proc in psutil.process_iter():
        if 'maplestory' in proc.name().lower():
            yield proc


def convert_psutil_status(status):
    if status == psutil.STATUS_RUNNING:
        return MapleState.ACTIVE
    else:
        return MapleState.CRASHED


def get_maple_status():
    mprocesses = list(get_maple_processes())
    if len(mprocesses) == 0:
        return MapleState.CLOSED
    else:
        for mproc in mprocesses:
            status = convert_psutil_status(mproc.status())
            if status != MapleState.ACTIVE:
                return status
        return MapleState.ACTIVE


def focus_maple():
    hwnd = get_maple_hwnd()
    shell = Dispatch("WScript.Shell")
    shell.SendKeys('%')
    try:
        win32gui.SetForegroundWindow(hwnd)
    except:
        pass


def get_maple_windows():
    wins = pyautogui.getWindowsWithTitle("MapleStory")
    if get_maple_status() == MapleState.ACTIVE and len(wins) > 0:
        return list(filter(lambda x: x.title == 'MapleStory', wins))
    else:
        raise Exception("Unable to get maplestory, maplestory is not running")


def grab_maple(focus=True):
    wins = get_maple_windows()
    box = wins[0].box

    if focus:
        focus_maple()

    with mss.mss() as sct:
        mon = sct.monitors[1]
        monitor = {
            "top": mon["top"] + box.top,  # 100px from the top
            "left": mon["left"] + box.left,  # 100px from the left
            "width": box.width,
            "height": box.height,
            "mon": 1,
        }
        img = sct.grab(monitor)
        img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")

    return img, box


def press_and_release(key, release_delay=.1, repeat=1):
    if key:
        for i in range(repeat):
            press(key)
            sleep(release_delay)
            release(key)


def press(key):
    if key:
        keyboard.press(key)


def release(key):
    if key:
        keyboard.release(key)


def click(x=None, y=None, duration=0, clicks=1, interval=0):
    pyautogui.click(x, y, duration=duration, interval=interval, clicks=clicks)


def locate(img_path, source, confidence=.999):
    return pyautogui.locate(img_path, source, confidence=confidence)


def locate_all(img_path, source, confidence=.999):
    return pyautogui.locateAll(img_path, source, confidence=confidence)


def locate_all_multiple_images(source, path, imgnames, confidence=.99, key=None):
    results = []
    for img in imgnames:
        img_path = os.path.join(path, img)
        img = img.split('.')[0]
        for result in locate_all(img_path, source, confidence):
            results.append((img, result))
    results = sorted(results, key=key) if key else results
    return np.asarray(results, dtype=tuple)


def locate_on_screen(img_path, confidence=.999):
    return pyautogui.locateOnScreen(img_path, confidence=confidence)


def locate_all_on_screen(img_path, confidence=.999):
    return pyautogui.locateAllOnScreen(img_path, confidence=confidence)


def locate_on_screen_and_click(img_path, clicks=1, clicks_interval=0, duration=0, confidence=.999):
    box = locate_on_screen(img_path, confidence=confidence)
    if box:
        click(box, duration=duration, clicks=clicks, interval=clicks_interval)
        return True
    return False


def locate_and_click(img_path, source, source_box, clicks=1, clicks_interval=0, duration=0, confidence=.999):
    box = locate(img_path, source, confidence=confidence)
    if box:
        click(source_box.left + box.left, source_box.top + box.top, duration=duration, clicks=clicks,
              interval=clicks_interval)
        return True
    return False


def sleep(seconds):
    time.sleep(seconds)


def log(message, path='log.txt', console=False):
    with open(path, 'a') as fd:
        message = '[{}] {}\n'.format(str(datetime.datetime.now()), message)
        fd.write(message)
        if console:
            print(message)


def clearlog(path='log.txt'):
    with open(path, 'w') as fd:
        fd.seek(0)
        fd.truncate()
