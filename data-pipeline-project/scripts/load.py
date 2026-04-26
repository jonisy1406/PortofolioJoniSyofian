from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import logging

def load_to_db(df):
    logging.info("Loading to database...")

    url = URL.create(
        drivername="postgresql",
        username="postgres",
        password="Test123",
        host="localhost",
        port=5432,
        database="sales_db"
    )

    engine = create_engine(url)

    df.to_sql("sales_data", engine, if_exists="replace", index=False)

    logging.info("Data loaded successfully")