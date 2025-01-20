import os
import cx_Oracle
import csv

# Wallet and database connection information
wallet_location = r"C:\Users\Vinitha\Downloads\Wallet_DATAENTREGA 1 (1)"
uid = "WS_2005_SR"
pwd = "Dataentrega@2024"
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="ORCL")  # Replace with your DB details
output_folder = r"C:\Temp\Streamlit-CSV"

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Oracle connection setup
connection = cx_Oracle.connect(user=uid, password=pwd, dsn=dsn,
                                config_dir=wallet_location, wallet_location=wallet_location, 
                                wallet_password=pwd)

try:
    with connection.cursor() as cursor:
        # Query to find tables/views starting with 'V_DE_WHRM_'
        query = """
        SELECT object_name
        FROM all_objects
        WHERE object_type IN ('TABLE', 'VIEW')
          AND object_name LIKE 'V_DE_WHRM_%'
        """
        cursor.execute(query)

        tables_or_views = [row[0] for row in cursor.fetchall()]

        for table_name in tables_or_views:
            # Fetch data from the table/view
            data_query = f"SELECT * FROM {table_name}"
            cursor.execute(data_query)

            # Fetch column names
            columns = [desc[0] for desc in cursor.description]

            # Write data to CSV
            output_file = os.path.join(output_folder, f"{table_name}.csv")
            with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter='~')
                writer.writerow(columns)  # Write headers
                for row in cursor:
                    writer.writerow(row)  # Write data rows

            print(f"Data exported to: {output_file}")

except cx_Oracle.Error as e:
    print(f"Error: {e}")
finally:
    connection.close()
