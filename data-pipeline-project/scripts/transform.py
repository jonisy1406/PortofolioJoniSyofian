import pandas as pd
import logging

def transform_data(df):
    logging.info("Transforming data...")

    # convert date
    df['Order Date'] = pd.to_datetime(df['Order Date'])

    # create new column
    df['Revenue'] = df['Sales'] - df['Profit']

    # remove duplicates
    df = df.drop_duplicates()

    # business rule
    if (df['Revenue'] < 0).any():
        logging.warning("Negative revenue found")

    return df