from typing import List, Dict, Optional, Tuple, Callable
from datetime import datetime, timedelta, date
import os.path, time, random

from selenium_pinterest import Pinterest
from kcu import rand, kjson

class Bot:
    def __init__(self, config: Dict[str, str], cookies_path: str, extensions_path: str, followed_users_path: str):
        self.cookies_path = cookies_path
        self.extensions_path = extensions_path
        self.proxy_host = config['proxy_host'] if 'proxy_host' in config else None
        self.proxy_port = config['proxy_port'] if 'proxy_port' in config else None
        self.username = config['username']
        self.followed_users_path = followed_users_path
        self.currently_followed_users = kjson.load(followed_users_path)

    def login(self) -> None:
        self.session = Pinterest(self.cookies_path, self.extensions_path, host=self.proxy_host, port=self.proxy_port)

    def repin(self, pin_id: str, board_name: str, needs_repin_id: bool=False) -> Tuple[bool, Optional[str]]:
        return self.session.repin(pin_id, board_name, needs_repin_id=needs_repin_id)

    def follow(self, user_name: str) -> bool:
        return self.session.follow(user_name) 

    def unfollow(self, user_name: str) -> bool:
        return self.session.unfollow(user_name)

    def get_board_followers(
        self, 
        user_name: str,
        board_name: str,
        ignored_users: List[str],
        number_of_users_to_follow,
        full_board_url: str = None
    ) -> Optional[Tuple[List[str], List[str]]]:
        return self.session.get_board_followers(user_name, board_name, ignored_users, number_of_users_to_follow,    full_board_url=full_board_url)
    
    def search_pinterest_boards(self, search_term: str, number_of_boards_to_get: int = 35) -> Optional[List[Tuple[str, str]]]:
        return self.session.search_pinterest_boards(search_term, number_of_boards_to_get)
    
    def get_pins_from_home_feed(self) -> Optional[List[str]]:
        return self.session.get_pins_from_home_feed()

    def post_pin(
        self, 
        file_path: str,
        title_text: str,
        board_name: str,
        about_text: str = None,
        destination_link_text: str = None
    ) -> Optional[str]:
        return self.session.post_pin(file_path, title_text, board_name, about_text=about_text, destination_link_text=destination_link_text)
    
    def quit(self) -> None:
        self.session.browser.driver.quit()
    
    def do_repinner_daily_tasks(
        self, 
        users_to_follow: List[str], 
        users_to_unfollow: List[str],
        number_of_random_pins_to_repin: int,
        main_pin: str,
        main_board_name: str,
        first_random_board: str = "best posts",
        second_random_board: str = "my random stuff"
    ) -> Tuple[Optional[str], Dict[str, int]]:
        self.login()
        print('logged in to secondary bot')

        ### REPIN SESSION ### 

        home_feed_pins = random.choices(self.get_pins_from_home_feed(), k=number_of_random_pins_to_repin)

        if home_feed_pins is not None:
            self.repin(home_feed_pins[0], first_random_board) #do a separate pin so we have atleast 2 boards per bot as Pinterest acts differently this way.
            for home_pin in home_feed_pins[1:]:
                feed_pin_status, _ = self.repin(home_pin, second_random_board)
                if feed_pin_status:
                    print('repinned pin nr:', home_pin, 'to:', second_random_board)
                else:
                    print('did not repin random pin')

        main_pin_status, bot_pin_id = self.repin(main_pin, main_board_name, needs_repin_id=True)
        
        if main_pin_status:
            print('repinned main pin id:', bot_pin_id)
        else:
            print('could not repin main pin for some reason')

        ### FOLLOW/UNFOLLOW SESSION ### 

        for user in users_to_unfollow:
            print('the user to be unfollowed:', user)
            
            if self.unfollow(user):
                print('unfollowed:', user)
                del self.currently_followed_users[user]

        for user in users_to_follow:
            print('the user to be followed:', user)

            if self.follow(user):
                print('followed:', user)
                self.currently_followed_users[user] = time.time()
        
        kjson.save(self.followed_users_path, self.currently_followed_users)
        self.quit()
        rand.sleep(0.5, 1)

        return bot_pin_id

    def do_mainbot_tasks(
        self,
        file_path: str,
        title_text: str,
        board_name_to_post_to: str,
        board_search_term_to_get_users: str,
        ignored_users: List[str],
        number_of_users_to_follow: int,
        about_text: str = None,
        destination_link_text: str = None
    ) -> Tuple[Optional[str], List[str], List[str]]:
        self.login()
        print('logged in to mainbot')
        pin_id = self.post_pin(file_path, title_text, board_name_to_post_to, about_text, destination_link_text)
        print('pin id for mainbot is:', pin_id)
        rand.sleep(2, 3)
        user_and_board_names = self.search_pinterest_boards(board_search_term_to_get_users)

        for user_name, board_name in user_and_board_names:
            users_to_follow, ignored_users = self.get_board_followers(user_name, board_name, ignored_users, number_of_users_to_follow=number_of_users_to_follow)

            if len(users_to_follow) != number_of_users_to_follow:
                continue

            break

        print('users_to_follow:', users_to_follow)
        # self.quit()

        return pin_id, users_to_follow, ignored_users