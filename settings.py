# https://myaccount.google.com/apppasswords

# possible game states:
# Matching
# Loading loot
# Awaiting session start
# Waiting players
# Deploying
# Unknown

userInfo = {
    'number': 1234567890,
    'provider': 'Provider',  # check info.py for the exact name of your provider
    'email': 'email@gmail.com',
    'app_password': 'qwertyuiopasdfgh',
    'screen_width': 1920,
    'screen_height': 1080
}

# ('string found', 'game state')
states = [
    ('Matching', 'Matching'),
    ('loot', 'Loading loot'),
    ('Awaiting', 'Awaiting session start'),
    ('Waiting', 'Waiting for players'),
    ('Deploying',  'Deploying'),
]

Settings = {
    'debug_mode': False,
    'see-what-the-computer-sees': False,
    'threshold': 110,
    'screen_capture_delay': 1,
    'message_type': 'mms',  # sms, mms
    'notify_on': ['Loading loot', 'Waiting for players', 'Deploying'],
    'quit_on': ['Deploying'],
    'save_sent_images': False
}
