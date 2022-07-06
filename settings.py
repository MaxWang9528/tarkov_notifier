userInfo = {
    'number': 1234567890,                   # 10 digit phone number
    'provider': 'Provider Name',            # check info.py for exact name of any cell service provider
    'email': 'email@gmail.com',
    'app_password': 'qwertyuiopasdfgh',     # https://myaccount.google.com/apppasswords
}

states = [
    ('Matching', 'Matching'),               # ('string found', 'game state')
    ('loot', 'Loading loot'),
    ('Awaiting', 'Awaiting session start'),
    ('Waiting', 'Waiting for players'),
    ('Deploying',  'Deploying'),
]

Settings = {
    'debug_mode': False,                    # show a window with the screen capture
    'see-what-the-computer-sees': False,    # show a window with the preprocessed screen capture
    'threshold': 110,                       # threshold amount
    'screen_capture_delay': 1,              # seconds between screen captures
    'message_type': 'mms',                  # sms with no images OR mms with images
    'notify_on': ['Loading loot', 'Waiting for players', 'Deploying'],  # notifies if any of these strings are found
    'pause_on': ['Deploying'],              # stops program if any of these strings are found
    'save_sent_images': False,              # save the screen capture in /images
    'capture-bbox': (0, 0, 1920, 1080)      # x1, y1, x2, y2
                                            # (700, 700, 1220, 950) might be faster?
}
