import os, random, json, time
from typing import List, Dict, Optional, Callable

from kcu import kjson, kpath

from utils.objects.bot import Bot
from utils.url_creator import UrlCreator
from utils.bot_flow import bots_flow

### CONFIG ###

NR_OF_USERS_TO_FOLLOW_PER_BOT       = 5
SECONDS_UNTIL_UNFOLLOW              = 4*24*60*60
NUMBER_OF_RANDOM_PINS_TO_REPIN      = 1
CURRENTLY_FOLLOWED_USERS_FILE_NAME  = 'currently_followed_users.json'

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

accs_info = kjson.load(ACCS_PATH)
all_bots = []

for acc_detail in accs_info:
    bot_folder_path = os.path.join(REPINNERS_PATH, acc_detail['username'])

    if not os.path.exists(bot_folder_path):
        os.makedirs(bot_folder_path)
        kjson.save(os.path.join(bot_folder_path, CURRENTLY_FOLLOWED_USERS_FILE_NAME), {})

    all_bots.append(
        Bot(
            acc_detail,
            os.path.join(COOKIES_BASE_PATH, acc_detail['username']),
            EXTENSIONS_BASE_PATH,
            os.path.join(bot_folder_path, CURRENTLY_FOLLOWED_USERS_FILE_NAME)
        )
    )

main_bot = all_bots[0]
repinner_bots = all_bots[1:]
ignored_users = kjson.load(IGNORED_USERS_PATH, default_value={}, save_if_not_exists=True)

def main_flow():
    def save_ignored_users(ignored_users: List[str]):
        kjson.save(IGNORED_USERS_PATH, ignored_users)

    bots_flow(
        main_bot=main_bot,
        bots_not_used=repinner_bots,
        image_to_post_path=os.path.join(FILES_PATH, 'resources/images/image.jpg'),
        post_title='testing this title',
        main_board_name='this is the main',
        search_term_for_boards='men clothes', 
        ignored_users=ignored_users,
        ignored_users_callback=save_ignored_users,
        nr_of_users_to_follow_per_bot=NR_OF_USERS_TO_FOLLOW_PER_BOT,
        seconds_until_unfollow=SECONDS_UNTIL_UNFOLLOW,
        number_of_random_pins_to_repin=NUMBER_OF_RANDOM_PINS_TO_REPIN,
        gr_nr=2
    )

main_flow()