import os

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_PATH = os.path.join(PROJECT_DIR, 'assets')

FB_APP_ID = os.environ['AROUND_THE_BLOCK_FB_APP_ID']
FB_SECRET = os.environ['AROUND_THE_BLOCK_FB_SECRET']

REDIS_PORT = os.environ.get('AROUND_THE_BLOCK_REDIS_PORT', 6379)
