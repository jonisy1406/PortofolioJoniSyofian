from scripts.extract import extract_data
from scripts.validate import validate_data
from scripts.transform import transform_data
from scripts.load import load_to_db
from scripts.logger import setup_logger

import logging

def run_pipeline():
    setup_logger()

    try:
        logging.info("Pipeline started")

        df = extract_data("data/raw/Superstore.csv")
        df = validate_data(df)
        df = transform_data(df)

        df.to_csv("data/processed/clean_data.csv", index=False)

        load_to_db(df)

        logging.info("Pipeline finished successfully")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    run_pipeline()