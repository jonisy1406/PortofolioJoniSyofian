import logging

def validate_data(df):
    logging.info("Validating data...")

    # NULL check
    if df.isnull().sum().sum() > 0:
        logging.warning("Null values detected")

    # Duplicate check
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        logging.warning(f"{duplicates} duplicate rows found")

    # Schema check
    required_cols = ['Order Date', 'Sales', 'Profit']
    for col in required_cols:
        if col not in df.columns:
            logging.error(f"Missing column: {col}")
            raise Exception("Schema validation failed")

    return df