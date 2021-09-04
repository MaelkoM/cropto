import io
import os
import time

import krakenex
import matplotlib
import pandas as pd
import psycopg2
import tqdm
from numpy.core.defchararray import endswith
from numpy.lib.function_base import select
from pykrakenapi import KrakenAPI
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    desc,
    func,
    inspect,
    select,
    text,
)

import config

OTP = 632390
user = "postgres"
password = "postgres"
host = "127.0.0.1"
port = "5432"
database = "cropto"
uri = f"postgresql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(uri, echo=True)
metadata = MetaData()
insp = inspect(engine)

api = krakenex.API(key=config.API_KEY, secret=config.PRIVATE_KEY)
k = KrakenAPI(api)
account = k.get_account_balance()
account.drop(index=["ZUSD", "ZEUR"], inplace=True)
print(account)
current = account[account["vol"] > 0.001]

all_pairs = k.get_tradable_asset_pairs()
euro_pairs = all_pairs.filter(like="EUR", axis=0)
pairs = [
    euro_pairs[euro_pairs["base"] == currency].index[0]
    for currency in current.index.values
]
time.sleep(1)
# help(KrakenAPI)
current.insert(0, "pair", pairs)
prices_history = pd.DataFrame(columns=pairs)
prices_history.to_csv("prices_history.csv", mode="w")
while True:
    timestamp = time.time()
    prices = k.get_ticker_information(prices_history.columns.values)
    print(prices)
    prices.append(prices)
    time.sleep(60)
    ticker = pd.Series(prices, index=pairs, name=timestamp)
    print(ticker)
    prices_history = prices_history.append(ticker)
    print(prices_history)
    prices_history.iloc[-1][:].to_csv("prices_history.csv", header=False, mode="a+")
