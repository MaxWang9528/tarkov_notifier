from pytesseract import pytesseract
from pytesseract import Output
import settings
import time
from info import PROVIDERS
import send_notification
from PIL import ImageGrab
import numpy as np
import cv2
pytesseract.tesseract_cmd = 'Tesseract-OCR\\tesseract.exe'

THRESHOLD = settings.Settings.get('threshold')
DEBUG_MODE = settings.Settings.get('debug_mode')
THRESH_MODE = settings.Settings.get('see-what-the-computer-gets')
CAPTURE_DELAY = settings.Settings.get('screen_capture_delay')

NUMBER = settings.userInfo.get('number')
PROVIDER = settings.userInfo.get('provider')
EMAIL = settings.userInfo.get('email')
PASSWORD = settings.userInfo.get('app_password')
SCREEN_WIDTH = settings.userInfo.get('screen_width')
SCREEN_HEIGHT = settings.userInfo.get('screen_height')
NOTIFY_ON = settings.Settings.get('notify_on')
MESSAGE_TYPE = settings.Settings.get('message_type')
AT = PROVIDERS.get(PROVIDER).get("mms")


# Apply filters to the original image for better recognition
def screen_image_preprocessing():
    capture = np.array(ImageGrab.grab(bbox=(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)), dtype='uint8')
    rgb = cv2.cvtColor(capture, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(capture, cv2.COLOR_RGB2GRAY)
    _, th1 = cv2.threshold(gray, THRESHOLD, 255, cv2.THRESH_BINARY)
    return th1, rgb


# Draw bounding boxes around words on the rgb image
def word_bbox(img, rgb):
    image_data = pytesseract.image_to_data(img, output_type=Output.DICT)
    all_words = []
    for i, word in enumerate(image_data['text']):
        if word != '':
            # print(word)
            all_words.append(word)
            x, y, w, h = image_data['left'][i], image_data['top'][i], image_data['width'][i], image_data['height'][i]
            cv2.rectangle(rgb, (x, y), (x+w, y+h), (0, 255, 0), 1)

    if DEBUG_MODE:
        if THRESH_MODE:
            cv2.imshow('window', img)
        else:
            cv2.imshow('window', rgb)
        cv2.waitKey(0)
    return all_words, rgb


# determines the game state depending on what words were found in the screen capture
def get_game_state(all_words):
    if 'Matching...' in all_words:
        state = 'Matching'
    elif 'loot...' in all_words:
        state = 'Loading loot'
    elif 'Awaiting' in all_words:
        state = 'Awaiting session start'
    elif 'Waiting' in all_words:
        state = 'Waiting for players'
    elif 'Deploying' in all_words:
        state = 'Deploying'
    else:
        state = 'Unknown'
    return state


def main():
    past_states = []
    while True:
        start = time.time()
        th1, rgb = screen_image_preprocessing()
        all_words, rgb_bbox = word_bbox(th1, rgb)
        state = get_game_state(all_words)
        if state in NOTIFY_ON and state not in past_states:
            past_states.append(state)
            if MESSAGE_TYPE == 'sms':
                send_notification.send_sms(NUMBER, state, AT, (EMAIL, PASSWORD))
            else:
                title = round(time.time(), 1)
                cv2.imwrite(f'images/{title}.jpg', rgb_bbox)
                send_notification.send_mms(NUMBER, state, AT, (EMAIL, PASSWORD), f'images/{title}.jpg', 'image', 'jpg')
        print(state)
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
        main()

