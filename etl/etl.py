import time
from sqlalchemy import create_engine
import pandas as pd
import pymongo

time.sleep(5)

pg = create_engine("postgresql://postgres:postgres@postgresdb:5432/tweet_db", echo=True)

for currency in currencies:
    pg.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {currency}prices (
        index INT,
        close DOUBLE PRECISION,
        time TIMESTAMPTZ,
        sentiment NUMERIC
    );
    SET TIMEZONE to "EUROPE/PARIS";
    """
    )
    df = pd.DataFrame(columns=["close", "time"])

    # Establish a connection to the MongoDB server
    client = pymongo.MongoClient("mongodb")

    # Select the database you want to use withing the MongoDB server
    db = client.prices_data

    # Select the collection of documents you want to use withing the MongoDB database
    collection = db["prices"]

    entries = collection.find()

    dicti = {}
    for e in entries:
        dicti["close"] = e["close"]
        dicti["time"] = e["time"]
        df = df.append(dicti, ignore_index=True)

    df.to_sql(f"{currency}prices", pg, if_exists="append")
