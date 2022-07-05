from pytesseract import pytesseract
from pytesseract import Output
import settings
import time
from info import PROVIDERS
import send_notification
import PIL
from PIL import Image
from PIL import ImageGrab
import numpy as np
import cv2
import os
import pystray
import threading
import sys

pytesseract.tesseract_cmd = 'Tesseract-OCR\\tesseract.exe'

T2_STOP = False
THRESHOLD = settings.Settings.get('threshold')
DEBUG_MODE = settings.Settings.get('debug_mode')
THRESH_MODE = settings.Settings.get('see-what-the-computer-sees')
CAPTURE_DELAY = settings.Settings.get('screen_capture_delay')
SCREEN_WIDTH = settings.userInfo.get('screen_width')
SCREEN_HEIGHT = settings.userInfo.get('screen_height')
POSSIBLE_STATES = settings.states
NOTIFY_ON = settings.Settings.get('notify_on')
QUIT_ON = settings.Settings.get('quit_on')
MESSAGE_TYPE = settings.Settings.get('message_type')
SAVE_IMAGES = settings.Settings.get('save_sent_images')

NUMBER = settings.userInfo.get('number')
PROVIDER = settings.userInfo.get('provider')
EMAIL = settings.userInfo.get('email')
AT = PROVIDERS.get(PROVIDER).get("mms")
PASSWORD = settings.userInfo.get('app_password')
COUNTER = 0


# class ThreadwResult(threading.Thread):
#     def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
#         self.result = None
#
#         def function():
#             self.result = target(*args, **kwargs)
#         super().__init__(group=group, target=function, name=name, daemon=daemon)
#
#
# def run_once(f):
#     def wrapper(*args, **kwargs):
#         if not wrapper.has_run:
#             wrapper.has_run = True
#             return f(*args, **kwargs)
#     wrapper.has_run = False
#     return wrapper


def tray(state):
    image = PIL.Image.open('tray_icon.jpg')

    def on_clicked(icon, item):
        global T2_STOP
        if str(item) == 'Start':
            t2.daemon = True
            T2_STOP = False
            t2.start()
        if str(item) == 'Stop':
            T2_STOP = True
        if str(item) == 'Quit':
            icon.stop()
    icon = pystray.Icon('Tarkov Notifications', image, menu=pystray.Menu(
        pystray.MenuItem('Start', on_clicked),
        pystray.MenuItem('Stop', on_clicked),
        pystray.MenuItem('Quit', on_clicked),
        pystray.MenuItem(f'State: {state}', on_clicked)
    ))

    icon.run()
    # icon.stop() jumps to here
    sys.exit()


# Apply filters to the original image for better recognition
def screen_image_preprocessing():
    capture = np.array(ImageGrab.grab(bbox=(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)), dtype='uint8')
    rgb = cv2.cvtColor(capture, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(capture, cv2.COLOR_RGB2GRAY)
    _, th1 = cv2.threshold(gray, THRESHOLD, 255, cv2.THRESH_BINARY)
    return th1, rgb


# Draw bounding boxes around words on the rgb image
def word_bbox(th1, rgb):
    if THRESH_MODE:
        img = th1
    else:
        img = rgb
    image_data = pytesseract.image_to_data(th1, output_type=Output.DICT)
    all_words = ''
    for i, word in enumerate(image_data['text']):
        if word != '':
            # print(word)
            all_words += word
            x, y, w, h = image_data['left'][i], image_data['top'][i], image_data['width'][i], image_data['height'][i]
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)

    if DEBUG_MODE:
        cv2.imshow('window', img)
        cv2.waitKey(0)
    return all_words, rgb


# determines the game state depending on what words were found in the screen capture
def get_game_state(all_words):
    for tup in POSSIBLE_STATES:
        if tup[0] in all_words:
            return tup[1]
    return 'Unknown'


def main():
    global COUNTER
    past_states = []
    while not T2_STOP:
        start = time.time()
        th1, rgb = screen_image_preprocessing()
        if MESSAGE_TYPE == 'sms':
            all_words = pytesseract.image_to_string(th1)
            state = get_game_state(all_words)
            if state in NOTIFY_ON and state not in past_states:
                send_notification.send_sms(NUMBER, state, AT, (EMAIL, PASSWORD))
                past_states.append(state)

        # only do the extra steps for mms
        else:  # MESSAGE_TYPE == 'mms'
            all_words, rgb = word_bbox(th1, rgb)
            state = get_game_state(all_words)
            if state in NOTIFY_ON and state not in past_states:
                title = round(time.time(), 1)
                cv2.imwrite(f'images/{title}.jpg', rgb)
                send_notification.send_mms(NUMBER, state, AT, (EMAIL, PASSWORD), f'images/{title}.jpg', 'image', 'jpg')
                if not SAVE_IMAGES:
                    os.remove(f'images/{title}.jpg')
                past_states.append(state)

        print(f'({COUNTER}) {state}')
        COUNTER += 1
        if state in QUIT_ON:
            quit()
        elapsed = time.time() - start
        if CAPTURE_DELAY - elapsed > 0:
            time.sleep(CAPTURE_DELAY - elapsed)  # sleep for the remaining capture delay time


def debug():
    img, rgb = screen_image_preprocessing()
    word_bbox(img, rgb)


if __name__ == '__main__':
    if DEBUG_MODE:
        debug()
    else:
        t1 = threading.Thread(target=tray, args=('Not started',))
        t2 = threading.Thread(target=main)

        t1.start()
