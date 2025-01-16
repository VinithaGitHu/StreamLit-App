import streamlit as st
import pandas as pd
import pyodbc

# Database connection details
SERVER_NAME = "LAPTOP-9MQOKA1D"
DB_NAME = "DE_DWHM_DB"
TABLE_NAME = "FileCompare"
SCHEMA_NAME = "dbo"

def fetch_data():
    """Fetches data from the specified table in the database."""
    try:
        # Establishing connection
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER_NAME};"
            f"DATABASE={DB_NAME};"
            f"Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str)
        query = f"SELECT * FROM {SCHEMA_NAME}.{TABLE_NAME}"
        # Execute the query and fetch data into a DataFrame
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except pyodbc.Error as e:
        st.error(f"Database connection error: {e}")
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
    return None

# Streamlit app
st.title("SQL Server Table Viewer")
st.markdown("This app fetches and displays data from the FileCompare table in the DE_DWHM_DB database.")

# Fetch data
data = fetch_data()

if data is not None:
    if not data.empty:
        st.subheader("Data Preview")
        st.dataframe(data)

        st.subheader("Download Data")
        csv = data.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv, file_name="FileCompare.csv", mime="text/csv")
    else:
        st.warning("The table is empty.")
else:
    st.warning("No data available or an error occurred.")
