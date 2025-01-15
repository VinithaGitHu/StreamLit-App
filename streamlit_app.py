import pyodbc
import pandas as pd
import streamlit as st

# Streamlit app setup
st.title("ODBC Data Fetch and Display")

# Input parameters (from user or fixed configuration)
odbc_name = "DE_DWHM_DB"
server_name = "LAPTOP-9MQOKA1D"
db_name = "DE_DWHM_DB"
table_name = "FileCompare"

def fetch_data():
    """Fetches data from the SQL Server table."""
    try:
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_name};DATABASE={db_name};Trusted_Connection=yes;Connection Timeout=30;"
        conn = pyodbc.connect(connection_string)
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        conn.close()
        st.success("Data fetched successfully!")
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Main process
if st.button("Fetch Data"):
    st.info("Fetching data from SQL Server...")
    data = fetch_data()

    if data is not None:
        st.info("Displaying data...")
        st.dataframe(data)
