import os, random, json, time
from typing import List, Dict, Optional, Callable

from kcu import kjson, kpath

from utils.objects.bot import Bot
from utils.url_creator import UrlCreator
from utils.bot_flow import bots_flow

### PATHS 

FILES_PATH = os.path.join(os.path.dirname(__file__), 'files')
CACHE_PATH = os.path.join(FILES_PATH, 'cache')
RESOURCES_PATH = os.path.join(FILES_PATH, 'resources')
ACCS_PATH = os.path.join(RESOURCES_PATH, 'accs.json')
IGNORED_USERS_PATH = os.path.join(CACHE_PATH, 'ignored_users.json')
COOKIES_BASE_PATH = os.path.join(CACHE_PATH, 'cookies')
EXTENSIONS_BASE_PATH = os.path.join(RESOURCES_PATH, 'extensions')
REPINNERS_PATH = os.path.join(CACHE_PATH, 'repinners')

os.makedirs(CACHE_PATH, exist_ok=True)
os.makedirs(FILES_PATH, exist_ok=True)
os.makedirs(RESOURCES_PATH, exist_ok=True)
os.makedirs(COOKIES_BASE_PATH, exist_ok=True)
os.makedirs(EXTENSIONS_BASE_PATH, exist_ok=True)
os.makedirs(REPINNERS_PATH, exist_ok=True)

### create bot objects from config

accs_info = kjson.load(ACCS_PATH)
all_bots = [Bot(acc_detail, os.path.join(COOKIES_BASE_PATH, acc_detail['username']), EXTENSIONS_BASE_PATH, os.path.join(REPINNERS_PATH, acc_detail['username'])) for acc_detail in accs_info]
main_bot = all_bots[0]
repinner_bots = all_bots[1:]

### CONFIG ### 

NR_OF_USERS_TO_FOLLOW_PER_BOT = 3
SECONDS_UNTIL_UNFOLLOW = 4*24*60*60
NUMBER_OF_RANDOM_PINS_TO_REPIN = 3

ignored_users = kjson.load(IGNORED_USERS_PATH, default_value={}, save_if_not_exists=True)

def main_flow():
    def save_ignored_users(ignored_users: List[str]=ignored_users):
        kjson.save(IGNORED_USERS_PATH, ignored_users)

    bots_flow(main_bot, repinner_bots, '/Users/macbook/github_desktop/pinterest_bot/files/resources/images/image.jpg', 'testing this title', 'this is the main board', 'baby clothes', ignored_users, save_ignored_users, NR_OF_USERS_TO_FOLLOW_PER_BOT, SECONDS_UNTIL_UNFOLLOW, NUMBER_OF_RANDOM_PINS_TO_REPIN, 3)

main_flow()

    

