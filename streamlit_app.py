import pyodbc
import pandas as pd
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import streamlit as st

# Streamlit app setup
st.title("ODBC Data Fetch and Google Drive Upload")

# Input parameters (from user or fixed configuration)
odbc_name = "Sales"
server_name = "LAPTOP-9MQOKA1D"
db_name = "DE_DWHM_DB"
table_name = "FileCompare"
csv_file_name = f"{table_name}.csv"

def fetch_data():
    """Fetches data from the SQL Server table."""
    try:
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_name};DATABASE={db_name};Trusted_Connection=yes;"
        conn = pyodbc.connect(connection_string)
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        conn.close()
        st.success("Data fetched successfully!")
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def save_csv(df, file_name):
    """Saves DataFrame to a CSV file."""
    try:
        df.to_csv(file_name, index=False)
        st.success(f"CSV file created: {file_name}")
    except Exception as e:
        st.error(f"Error saving CSV: {e}")

def upload_to_google_drive(file_name):
    """Uploads a file to Google Drive."""
    try:
        # Google Drive Authentication
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # Creates local webserver for authentication
        drive = GoogleDrive(gauth)

        # Upload file
        file = drive.CreateFile({"title": os.path.basename(file_name)})
        file.SetContentFile(file_name)
        file.Upload()
        st.success(f"File uploaded to Google Drive: {file['title']}")
    except Exception as e:
        st.error(f"Error uploading file to Google Drive: {e}")

# Main process
if st.button("Fetch and Upload Data"):
    st.info("Fetching data from SQL Server...")
    data = fetch_data()

    if data is not None:
        st.info("Saving data to CSV...")
        save_csv(data, csv_file_name)

        st.info("Uploading CSV to Google Drive...")
        upload_to_google_drive(csv_file_name)

        # Clean up local file
        if os.path.exists(csv_file_name):
            os.remove(csv_file_name)
            st.success("Local CSV file removed after upload.")
