import streamlit as st
import oracledb
import pandas as pd
import json
import requests
import threading
import time

# Streamlit app title
st.title("Oracle Data Fetch and Google Drive Upload with Background File Monitoring")

# Access Oracle credentials via user input (no secrets.toml)
dsn = st.text_input("Enter Oracle DSN", value="WS_2005_SR")  # Example: "localhost:1521/ORCL"
username = st.text_input("Enter Oracle Username", value="WS_2005_SR")  # Replace with your default username
password = st.text_input("Enter Oracle Password", value="Dataentrega@2024", type="password")  # Password input is masked

st.sidebar.header("Table Selection")
table_names = st.sidebar.text_input("Enter Table Names (comma-separated)", value="V_DE_WHRM_1001")

# Google Drive API access token
headers = {
    "Authorization": "Bearer ya29.a0ARW5m77gktvnXLvvKC5cwwjnTBHz1PISQJT2jsTqGaRuxiOoTP_-fK2UxGkI4eKH3i6U7oeUIl2Ed1KsmL1uU6_Xs5cW1JlMHM38PWNAalhyuOG9OdwI1IRt0yCnRruNnAxnvApwEmjGkUa1e0-XE_hqFJOfPNfaSthlmCuhaCgYKAXUSARASFQHGX2MiRfDR5qewkdD50KgLoaECYA0175"
}  # Replace with your access token.

# Folder IDs for Migration A, B, C
migration_a_folder_id = "1qfgsEKOiJPEN_fJ9OLuyNf2yj1DytheG"  # Replace with Migration A folder ID
migration_b_folder_id = "1Mbejz1LTosUNY4ke7O8OnZDtXO2mnHPz"  # Replace with Migration B folder ID
migration_c_folder_id = "1UAsT1L8X4VmUEqhxqV4O8xBYNUyBYAOc"  # Replace with Migration C folder ID

# Function to list files in a folder
def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    response = requests.get(
        f"https://www.googleapis.com/drive/v3/files?q={query}&fields=files(id,name)",
        headers=headers,
    )
    if response.status_code == 200:
        return response.json().get("files", [])
    else:
        st.error(f"Failed to list files: {response.status_code}, {response.text}")
        return []

# Function to move a file to another folder
def move_file(file_id, target_folder_id):
    get_response = requests.get(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=parents", headers=headers
    )
    if get_response.status_code == 200:
        current_parents = ",".join(get_response.json().get("parents", []))
        update_response = requests.patch(
            f"https://www.googleapis.com/drive/v3/files/{file_id}",
            headers=headers,
            params={"addParents": target_folder_id, "removeParents": current_parents},
        )
        if update_response.status_code == 200:
            st.success("Trigger.txt moved successfully to Migration C folder.")
        else:
            st.error(f"Failed to move file: {update_response.status_code}, {update_response.text}")
    else:
        st.error(f"Failed to get file details: {get_response.status_code}, {get_response.text}")

# Background task to monitor Migration B folder
def monitor_folder():
    while True:
        try:
            # List files in Migration B folder
            files = list_files_in_folder(migration_b_folder_id)

            # Check if Trigger.txt exists
            trigger_file = next((file for file in files if file["name"] == "Trigger.txt"), None)
            if trigger_file:
                st.info("Found Trigger.txt in Migration B folder. Moving it to Migration C folder...")
                move_file(trigger_file["id"], migration_c_folder_id)
            else:
                st.warning("Trigger.txt not found in Migration B folder. Checking again in 1 minute...")

            # Wait for 5 minute before rechecking
            time.sleep(300)
        except Exception as e:
            st.error(f"Error in monitoring folder: {str(e)}")

# Start the background monitoring thread
monitor_thread = threading.Thread(target=monitor_folder, daemon=True)
monitor_thread.start()

# Button to fetch data from Oracle and upload file to Google Drive
if st.sidebar.button("Fetch Data and Upload to Google Drive"):
    try:
        # Establish oracledb connection to Oracle database
        conn = oracledb.connect(user=username, password=password, dsn=dsn)

        # Split table names by comma
        table_names_list = [table.strip() for table in table_names.split(",")]

        # Initialize a list to store file names
        csv_files = []

        # Loop through each table and process data
        for table_name in table_names_list:
            try:
                # Fetch data for the table
                query = f"SELECT * FROM {table_name}"
                df = pd.read_sql(query, conn)

                # Display data
                st.write(f"Fetched Data from {table_name}:")
                st.dataframe(df)

                # Save data to a CSV file locally
                csv_file = f"{table_name}.csv"
                df.to_csv(csv_file, index=False)
                st.success(f"Data saved to {csv_file}")
                csv_files.append(csv_file)

            except Exception as table_error:
                # Handle errors for individual tables
                st.error(f"Failed to fetch data for table {table_name}: {table_error}")

        # Close the connection
        conn.close()

        # Loop through and upload each CSV file
        for csv_file in csv_files:
            try:
                # Metadata for Google Drive upload
                para = {
                    "name": csv_file,
                    "parents": [migration_a_folder_id]  # Ensure it uploads to Migration A folder
                }

                files = {
                    'data': ('metadata', json.dumps(para), 'application/json'),
                    'file': open(csv_file, "rb")
                }

                response = requests.post(
                    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                    headers=headers,
                    files=files
                )

                # Handling the response
                if response.status_code == 200:
                    st.success(f"{csv_file} uploaded successfully to Migration A folder in Google Drive.")
                    st.json(response.json())
                else:
                    st.error(f"Failed to upload {csv_file}: {response.status_code}, {response.text}")
            except Exception as upload_error:
                st.error(f"Error uploading {csv_file}: {upload_error}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
