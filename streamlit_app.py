from sqlalchemy import create_engine
import pandas as pd

# Database connection details
SERVER_NAME = "LAPTOP-9MQOKA1D"
DB_NAME = "DE_DWHM_DB"
TABLE_NAME = "FileCompare"
SCHEMA_NAME = "dbo"

def fetch_data():
    try:
        # Create the SQLAlchemy engine
        engine = create_engine(f"mssql+pymssql://{SERVER_NAME}/{DB_NAME}")
        # Query the table and fetch data into a DataFrame
        query = f"SELECT * FROM {SCHEMA_NAME}.{TABLE_NAME}"
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
        return df
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

data = fetch_data()
if data is not None:
    print(data)
