import os
import pyodbc
import pandas as pd
import streamlit as st

# Fetch SQL Server connection details from environment variables
server_name = os.getenv("SQL_SERVER_NAME", "LAPTOP-9MQOKA1D")
database_name = os.getenv("SQL_DATABASE_NAME", "DE_DWHM_DB")
table_name = os.getenv("SQL_TABLE_NAME", "[dbo].[SampleTable]")

# Construct the connection string
connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}}; "
    f"Server=tcp:{server_name},1433; "
    f"DATABASE={database_name}; "
    f"Trusted_Connection=yes; "
    f"TrustServerCertificate=yes;"
)

def fetch_data():
    """Fetch data from the SQL Server table."""
    try:
        # Establish connection
        with pyodbc.connect(connection_string) as conn:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Streamlit application
def main():
    st.title("SQL Server Data Viewer")
    st.write("This app fetches data from a SQL Server table and displays it.")

    # Fetch data from the database
    df = fetch_data()
    if not df.empty:
        st.write("Data from the table:")
        st.dataframe(df)
    else:
        st.warning("No data available or an error occurred.")

if __name__ == "__main__":
    main()
