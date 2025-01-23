import streamlit as st
import cx_Oracle
import pandas as pd
import json
import requests
import threading
import time

# Streamlit app title
st.title("Oracle Data Fetch and Google Drive Upload with Background File Monitoring")

# Database connection details
dsn = st.text_input("DSN (Data Source Name)", placeholder="Enter DSN here")
username = st.text_input("Username", placeholder="Enter Oracle username")
password = st.text_input("Password", placeholder="Enter Oracle password", type="password")

# Google Drive API access token
headers = {
    "Authorization": "Bearer ya29.a0ARW5m775L4ODw5VW__mmpVW6zm7asuQx618d4HleZoC-Efci7DErj102JxkzKaAxMQaV9nK2B0pdqsrIrCJfdrnPwKUp9CfQut2ZCbH4hDGbtEHmBEycl2XKJKBG2mYB20m-FtIGpW9GyzHpCHiN4_CAnLR46EzQrc8WidGzaCgYKAQASARASFQHGX2MiRFtnC1vW5DhGQn85et5nPw0175"
}  # Replace with your actual access token.

# Folder IDs for Migration A, B, C
migration_a_folder_id = "1qfgsEKOiJPEN_fJ9OLuyNf2yj1DytheG"
migration_b_folder_id = "1Mbejz1LTosUNY4ke7O8OnZDtXO2mnHPz"
migration_c_folder_id = "1UAsT1L8X4VmUEqhxqV4O8xBYNUyBYAOc"

# Function to fetch files from a Google Drive folder
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
        f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=parents",
        headers=headers,
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

# Background thread to monitor the Migration B folder
def monitor_folder():
    while True:
        try:
            files = list_files_in_folder(migration_b_folder_id)
            trigger_file = next((file for file in files if file["name"] == "Trigger.txt"), None)
            if trigger_file:
                st.info("Found Trigger.txt in Migration B folder. Moving it to Migration C folder...")
                move_file(trigger_file["id"], migration_c_folder_id)
            else:
                st.warning("Trigger.txt not found in Migration B folder. Checking again in 1 minute...")
            time.sleep(300)
        except Exception as e:
            st.error(f"Error in monitoring folder: {str(e)}")

# Start the background monitoring thread
monitor_thread = threading.Thread(target=monitor_folder, daemon=True)
monitor_thread.start()

# Button to fetch data from Oracle and upload it to Google Drive
if st.sidebar.button("Fetch Data and Upload to Google Drive"):
    try:
        # Establish connection using cx_Oracle
        if not dsn or not username or not password:
            st.error("Please provide all database connection details.")
        else:
            conn = cx_Oracle.connect(user=username, password=password, dsn=dsn)
            cursor = conn.cursor()

            # Fetch views
            cursor.execute("SELECT VIEW_NAME FROM ALL_VIEWS WHERE VIEW_NAME LIKE 'V_DE_WHRM_%'")
            views = [row[0] for row in cursor.fetchall()]

            csv_files = []
            for view_name in views:
                try:
                    query = f"SELECT * FROM {view_name}"
                    df = pd.read_sql(query, conn)
                    csv_file = f"{view_name}.csv"
                    df.to_csv(csv_file, index=False)
                    st.success(f"Data from {view_name} saved to {csv_file}")
                    csv_files.append(csv_file)
                except Exception as e:
                    st.error(f"Failed to fetch data from {view_name}: {e}")

            # Close the connection
            conn.close()

            # Upload files to Google Drive
            for csv_file in csv_files:
                with open(csv_file, "rb") as f:
                    metadata = {
                        "name": csv_file,
                        "parents": [migration_a_folder_id]
                    }
                    files = {
                        "data": ("metadata", json.dumps(metadata), "application/json"),
                        "file": f
                    }
                    response = requests.post(
                        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                        headers=headers,
                        files=files
                    )
                    if response.status_code == 200:
                        st.success(f"{csv_file} uploaded successfully.")
                    else:
                        st.error(f"Failed to upload {csv_file}: {response.text}")
    except Exception as e:
        st.error(f"Error occurred: {e}")
