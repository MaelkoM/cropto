import config
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
import logging
import time

import database_manager as dm


def authenticate():
    """Function for handling Twitter Authentication. Please note
    that this script assumes you have a file called config.py
    which stores the 4 required authentication tokens:

    1. API_KEY
    2. API_SECRET
    3. ACCESS_TOKEN
    4. ACCESS_TOKEN_SECRET
    """
    auth = OAuthHandler(config.TWITTER_API_KEY, config.TWITTER_API_SECRET)
    auth.set_access_token(
        config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET
    )

    return auth


class MaxTweetsListener(StreamListener):
    def __init__(self, max_tweets, *args, **kwargs):
        # initialize the StreamListener
        super().__init__(*args, **kwargs)
        # set the instance attributes
        self.max_tweets = max_tweets
        self.counter = 0
        self.tl = tl()
        logging.basicConfig(format="%(asctime)s %(message)s", filename="streaming.log")

    def on_connect(self):
        logging.info("connected. listening for incoming tweets")
        print("connected. listening for incoming tweets")

    def on_status(self, status):
        """
        Stores tweet in psql database.
        Info stored: timestamp, text, user, follower count and currency.
        """

        # increase the counter
        self.counter += 1

        tweet = {
            "timestamp": int(time.time() * 1000),
            "text": status.text,
            "username": status.user.screen_name,
            "followers_count": status.user.followers_count,
        }
        dm.store_tweet(tweet)
        logging.info(f'New tweet arrived: {tweet["text"]}')
        print(f'New tweet arrived: {tweet["text"]}')

        # check if we have enough tweets collected
        if self.max_tweets == self.counter:
            # reset the counter
            self.counter = 0
            # return False to stop the listener
            return False

    def on_error(self, status):
        if status == 420:
            logging.warning("Rate limit applies. Stop the stream.")
            print(f"Rate limit applies. Stop the stream.")
            return False


def tweet_listener(max_tweets):
    auth = authenticate()
    listener = MaxTweetsListener(max_tweets)
    stream = Stream(auth, listener)
    stream.filter(track=["berlin"], languages=["en"], is_async=False)
