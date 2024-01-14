# Output a count of all tables with the current date - purely for audit purposes
import sqlite3
from db_functions import DB_PATH
import datetime as dt
import csv
from pathlib import Path
from auction_functions import *

#Add code to process the command line args - if this becomes important

def output_row_counts(log_level, conn):
    current_dt = dt.datetime.now()
    table_list = []
    row_count_list = []

    output_file = f'./output/db_row_counts.csv'

    file_exists = Path(output_file).is_file()

    query = """
    SELECT name
    FROM sqlite_master
    WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """
    tables = conn.execute(query).fetchall()

    #iterate thorugh the tables to create the header row
    if not file_exists:
        #make a list of the DB tables
        table_list.append("Date-time")
        for table in tables:
            table_list.append(table[0])
        print(table_list)

        #Create the file and write the header row
        log_msg(log_level, 2, __file__, f"The file '{output_file}' does not exist. Creating...")
        log_msg(log_level, 2, __file__, f"Table list: {table_list}")
        with open(output_file, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(table_list)

    #Now output the row counts to the file
    for table in tables:

        table_name = table[0]
        row_count_query = f"SELECT COUNT(*) FROM {table_name};"
        row_count = conn.execute(row_count_query).fetchone()[0]
        log_msg(log_level, 2, __file__, f"Table: {table_name}, Row Count: {row_count}")
        row_count_list.append(row_count)

    row_count_list.insert(0, current_dt)
    with open(output_file, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row_count_list)

    return


if __name__ == "__main__":
    # Connect to the database.
    connection = sqlite3.connect(DB_PATH)

    output_row_counts(3, connection)

    # Close the database connection
    connection.close()
