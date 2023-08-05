import os
from pathlib import Path
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = str(Path.home())
CONFIG_DIR = os.path.join(HOME_DIR, '.tw2gif')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
FFMPEG_SCRIPT = os.path.join(BASE_DIR, 'scripts/video_to_gif.sh')

def setup():
    os.mkdir(CONFIG_DIR)
    settings = {
        'CONSUMER_KEY': input('Consumer key: '),
        'CONSUMER_SECRET': input('Consumer secret: '),
        'ACCESS_TOKEN_KEY': input('Access token key: '),
        'ACCESS_TOKEN_SECRET': input('Access token secret: '),
    }
    with open(CONFIG_FILE, 'w') as f:
        f.write(json.dumps(settings))

if (not os.path.exists(CONFIG_FILE)):
    setup()

settings = ""
with open(CONFIG_FILE) as f:
    settings = json.loads(f.read())

CONSUMER_KEY = settings['CONSUMER_KEY']
CONSUMER_SECRET = settings['CONSUMER_SECRET']
ACCESS_TOKEN_KEY = settings['ACCESS_TOKEN_KEY']
ACCESS_TOKEN_SECRET = settings['ACCESS_TOKEN_SECRET']
