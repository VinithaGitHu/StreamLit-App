import streamlit as st
import pandas as pd
import pyodbc

# Database connection details
SERVER_NAME = "LAPTOP-9MQOKA1D"
DB_NAME = "DE_DWHM_DB"
TABLE_NAME = "FileCompare"
SCHEMA_NAME = "dbo"

def fetch_data():
    """Fetch data using pyodbc."""
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER_NAME};"
            f"DATABASE={DB_NAME};"
            f"Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str)
        query = f"SELECT * FROM {SCHEMA_NAME}.{TABLE_NAME}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
        return None

st.title("SQL Server Table Viewer")
data = fetch_data()
if data is not None:
    st.dataframe(data)
else:
    st.warning("No data available or an error occurred.")
