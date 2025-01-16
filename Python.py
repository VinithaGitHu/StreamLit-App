import pyodbc
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-9MQOKA1D;"
    "DATABASE=DE_DWHM_DB;"
    "Trusted_Connection=yes;"
)
conn = pyodbc.connect(conn_str)
print("Connection successful!")
