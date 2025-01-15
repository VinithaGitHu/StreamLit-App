import streamlit as st
import pyodbc
import pandas as pd
import json
import requests

# Streamlit app title
st.title("SQL Server Data Fetch and Google Drive Upload")

# Sidebar for input fields
st.sidebar.header("SQL Server Connection Details")
server = st.sidebar.text_input("Server Address", value="DESKTOP-RCE6E1O")
database = st.sidebar.text_input("Database Name", value="DE_MIGR_DB")
username = st.sidebar.text_input("Username", value="test1")
password = st.sidebar.text_input("Password", value="cls", type="password")

st.sidebar.header("Table Selection")
table_name = st.sidebar.text_input("Table Name", value="DemoTable")

# Button to fetch data
if st.sidebar.button("Fetch Data and Upload to Google Drive"):
    try:
        # Establish pyodbc connection
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        conn = pyodbc.connect(connection_string)

        # Fetch data
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)

        # Close the connection
        conn.close()

        # Display data
        st.write("Fetched Data:")
        st.dataframe(df)

        # Save data to a CSV file locally
        csv_file = f"{table_name}.csv"
        df.to_csv(csv_file, index=False)
        st.success(f"Data saved to {csv_file}")

        # Google Drive Upload - Replace with your access token
        headers = {"Authorization": "Bearer ya29.a0ARW5m75wvEaloWYXYYGsRbjMwFt4IgspbX6osR4CBXh8A0J1BZRnAHHl5a4vcqfoVBon-lbh35z_xFISstdSgxJEmeXIns0j63NuDNZp1yhMD_dikIb4TI9o3Yg0AHK2voi8kGBDhs3usN-CmJbUZg6799WEsyNkunk0WIIOaCgYKAZ4SARISFQHGX2MiMx1INhPtYZQ6uufeZBGgnA0175"}  # Make sure to replace 'YOUR_ACCESS_TOKEN' with the actual access token

        # Metadata
        para = {
            "name": csv_file,
        }

        # Open the CSV file to upload
        files = {
            'data': ('metadata', json.dumps(para), 'application/json'),
            'file': open(csv_file, "rb")
        }

        # Upload file to Google Drive
        response = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
            headers=headers,
            files=files
        )

        # Handling the response
        if response.status_code == 200:
            st.success("File uploaded successfully to Google Drive.")
            st.json(response.json())
        else:
            st.error(f"Failed to upload file: {response.status_code}, {response.text}")

    except Exception as e:
        st.error(f"An error occurred: {e}")