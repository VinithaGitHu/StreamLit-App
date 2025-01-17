import streamlit as st
import cx_Oracle
import mysql.connector
import time
import os
from datetime import datetime

def connect_to_oracle(dsn, user, password):
    try:
        connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
        st.success("Connected to Oracle Database successfully.")
        return connection
    except Exception as e:
        st.error(f"Failed to connect to Oracle Database: {str(e)}")
        return None

def execute_oracle_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error executing query on Oracle: {str(e)}")
        return None

def connect_to_mysql(host, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        st.success("Connected to MySQL Database successfully.")
        return connection
    except Exception as e:
        st.error(f"Failed to connect to MySQL Database: {str(e)}")
        return None

def check_mysql_trigger(connection, table_name, column_name, check_value):
    try:
        cursor = connection.cursor()
        while True:
            query = f"SELECT {column_name} FROM {table_name} WHERE {column_name} = '{check_value}'"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                return True
            time.sleep(60)
    except Exception as e:
        st.error(f"Error checking MySQL trigger: {str(e)}")
        return False

st.title("Data Export and Monitoring App")

gdrive_path = st.text_input("Enter the Google Drive path (e.g., G:\\):")

if gdrive_path:
    st.success(f"Google Drive path set to: {gdrive_path}")

oracle_dsn = "WS_2005_SR"
oracle_user = "WS_2005_SR"
oracle_password = "Dataentrega@2024"

if st.button("Connect to Oracle and Export Files"):
    oracle_connection = connect_to_oracle(oracle_dsn, oracle_user, oracle_password)
    if oracle_connection:
        query = "SELECT * FROM V_DE_WHRM_*"  # Replace with the actual query
        data = execute_oracle_query(oracle_connection, query)

        if data:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            export_file = os.path.join(gdrive_path, f"export_{timestamp}.csv")

            try:
                with open(export_file, "w") as file:
                    for row in data:
                        file.write(",".join(map(str, row)) + "\n")
                st.success(f"Exported data to {export_file}")

                empty_file_path = os.path.join(gdrive_path, "success_flag.txt")
                with open(empty_file_path, "w") as file:
                    file.write("")
                st.success(f"Created success flag file: {empty_file_path}")

            except Exception as e:
                st.error(f"Failed to export data or create file: {str(e)}")

mysql_host = "web_hosting_server"
mysql_user = "your_mysql_user"
mysql_password = "your_mysql_password"
mysql_database = "your_mysql_database"
mysql_table = "your_trigger_table"
mysql_column = "trigger_column"
trigger_value = "expected_value"

if st.button("Monitor MySQL Trigger"):
    mysql_connection = connect_to_mysql(mysql_host, mysql_user, mysql_password, mysql_database)
    if mysql_connection:
        st.info("Monitoring MySQL for trigger value...")
        if check_mysql_trigger(mysql_connection, mysql_table, mysql_column, trigger_value):
            st.success("Trigger detected! Process completed.")
