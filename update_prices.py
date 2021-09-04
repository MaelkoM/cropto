import io
import os
import time

import krakenex
import matplotlib
import pandas as pd
import psycopg2
import tqdm
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

dataframes = {}

timestamp = int(time.time() * 1000)
currency_pair_tables = insp.get_table_names()
for table in tqdm.tqdm(currency_pair_tables):
    print(table)
    t = """SELECT "timestamp" FROM "XRPEUR_1" ORDER BY "timestamp" DESC LIMIT 1;"""
    # print(t)
    # timestamp = cur.execute(t)
    # print(timestamp)
    conn = engine.raw_connection()
    cur = conn.cursor()
    cur.execute(t)
    timestamp = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(timestamp)
    pair = table.split("_")[0]
    interval = table.split("_")[1]
    print(pair, interval)
    ohlc = k.get_ohlc_data(pair=pair, ascending=True, interval=interval)[0]
    ohlc.rename(columns={"count": "trades"}, inplace=True)
    ohlc.index.rename("timestamp", inplace=True)
    ohlc.drop(columns=["vwap", "time"], inplace=True)
    ohlc = ohlc[ohlc.index > timestamp]
    ohlc.reset_index(level=0, inplace=True)
    # code below thanks to Aseem @ https://stackoverflow.com/questions/23103962/how-to-write-dataframe-to-postgres-table
    output = io.StringIO()
    ohlc.to_csv(output, sep="\t", header=False, index=False, chunksize=10000)
    output.seek(0)
    contents = output.getvalue()
    conn = engine.raw_connection()
    cur = conn.cursor()
    cur.copy_from(output, table, null="")  # null values become ''
    cur.close()
    conn.close()

