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
    'provider': 'Provider',  # check info.py
    'email': 'email@gmail.com',
    'app_password': 'qwertyuiopasdfgh',
    'screen_width': 1920,
    'screen_height': 1080
}

Settings = {
    'debug_mode': False,
    'see-what-the-computer-sees': False,
    'threshold': 110,
    'screen_capture_delay': 1,
    'message_type': 'sms',  # sms(faster with no image), mms(slower with image)
    'notify_on': ['Loading loot', 'Waiting for players', 'Deploying']
}
