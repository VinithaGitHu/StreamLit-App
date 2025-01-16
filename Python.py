import pyodbc

import streamlit as st

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-9MQOKA1D;"  # Change this to your actual server
    "DATABASE=DE_DWHM_DB;"
    "Trusted_Connection=yes;"  # Or use UID and PWD if using SQL Auth
)

try:
    conn = pyodbc.connect(conn_str)
    print("Connection successful!")
    conn.close()
except pyodbc.Error as e:
    st.write("Hello, World!")
