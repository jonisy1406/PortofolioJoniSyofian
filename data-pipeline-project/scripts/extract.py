import pandas as pd
import logging
import chardet

def detect_encoding(path, n_bytes=10000):
    with open(path, "rb") as f:
        result = chardet.detect(f.read(n_bytes))
    return result["encoding"]

def extract_data(path):
    logging.info("Extracting data...")

    try:
        # 1. Detect encoding
        encoding = detect_encoding(path)
        logging.info(f"Detected encoding: {encoding}")

        # 2. Read file
        df = pd.read_csv(path, encoding=encoding)

    except Exception as e:
        logging.warning(f"Failed with detected encoding: {e}")
        logging.info("Fallback to latin-1 with replace mode")

        # 3. Fallback 
        df = pd.read_csv(path, encoding="latin-1", errors="replace")

    # 4. Basic cleaning (handle NBSP 0xa0)
    df = df.replace('\xa0', ' ', regex=True)

    # 5. Logging metadata
    logging.info(f"Data shape: {df.shape}")
    logging.info(f"Columns: {list(df.columns)}")

    # 6. Validasi sederhana
    if df.empty:
        logging.error("Data is empty!")
        raise ValueError("Extracted data is empty")

    return df
