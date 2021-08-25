from sqlalchemy import create_engine
import time

time.sleep(5)

pg = create_engine("postgresql://postgres:postgres@postgresdb:5432/tweet_db", echo=True)
pg.execute(
    """
    CREATE TABLE IF NOT EXISTS tweets (
    index INT,
    handle VARCHAR(255),
    tweet VARCHAR(500),
    sentiment NUMERIC
);
"""
)
