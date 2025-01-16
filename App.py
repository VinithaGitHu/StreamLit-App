import pyodbc
import pandas as pd
import streamlit as st

# SQL Server connection details
server_name = "LAPTOP-9MQOKA1D"
database_name = "DE_DWHM_DB"
table_name = "[dbo].[SampleTable]"

# Connection string
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}}; Server=tcp:{server_name},1433;DATABASE={database_name};Trusted_Connection=yes;TrustServerCertificate=yes;"

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
