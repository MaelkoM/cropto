import pymongo


class PricesLocker:
    def __init__(self):
        client = pymongo.MongoClient("mongodb")
        self.prices_vault = client.prices_data
        self.prices_col = self.prices_vault["tweets"]

    def store_prices(self, tweet):
        text = tweet["text"]
        handle = tweet["username"]
        followers = tweet["followers_count"]
        new_prices = {"text": text, "handle": handle, "followers": followers}
        self.lock_prices(new_prices)

    def check_prices(self, tweet):
        if self.prices_col.find({"text": tweet["text"]}) != None:
            return False

    def lock_prices(self, prices):
        if self.check_prices(prices) == False:
            self.prices_col.insert_one(prices)
