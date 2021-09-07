import io
import os
import time

import krakenex
import matplotlib
import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy.sql.expression import column
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

user = config.DB_USER
password = config.DB_PASSWORD
host = config.DB_ENDPOINT
port = "5432"
database = config.DB_NAME
uri = f"postgresql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(uri, echo=True)
metadata = MetaData()

dataframes = {}

timestamp = int(time.time() * 1000)

for file in tqdm.tqdm(os.listdir("data/Kraken_OHLCVT")):
    if file.endswith("csv"):
        pair = file.split(".")[0].lower()
        print(pair)
        df = pd.read_csv(
            "data/Kraken_OHLCVT/" + file,
            sep=",",
            names=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "trades",
                "vwap",
            ],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df["vwap"] = np.cumsum(
            df["volume"] * (df["open"] * df["high"] * df["close"]) / 3
        ) / np.cumsum(df["volume"])
        print(df)

        df.head(0).to_sql(
            pair.lower(), engine, if_exists="replace", index=False
        )  # drops old table and creates new empty table

        conn = engine.raw_connection()
        cur = conn.cursor()
        output = io.StringIO()
        df.to_csv(output, sep="\t", header=False, index=False)
        output.seek(0)
        contents = output.getvalue()
        cur.copy_from(output, pair.lower(), null="")  # null values become ''
        conn.commit()

