import os
import streamlit as st
import cx_Oracle
import pandas as pd
import json
import requests
import threading
import time

# Add the 'instantclient' folder to the system PATH
os.environ["PATH"] = os.path.join(os.getcwd(), "instaclient") + ";" + os.environ.get("PATH", "")

print("Updated PATH:", os.environ["PATH"])

# Streamlit app title
st.title("Oracle Data Fetch and Google Drive Upload with Background File Monitoring")

# Access DSN and Database Name via user input
database_name = st.text_input("Database Name", placeholder="Database Name")  # Placeholder for Database Name
dsn = st.text_input("DSN Name", placeholder="DSN Name")  # Placeholder for DSN Name
username = "WS_2005_SR"  # Oracle username
password = "Dataentrega@2024"  # Oracle password

# If database_name is empty, set it to the DSN value
if not database_name:
    database_name = dsn

# Google Drive API access token
headers = {
    "Authorization": "Bearer ya29.a0ARW5m775L4ODw5VW__mmpVW6zm7asuQx618d4HleZoC-Efci7DErj102JxkzKaAxMQaV9nK2B0pdqsrIrCJfdrnPwKUp9CfQut2ZCbH4hDGbtEHmBEycl2XKJKBG2mYB20m-FtIGpW9GyzHpCHiN4_CAnLR46EzQrc8WidGzaCgYKAQASARASFQHGX2MiRFtnC1vW5DhGQn85et5nPw0175"
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

            # Wait for 5 minutes before rechecking
            time.sleep(300)
        except Exception as e:
            st.error(f"Error in monitoring folder: {str(e)}")

# Start the background monitoring thread
monitor_thread = threading.Thread(target=monitor_folder, daemon=True)
monitor_thread.start()

# Button to fetch data from Oracle and upload file to Google Drive
if st.sidebar.button("Fetch Data and Upload to Google Drive"):
    try:
        # Establish cx_Oracle connection to Oracle database
        conn = cx_Oracle.connect("WS_2005_SR", "Dataentrega@2024", "dataentrega_high")

        # Query to get all views starting with "V_DE_WHRM_"
        cursor = conn.cursor()
        cursor.execute("SELECT VIEW_NAME FROM ALL_VIEWS WHERE VIEW_NAME LIKE 'V_DE_WHRM_%'")
        views = [row[0] for row in cursor.fetchall()]

        # Initialize a list to store file names
        csv_files = []

        # Loop through each view and process data
        for view_name in views:
            try:
                # Fetch data for the view
                query = f"SELECT * FROM {view_name}"
                df = pd.read_sql(query, conn)

                # Display data
                st.write(f"Fetched Data from {view_name}:")
                st.dataframe(df)

                # Save data to a CSV file locally
                csv_file = f"{view_name}.csv"
                df.to_csv(csv_file, index=False)
                st.success(f"Data saved to {csv_file}")
                csv_files.append(csv_file)

            except Exception as view_error:
                # Handle errors for individual views
                st.error(f"Failed to fetch data for view {view_name}: {view_error}")

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
