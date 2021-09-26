from os import name
import time
import krakenex
import pandas as pd
from pykrakenapi import KrakenAPI
import config


class PortfolioHistory:
    def __init__(self) -> None:
        self.api = krakenex.API(key=config.API_KEY, secret=config.PRIVATE_KEY)
        self.kraken = KrakenAPI(self.api)
        self.current = self.get_current_portfolio()
        self.pairs = self.get_currency_pairs()
        time.sleep(1)
        self.current.insert(0, "pair", self.pairs)
        self.prices_history = None
        self.get_prices_history()

    def get_current_portfolio(self):
        self.account = self.kraken.get_account_balance()
        self.account.drop(index=["ZUSD", "ZEUR"], inplace=True)
        return self.account[self.account["vol"] > 0.001]

    def get_currency_pairs(self):
        all_pairs = self.kraken.get_tradable_asset_pairs()
        euro_pairs = all_pairs.filter(like="EUR", axis=0)
        return [
            euro_pairs[euro_pairs["base"] == currency].index[0]
            for currency in self.current.index.values
        ]

    def get_prices_history(self):
        self.prices_history = pd.DataFrame(columns=self.pairs)
        self.prices_history.to_csv("prices_history.csv", mode="w")

    def save_prices(self, ticker):
        self.prices_history = self.prices_history.append(ticker)
        print(self.prices_history)
        self.prices_history.iloc[-1:][:].to_csv(
            "prices_history.csv", header=False, mode="a+"
        )

    def get_prices(self):
        prices = []
        for currency in self.prices_history.columns.values:
            price = self.kraken.get_ticker_information(currency)["c"][0][0]
            prices.append(price)
            time.sleep(1)
        return prices

    def update_ticker(self):
        while True:
            timestamp = time.time()
            prices = self.get_prices()
            ticker = pd.Series(prices, index=self.pairs, name=timestamp)
            print(ticker)
            self.save_prices(ticker)
            time.sleep(19)


if __name__ == "__main__":
    history = PortfolioHistory()
    history.update_ticker()
