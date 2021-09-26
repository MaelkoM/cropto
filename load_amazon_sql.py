import io
import os
import time

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
        self.engine = create_engine(self.uri, echo=True)
        self.timestamp = int(time.time() * 1000)


def load_history_tables(self) -> None:
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
                pair.lower(), self.engine, if_exists="replace", index=False
            )  # drops old table and creates new empty table

            conn = self.engine.raw_connection()
            cur = conn.cursor()
            output = io.StringIO()
            df.to_csv(output, sep="\t", header=False, index=False)
            output.seek(0)
            contents = output.getvalue()
            cur.copy_from(output, pair.lower(), null="")  # null values become ''
            conn.commit()
