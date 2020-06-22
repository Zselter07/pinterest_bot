import os, random, json
from typing import List, Dict

from kcu import kjson, kpath

from bot import Bot
from utils.url_creator import UrlCreator

### PATHS 

FILES_PATH = os.path.join(os.path.dirname(__file__), 'files')
CACHE_PATH = os.path.join(FILES_PATH, 'cache')
RESOURCES_PATH = os.path.join(FILES_PATH, 'resources')
CONFIG_PATH = os.path.join(RESOURCES_PATH, 'config.json')
IGNORED_USERS_PATH = os.path.join(CACHE_PATH, 'ignored_users.json')

os.makedirs(CACHE_PATH, exist_ok=True)
os.makedirs(FILES_PATH, exist_ok=True)
os.makedirs(RESOURCES_PATH, exist_ok=True)

### create bot objects from config

accs_info = kjson.load(CONFIG_PATH)
bots_container = []

for acc_detail in accs_info[1:]:
    bot = Bot(acc_detail)
    bots_container.append(bot)

mainbot = Bot(accs_info[0])

### CONFIG ### 

nr_of_users_to_follow_per_bot = 2
NUMBER_OF_USERS_TO_FOLLOW = nr_of_users_to_follow_per_bot * len(bots_container) 

def bots_flow(bots_not_used: List[Bot], gr_nr: int=2):

    ### mainbot task, load ignored users

    bots_needing_followers = [mainbot]
    ignored_users = kjson.load(IGNORED_USERS_PATH, default_value={}, save_if_not_exists=True)

    main_posted_pin_id, total_users_to_follow, ignored_users = mainbot.do_mainbot_tasks('/Users/macbook/github_desktop/pinterest_bot/files/resources/images/image.jpg', 'this title is cool', 'my main board', 'baby gift', ignored_users,number_of_users_to_follow=NUMBER_OF_USERS_TO_FOLLOW)
    kjson.save(IGNORED_USERS_PATH, ignored_users)
    bot_and_pin_id_pairs = [(mainbot, main_posted_pin_id)]

    print('main posted pin id:', main_posted_pin_id, 'total users to follow:', total_users_to_follow, 'ignored users:', ignored_users)

    while len(bots_not_used) > 0:

        ### get the pin id for the bot that will get repinned 

        elem = bots_needing_followers[0]

        for tup in bot_and_pin_id_pairs:
            if elem in tup:
                posted_pin_id = tup[1]

        gr_nr_counter = 0

        for bot in list(bots_not_used):

            ### create separate lists of users to follow for each bot and remove those from total users to follow ###

            users_to_follow = []
            
            for _ in total_users_to_follow:
                user = total_users_to_follow.pop()
                users_to_follow.append(user)

                if len(users_to_follow) == nr_of_users_to_follow_per_bot:
                    break

            ### daily task 

            path_of_bot = os.path.join(CACHE_PATH, 'repinners', bot.username)
            path_of_users_to_unfollow = os.path.join(path_of_bot, 'users_to_unfollow.json')

            if not os.path.exists(path_of_bot):
                os.makedirs(path_of_bot)
                empty_dict = {}
                kjson.save(path_of_users_to_unfollow, empty_dict)
            
            users_to_unfollow = kjson.load(path_of_users_to_unfollow)
            print('users to unfollow after loading in manager: ', users_to_unfollow)

            bot_and_pin_id, users_to_unfollow = bot.do_repinner_daily_tasks(users_to_follow, users_to_unfollow, posted_pin_id,
                                                nr_of_days_until_unfollow = 2)
            bot_and_pin_id_pairs.append(bot_and_pin_id)

            ### save users to unfollow json ### 

            kjson.save(path_of_users_to_unfollow, users_to_unfollow) 

            ### update lists

            bots_needing_followers.append(bot)
            bots_not_used.remove(bot)
            gr_nr_counter += 1

            if gr_nr_counter == gr_nr:
                del bots_needing_followers[0]

                break

bots_flow(bots_container)