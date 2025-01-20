import cx_Oracle
import os
import csv

def fetch_tables_and_write_csv(dsn, user, password, output_path):
    # Establish a connection to the Oracle database
    try:
        connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
        cursor = connection.cursor()

        # Query to fetch tables or views starting with 'V_DE_WHRM_'
        query = """
        SELECT table_name
        FROM all_tables
        WHERE table_name LIKE 'V_DE_WHRM_%'
        UNION ALL
        SELECT view_name
        FROM all_views
        WHERE view_name LIKE 'V_DE_WHRM_%'
        """

        cursor.execute(query)
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("No tables or views found matching the criteria.")
            return

        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)

        # Process each table or view
        for table in tables:
            print(f"Processing table/view: {table}")

            # Query to select all data from the table/view
            data_query = f"SELECT * FROM {table}"
            cursor.execute(data_query)

            # Fetch column names
            column_names = [col[0] for col in cursor.description]

            # Define the output CSV file path
            csv_file_path = os.path.join(output_path, f"{table}.csv")

            # Write data to the CSV file
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter='~')

                # Write the header row
                writer.writerow(column_names)

                # Write the data rows
                for row in cursor:
                    writer.writerow(row)

            print(f"Data written to: {csv_file_path}")

    except cx_Oracle.DatabaseError as e:
        print(f"Database error: {e}")

    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    # Database connection details
    DSN = "WS_2005_SR"
    USER_ID = "WS_2005_SR"
    PWD = "Dataentrega@2024"

    # Output path for CSV files
    LOCAL_PATH = r"C:\\Temp\\Streamlit-CSV"

    # Fetch tables and write data to CSV
    fetch_tables_and_write_csv(DSN, USER_ID, PWD, LOCAL_PATH)