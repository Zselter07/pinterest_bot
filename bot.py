from typing import List, Dict, Optional
from datetime import datetime, timedelta, date
import os.path, time, random

# from selenium_pinterest.selenium_pinterest import Pinterest
from selenium_pinterest import Pinterest
from kov_utils import kjson

# CACHE PATHS

CACHE_PATH = os.path.join(os.path.dirname(__file__), 'files', 'cache')
COOKIES_BASE_PATH = os.path.join(CACHE_PATH, 'cookies')

# RESOURCES PATHS

RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'files', 'resources')
EXTENSIONS_BASE_PATH = os.path.join(RESOURCES_PATH, 'extensions')

class Bot:
    def __init__(self, config: Dict[str, str]):
        self.email_address = config['email_address']
        self.password = config['password']
        self.proxy_host = config['proxy_host'] if 'proxy_host' in config else None
        self.proxy_port = config['proxy_port'] if 'proxy_port' in config else None
        self.username = config['username']

    def login(self) -> None:
        self.session = Pinterest(os.path.join(COOKIES_BASE_PATH, self.username), EXTENSIONS_BASE_PATH, host=self.proxy_host, port=self.proxy_port)

    def repin(self, pin_id: str, board_name: str) -> bool:
        return self.session.repin(pin_id, board_name)

    def follow(self, user_name: str) -> bool:
        return self.session.follow(user_name) 

    def unfollow(self, user_name: str) -> bool:
        return self.session.unfollow(user_name)

    def get_board_followers(self, 
        user_name: str,
        board_name: str,
        ignored_users: List[str],
        number_of_users_to_follow,
        full_board_url: str = None
    ) -> tuple:
        return self.session.get_board_followers(user_name, board_name, ignored_users, number_of_users_to_follow)
    
    def search_pinterest_boards(self, search_term: str, number_of_boards_to_get: int = 35) -> Optional[List[tuple]]:
        return self.session.search_pinterest_boards(search_term, number_of_boards_to_get)
    
    def get_pins_from_home_feed(self) -> Optional[List[str]]:
        return self.session.get_pins_from_home_feed()

    def post_pin(self, 
        file_path: str,
        title_text: str,
        board_name: str,
        about_text: str = None,
        destination_link_text: str = None
    ) -> str:
        return self.session.post_pin(file_path, title_text, board_name, about_text=None, destination_link_text=None)
    
    def get_pin_id_of_repinned_post(self) -> str:
        return self.session.get_link_to_repinned_post() 
    
    def quit(self) -> None:
        self.session.browser.driver.quit()
    
    def do_repinner_daily_tasks(self, 
        users_to_follow: List[str], 
        users_to_unfollow: Dict[str, str],
        main_pin: str, 
        nr_of_days_until_unfollow: int = 3
    ):
        self.login()
        print('logged in to secondary bot')
        # self.session.disable_pop_up()

        ### REPIN SESSION ### 

        home_feed_pins = random.choices(self.get_pins_from_home_feed(), k=3)

        if home_feed_pins is not None:
            self.repin(home_feed_pins[0], 'new board') # do a separate pin so we have atleast 2 boards per bot. 
            for home_pin in home_feed_pins[1:]:
                if self.repin(home_pin, "my stuff"):
                    print('repinned pin nr:', home_pin, 'to:', "my random stuff")
                else:
                    print('did not repin random pin')

        if self.repin(main_pin, "main board"):
            bot_pin_id = self.get_pin_id_of_repinned_post()
            print('repinned main pin id:', bot_pin_id)
            bot_and_pin_id = (Bot, bot_pin_id)
            
        else:
            print('could not repin main pin for some reason')

        ### FOLLOW/UNFOLLOW SESSION ### 

        if users_to_unfollow is not None:
            today = datetime.today()
            _temp_users_unfollowed = []
            for user, date_of_follow_str in users_to_unfollow.items():
                date_of_follow = datetime.strptime(date_of_follow_str, '%Y-%m-%d')

                if date_of_follow + timedelta(days=nr_of_days_until_unfollow) <= today: 
                    print('date of follow that has to be unfollowed', date_of_follow)
                    if self.unfollow(user):
                        _temp_users_unfollowed.append(user)
                        print('unfollowed user:', user)
                
            for user in _temp_users_unfollowed:
                del users_to_unfollow[user]
                print('removed', user, 'from users_to_unfollow')

        for user in users_to_follow:
            print('the user to be followed:', user)
            if self.follow(user):
                print('followed:', user)
                users_to_unfollow[user] = datetime.today().strftime('%Y-%m-%d')

        # self.quit()
        time.sleep(0.5)

        return bot_and_pin_id, users_to_unfollow

    def do_mainbot_tasks(self,
        file_path: str,
        title_text: str,
        board_name_to_post_to: str,
        board_search_term_to_get_users: str, # search for boards after a search term
        ignored_users: List[str], # already followed users
        number_of_users_to_follow,
        about_text: str = None,
        destination_link_text: str = None
    ) -> str:
        self.login()
        print('logged in to mainbot')
        pin_id = self.post_pin(file_path, title_text, board_name_to_post_to, about_text, destination_link_text)
        print('pin id for mainbot is:', pin_id)
        time.sleep(3)
        user_and_board_names = self.search_pinterest_boards(board_search_term_to_get_users)
        print(user_and_board_names)

        for tup in user_and_board_names:
            user_name, board_name = tup
            users_to_follow, ignored_users = self.get_board_followers(user_name, board_name, ignored_users, number_of_users_to_follow=number_of_users_to_follow)

            if len(users_to_follow) != number_of_users_to_follow:
                continue

            break

        print('users_to_follow:', users_to_follow)
        self.quit()

        return (pin_id, users_to_follow, ignored_users)

### TESTING ### 

# RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'files', 'resources')
# CONFIG_PATH = os.path.join(RESOURCES_PATH, 'config.json')
# ignored_users = kjson.load(os.path.join(RESOURCES_PATH, 'ignored_users.json'))
# accs_info = kjson.load(CONFIG_PATH)

# bot = Bot(accs_info[1])
# bot.login()

# bot = Pinterest('/Users/macbook/github_desktop/pinterest_bot/files/cache/cookies/redditstories08', '/Users/macbook/github_desktop/pinterest_bot/files/resources/extensions')

# print(bot.unfollow('alessandradiva2013'))

# users = ['tonisweeneyofficial', 'HealthCentral']

# for user in users:
#     if bot.follow(user):
#         print('followed', user)