import os
from pathlib import Path

class Config:
    
    API_ID = int(os.environ.get('API_ID', 1667813))
    API_HASH = os.environ.get('API_HASH', '1f6921c27bf6cd01aba471a14ff33bcb')
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '1363050429:AAGZjh0i0sawiP82uRHA9K6wQcksVOPboSs')
    SESSION_NAME = os.environ.get('SESSION_NAME', 'AIsnapshotbot')
    LOG_CHANNEL = int(os.environ.get('LOG_CHANNEL', '-1001457404263'))
    DATABASE_URL = os.environ.get('DATABASE_URL')
    AUTH_USERS = [int(i) for i in os.environ.get('AUTH_USERS', '960156861 1326703864 1004538768').split(' ')]
    MAX_PROCESSES_PER_USER = int(os.environ.get('MAX_PROCESSES_PER_USER', 2))
    MAX_TRIM_DURATION = int(os.environ.get('MAX_TRIM_DURATION', 600))
    TRACK_CHANNEL = int(os.environ.get('TRACK_CHANNEL', '-1001457404263'))
    SLOW_SPEED_DELAY = int(os.environ.get('SLOW_SPEED_DELAY', 5))
    HOST = os.environ.get('HOST', 'https://ai-tgstream.herokuapp.com')
    TIMEOUT = int(os.environ.get('TIMEOUT', 60 * 30))
    DEBUG = bool(os.environ.get('DEBUG'))
    
    SCRST_OP_FLDR = Path('screenshots/')
    SMPL_OP_FLDR = Path('samples/')
    THUMB_OP_FLDR = Path('thumbnails/')
    COLORS = ['white', 'black', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'brown', 'gold', 'silver', 'pink']
    FONT_SIZES_NAME = ['Small', 'Medium', 'Large']
    FONT_SIZES = [30, 40, 50]
