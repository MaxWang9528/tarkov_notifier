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

S = settings.Settings
U = settings.userInfo
STATES = settings.states
T2_STOP = False
COUNTER = 0
STATE = 'Not Started'
ICON: pystray.Icon


def create_menu(action):
    menu = pystray.Menu(
        pystray.MenuItem('Start', action),
        pystray.MenuItem('Stop', action),
        pystray.MenuItem('Quit', action),
        pystray.MenuItem(f'State: {STATE}', action),
        pystray.MenuItem('placeholder', action))
    return menu


def on_clicked(icon, item):
    global T2_STOP
    global STATE
    if str(item) == 'Start':
        t2 = threading.Thread(target=main)
        t2.daemon = True
        T2_STOP = False
        t2.start()
    if str(item) == 'Stop':
        STATE = 'Not Started'
        ICON.menu = create_menu(on_clicked)
        T2_STOP = True
    if str(item) == 'Quit':
        icon.stop()


def tray():
    global ICON
    image = PIL.Image.open('tray_icon.jpg')
    ICON = pystray.Icon('Tarkov Notifications', image, menu=create_menu(on_clicked))
    ICON.run()
    sys.exit()


# Apply filters to the original image for better recognition
def screen_image_preprocessing():
    capture = np.array(ImageGrab.grab(bbox=S.get('capture-bbox')), dtype='uint8')
    rgb = cv2.cvtColor(capture, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(capture, cv2.COLOR_RGB2GRAY)
    _, th1 = cv2.threshold(gray, S.get('threshold'), 255, cv2.THRESH_BINARY)
    return th1, rgb


# Draw bounding boxes around words on the rgb image
def word_bbox(th1, rgb):
    if S.get('see-what-the-computer-sees'):
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

    if S.get('debug_mode'):
        cv2.imshow('window', img)
        cv2.waitKey(0)
    return all_words, rgb


# determines the game state depending on what words were found in the screen capture
def get_game_state(all_words):
    global STATE
    for tup in STATES:
        if tup[0] in all_words:
            STATE = tup[1]
            return tup[1]
    STATE = 'Unknown'
    return 'Unknown'


def main():
    global COUNTER
    global ICON
    past_states = []
    while not T2_STOP:
        start = time.time()
        th1, rgb = screen_image_preprocessing()
        if S.get('message_type') == 'sms':
            all_words = pytesseract.image_to_string(th1)
            state = get_game_state(all_words)
            if state in S.get('notify_on') and state not in past_states:
                send_notification.send_sms(U.get('number'), state, PROVIDERS.get(settings.userInfo.get('provider')).get("mms"), (U.get('email'), U.get('app_password')))
                past_states.append(state)

        # only do the extra steps for mms
        else:  # MESSAGE_TYPE == 'mms'
            all_words, rgb = word_bbox(th1, rgb)
            state = get_game_state(all_words)
            if state in S.get('notify_on') and state not in past_states:
                title = round(time.time(), 1)
                cv2.imwrite(f'images/{title}.jpg', rgb)
                send_notification.send_mms(U.get('number'), state, PROVIDERS.get(settings.userInfo.get('provider')).get("mms"), (U.get('email'), U.get('app_password')), f'images/{title}.jpg', 'image', 'jpg')
                if not S.get('save_sent_images'):
                    os.remove(f'images/{title}.jpg')
                past_states.append(state)

        ICON.menu = create_menu(on_clicked)
        print(f'({COUNTER}) {state}')
        COUNTER += 1
        if state in S.get('pause_on'):
            on_clicked(ICON, 'Stop')
        elapsed = time.time() - start
        if S.get('screen_capture_delay') - elapsed > 0:
            time.sleep(S.get('screen_capture_delay') - elapsed)  # sleep for the remaining capture delay time


def debug():
    img, rgb = screen_image_preprocessing()
    word_bbox(img, rgb)


if __name__ == '__main__':
    if S.get('debug_mode'):
        debug()
    else:
        t1 = threading.Thread(target=tray)
        t1.start()
