import io
import requests
import time
import zipfile

import pandas as pd
import numpy as np
import tqdm
from sqlalchemy import create_engine
import config


class PostgresCommunicator:
    def __init__(self) -> None:
        self.user = config.DB_USER
        self.password = config.DB_PASSWORD
        self.host = config.DB_ENDPOINT
        self.port = "5432"
        self.database = config.DB_NAME
        self.uri = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = None

    def load_history_tables(self) -> None:
        """
        Loads historic kraken coin data from zip file to a predefined aws sql server, creating new tables (replacing existing ones in the process).
        Get file here: https://support.kraken.com/hc/en-us/articles/360047124832-Downloadable-historical-OHLCVT-Open-High-Low-Close-Volume-Trades-data
        """
        self.start_engine()
        ohlcvt_file = zipfile.ZipFile("data/Kraken_OHLCVT.zip", "r")
        for name in tqdm.tqdm(ohlcvt_file.namelist()):
            if name.endswith("csv"):
                file = ohlcvt_file.read(name)
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

                conn = self.engine.raw_connection()
                cur = conn.cursor()
                output = io.StringIO()
                df.to_csv(output, sep="\t", header=False, index=False)
                output.seek(0)
                cur.copy_from(output, pair.lower(), null="")  # null values become ''
                conn.commit()
            self.stop_engine()

    def store_tweet(self, tweet=dict, currency=str) -> None:
        self.start_engine()
        df = pd.DataFrame(tweet)
        df.head(0).to_sql(
            currency.lower(), self.engine, if_exists="append", index=False
        )  # drops old table and creates new empty table

        conn = self.engine.raw_connection()
        cur = conn.cursor()
        output = io.StringIO()
        df.to_csv(output, sep="\t", header=False, index=False)
        output.seek(0)
        cur.copy_from(output, currency.lower(), null="")  # null values become ''
        conn.commit()
        self.stop_engine()

    def start_engine(self) -> None:
        self.engine = create_engine(self.uri, echo=True)

    def stop_engine(self) -> None:
        self.engine.dispose()


if __name__ == "__main__":
    ohlcvt_file = zipfile.ZipFile("data/Kraken_OHLCVT.zip", "r")
    for file in tqdm.tqdm(ohlcvt_file.namelist()):
        print(file)
