from typing import List, Dict, Tuple, Optional, Callable
import os, time

from kcu import kjson

from .objects import Bot

def bots_flow(
    main_bot: Bot,
    bots_not_used: List[Bot],
    image_to_post_path: str,
    post_title: str,
    main_board_name: str,
    search_term_for_boards: str,
    ignored_users: List[str],
    save_ignored_users: Callable[List[str], None],
    NR_OF_USERS_TO_FOLLOW_PER_BOT: int,
    SECONDS_UNTIL_UNFOLLOW: int,
    NUMBER_OF_RANDOM_PINS_TO_REPIN: int,
    gr_nr: int=2,
) -> None:

    ### mainbot task, load ignored users
    number_of_total_users_to_follow = NR_OF_USERS_TO_FOLLOW_PER_BOT * len(bots_not_used)
    bots_needing_followers = [main_bot]
    main_posted_pin_id, total_users_to_follow, ignored_users = main_bot.do_mainbot_tasks(image_to_post_path, post_title, main_board_name, search_term_for_boards, ignored_users, number_of_users_to_follow=number_of_total_users_to_follow)
    # kjson.save(IGNORED_USERS_PATH, ignored_users)
    save_ignored_users(ignored_users)

    bot_and_pin_id_pairs = {
        main_bot: main_posted_pin_id
    }
    print('main posted pin id:', main_posted_pin_id, 'total users to follow:', total_users_to_follow, 'ignored users:', ignored_users)

    while len(bots_not_used) > 0:

        ### get the pin id for the bot that will get repinned 

        bot_needing_followers = bots_needing_followers[0]

        for bot, pin_id in bot_and_pin_id_pairs.items():
            if bot_needing_followers == bot:
                posted_pin_id = pin_id

        gr_nr_counter = 0

        for bot in list(bots_not_used):

            ### create separate lists of users to follow for each bot and remove those from total users to follow ###

            users_to_follow = []
            
            for _ in range(NR_OF_USERS_TO_FOLLOW_PER_BOT):
                users_to_follow.append(total_users_to_follow.pop())

            ### daily task 
            
            currently_followed_users = bot.currently_followed_users
            print('users to unfollow after loading in manager: ', currently_followed_users)
            users_to_unfollow = []

            for user, seconds_when_followed in currently_followed_users.items():
                if seconds_when_followed + SECONDS_UNTIL_UNFOLLOW <= int(time.time()):
                    users_to_unfollow.append(user)

            bot_pin_id, new_followed_users = bot.do_repinner_daily_tasks(users_to_follow, 
                                                                        users_to_unfollow, NUMBER_OF_RANDOM_PINS_TO_REPIN, posted_pin_id,main_board_name)

            bot_and_pin_id_pairs[bot] = bot_pin_id
            currently_followed_users.update(new_followed_users)

            ### save users to unfollow json ### 

            kjson.save(bot.followed_users_path, currently_followed_users) 

            ### update lists

            bots_needing_followers.append(bot)
            bots_not_used.remove(bot)
            gr_nr_counter += 1

            if gr_nr_counter == gr_nr:
                del bots_needing_followers[0]

                break