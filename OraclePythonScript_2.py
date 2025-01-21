import streamlit as st
import oracledb
import pandas as pd
import json
import requests
import threading
import time

# Streamlit app title
st.title("Oracle Data Fetch and Google Drive Upload with Background File Monitoring")

# Oracle connection details
dsn_template = """
(description=
    (retry_count=20)(retry_delay=3)
    (address=(protocol=tcps)(host=adb.ap-mumbai-1.oraclecloud.com)(port=1522))
    (connect_data=(service_name=g10916f2e32ac91_dataentrega_high.adb.oraclecloud.com))
    (security=(ssl_server_dn_match=yes))
)
"""
dsn = st.text_area("Oracle DSN", value=dsn_template.strip())
username = st.text_input("Oracle Username", value="WS_2005_SR")
password = st.text_input("Oracle Password", value="Dataentrega@2024", type="password")

# Table selection
st.sidebar.header("Table Selection")
table_names = st.sidebar.text_input("Enter Table Names (comma-separated)", value="V_DE_WHRM_1001")

# Google Drive API Access Token
headers = {
    "Authorization": "Bearer ya29.a0ARW5m77gktvnXLvvKC5cwwjnTBHz1PISQJT2jsTqGaRuxiOoTP_-fK2UxGkI4eKH3i6U7oeUIl2Ed1KsmL1uU6_Xs5cW1JlMHM38PWNAalhyuOG9OdwI1IRt0yCnRruNnAxnvApwEmjGkUa1e0-XE_hqFJOfPNfaSthlmCuhaCgYKAXUSARASFQHGX2MiRfDR5qewkdD50KgLoaECYA0175"
}  # Replace with your access token.

# Google Drive folder IDs
migration_a_folder_id = "1qfgsEKOiJPEN_fJ9OLuyNf2yj1DytheG"
migration_b_folder_id = "1Mbejz1LTosUNY4ke7O8OnZDtXO2mnHPz"
migration_c_folder_id = "1UAsT1L8X4VmUEqhxqV4O8xBYNUyBYAOc"

# Function to list files in a Google Drive folder
def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    response = requests.get(
        f"https://www.googleapis.com/drive/v3/files?q={query}&fields=files(id,name)", headers=headers
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
            files = list_files_in_folder(migration_b_folder_id)
            trigger_file = next((file for file in files if file["name"] == "Trigger.txt"), None)
            if trigger_file:
                st.info("Found Trigger.txt in Migration B folder. Moving it to Migration C folder...")
                move_file(trigger_file["id"], migration_c_folder_id)
            time.sleep(300)  # Check every 5 minutes
        except Exception as e:
            st.error(f"Error in monitoring folder: {str(e)}")

# Start monitoring thread
monitor_thread = threading.Thread(target=monitor_folder, daemon=True)
monitor_thread.start()

# Button to fetch data from Oracle and upload to Google Drive
if st.sidebar.button("Fetch Data and Upload to Google Drive"):
    try:
        # Establish connection to Oracle database
        conn = oracledb.connect(user=username, password=password, dsn=dsn, config=oracledb.ConnectParams())

        table_names_list = [table.strip() for table in table_names.split(",")]
        csv_files = []

        for table_name in table_names_list:
            try:
                query = f"SELECT * FROM {table_name}"
                df = pd.read_sql(query, conn)
                st.write(f"Fetched Data from {table_name}:")
                st.dataframe(df)

                csv_file = f"{table_name}.csv"
                df.to_csv(csv_file, index=False)
                st.success(f"Data saved to {csv_file}")
                csv_files.append(csv_file)

            except Exception as table_error:
                st.error(f"Failed to fetch data for table {table_name}: {table_error}")

        conn.close()

        for csv_file in csv_files:
            try:
                para = {"name": csv_file, "parents": [migration_a_folder_id]}
                files = {
                    'data': ('metadata', json.dumps(para), 'application/json'),
                    'file': open(csv_file, "rb")
                }
                response = requests.post(
                    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                    headers=headers,
                    files=files
                )
                if response.status_code == 200:
                    st.success(f"{csv_file} uploaded successfully to Migration A folder in Google Drive.")
                else:
                    st.error(f"Failed to upload {csv_file}: {response.status_code}, {response.text}")
            except Exception as upload_error:
                st.error(f"Error uploading {csv_file}: {upload_error}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
