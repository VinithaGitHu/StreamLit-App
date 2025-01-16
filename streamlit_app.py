import streamlit as st
import pandas as pd
import pymssql

# Database connection details
SERVER_NAME = "LAPTOP-9MQOKA1D"
DB_NAME = "DE_DWHM_DB"
USER = "your_username"
PASSWORD = "your_password"
TABLE_NAME = "FileCompare"
SCHEMA_NAME = "dbo"

def fetch_data():
    """Fetch data using pymssql with SQL Server Authentication."""
    try:
        conn = pymssql.connect(server=SERVER_NAME, user=USER, password=PASSWORD, database=DB_NAME)
        query = f"SELECT * FROM {SCHEMA_NAME}.{TABLE_NAME}"
        df = pd.read_sql(query, conn)
        conn.close()
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
