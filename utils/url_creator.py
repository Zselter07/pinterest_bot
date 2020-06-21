import urllib.parse

BASE_URL = "https://www.pinterest.com/"
class UrlCreator:

    @staticmethod
    def pin_url(pin_id: str):
        return BASE_URL + "pin/" + pin_id

    @staticmethod
    def user_url(user_name: str):
        return BASE_URL + user_name

    @staticmethod
    def board_url(user_name: str, board_name: str):
        return BASE_URL + user_name + '/' + board_name

    @staticmethod
    def search_board_url(search_term: str):
        search_term_validated = urllib.parse.quote(search_term)

        return BASE_URL + "search/boards/?q=" + search_term_validated
    
    @staticmethod
    def home_feed_url():
        return BASE_URL + 'homefeed'
    
    @staticmethod
    def pin_builder_url():
        return BASE_URL + 'pin-builder'
    
    @staticmethod
    def pins_api_url(
        search_term: str, 
        bookmarks: str,
        page_size: int=250):
        encoded_search_term = urllib.parse.quote(search_term)
        base_url = "https://www.pinterest.com/resource/BaseSearchResource/get/?source_url=/search/pins/?q=" + encoded_search_term + "&data="

        data_dict = {"options":{"page_size":page_size,
                    "query":search_term,
                    "scope":"pins",
                    "bookmarks":[bookmarks],
                    "field_set_key":"unauth_react"
                        },
            "context":{}
            }

        final_data = str(data_dict).replace(' ', '').replace('\'', "\"")
        url_ending = urllib.parse.quote(str(final_data))

        return base_url + url_ending