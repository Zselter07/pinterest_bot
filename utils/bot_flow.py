from typing import List, Dict, Tuple, Optional, Callable
import os, time

from kcu import kjson

from .objects.bot import Bot

def bots_flow(
    main_bot: Bot,
    bots_not_used: List[Bot],
    image_to_post_path: str,
    post_title: str,
    main_board_name: str,
    search_term_for_boards: str,
    ignored_users: List[str],
    ignored_users_callback: Callable[[List[str]], None],
    nr_of_users_to_follow_per_bot: int,
    seconds_until_unfollow: int,
    number_of_random_pins_to_repin: int,
    gr_nr: int,
) -> None:

    ### mainbot task, load ignored users
    number_of_total_users_to_follow = nr_of_users_to_follow_per_bot * len(bots_not_used)
    bots_needing_followers = [main_bot]
    main_posted_pin_id, total_users_to_follow, ignored_users = main_bot.do_mainbot_tasks(image_to_post_path, post_title, main_board_name, search_term_for_boards, ignored_users, number_of_total_users_to_follow)
    ignored_users_callback(ignored_users)

    bot_and_pin_id_pairs = {
        main_bot.username: main_posted_pin_id
    }
    print('main posted pin id:', main_posted_pin_id, 'total users to follow:', total_users_to_follow, 'ignored users:', ignored_users)

    while len(bots_not_used) > 0:
        ### get the pin id for the bot that will get repinned 
        bot_needing_followers = bots_needing_followers[0]

        for bot_username, pin_id in bot_and_pin_id_pairs.items():
            if bot_needing_followers.username == bot_username:
                posted_pin_id = pin_id

        gr_nr_counter = 0

        for bot in list(bots_not_used):
            ### create separate lists of users to follow for each bot and remove those from total users to follow ###
            users_to_follow = []

            users_to_follow.extend(total_users_to_follow[:nr_of_users_to_follow_per_bot])
            total_users_to_follow = total_users_to_follow[nr_of_users_to_follow_per_bot:]

            ### daily task 
            users_to_unfollow = []

            for user_name, timestamp_when_followed in bot.currently_followed_users.items():
                if timestamp_when_followed + seconds_until_unfollow <= time.time():
                    users_to_unfollow.append(user_name)

            print('users to follow:', users_to_follow)
            print('users to unfollow:', users_to_unfollow)
            bot_pin_id = bot.do_repinner_daily_tasks(users_to_follow, users_to_unfollow, number_of_random_pins_to_repin, posted_pin_id, main_board_name)

            bots_not_used.remove(bot)

            if bot_pin_id is None:
                continue

            bot_and_pin_id_pairs[bot.username] = bot_pin_id

            ### update lists
            bots_needing_followers.append(bot)
            gr_nr_counter += 1

            if gr_nr_counter == gr_nr:
                del bots_needing_followers[0]

                break