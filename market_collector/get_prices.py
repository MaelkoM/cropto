import time
import logging
import pandas
import krakenex
from pykrakenapi import KrakenAPI
import config
from prices_locker_mongodb import PricesLocker as pl


pl = pl()

if __name__ == "__main__":
    api = krakenex.API(key=config.API_KEY, secret=config.PRIVATE_KEY)
    k = KrakenAPI(api)
    prices = k.get_asset_info()
    pl.store_prices(prices)


# tweet = {
#         'text': "text",
#         'username': "status.user.screen_name",
#         'followers_count': "status.user.followers_count"
#     }
# tl.store_tweet(tweet)

# gts.tweet_listener(100)
