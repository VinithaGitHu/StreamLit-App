import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Database connection details
SERVER_NAME = "LAPTOP-9MQOKA1D"
DB_NAME = "DE_DWHM_DB"
TABLE_NAME = "FileCompare"
SCHEMA_NAME = "dbo"

def fetch_data():
    """Fetch data using sqlalchemy."""
    try:
        conn_str = f"mssql+pyodbc://{SERVER_NAME}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        engine = create_engine(conn_str)
        query = f"SELECT * FROM {SCHEMA_NAME}.{TABLE_NAME}"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
        return None

# Streamlit app
st.title("SQL Server Table Viewer")
data = fetch_data()
if data is not None:
    st.dataframe(data)
else:
    st.warning("No data available or an error occurred.")
