userInfo = {
    'number': 1234567890,                   # int
    'provider': 'Provider Name',            # check info.py for exact name
    'email': 'email@gmail.com',             # str
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
    'debug_mode': False,                    # bool
    'see-what-the-computer-sees': False,    # bool
    'threshold': 110,                       # int
    'screen_capture_delay': 1,              # int (seconds)
    'message_type': 'mms',                  # sms OR mms
    'notify_on': ['Loading loot', 'Waiting for players', 'Deploying'],  # notifies if any of these strings are found
    'pause_on': ['Deploying'],              # stops program if any of these strings are found
    'save_sent_images': False,
    'capture-bbox': (0, 0, 1920, 1080)   # x1, y1, x2, y2
    # (700, 700, 1220, 950) maybe faster?
}
