# Code to de-dupe a table bsed on a specific column
# used to remove duplicate bid rows where teh same lot has more than one bid of the same amunt - due to coding error

import sqlite3
from db_functions import DB_PATH


def deduplicate_rows(connection, table, column_name):
    """
    Deduplicates rows in a database where a column has the same value.

    Args:
        connection: A SQLite3 connection object.
        table: The name of the table to deduplicate.
        column_name: The name of the column to deduplicate.
    """

    # Get the unique values of the column.
    cursor = connection.execute("SELECT COUNT(*) FROM (SELECT lot_id, amount_GBP FROM bid GROUP BY lot_id, amount_GBP)")
    number_of_rows = cursor.fetchone()[0]
    print(f" Row Count : {number_of_rows}")

    cursor = connection.execute("SELECT * FROM (SELECT bid_id, lot_id, amount_GBP FROM bid GROUP BY lot_id, amount_GBP)")

    row_count = 0
    if cursor is not None:
        for row in cursor:
            row_count += 1
            del_row_count = 0
            # print(f"Row: {row}")
            print(f"Distinct row {row_count}: Lot ID: {row[1]}, amount : {row[2]}, bid ID: {row[0]}")

            del_cursor = connection.execute(f"SELECT bid_id, lot_id, amount_GBP FROM bid WHERE lot_id = ? AND amount_GBP = ? AND bid_id <> ?", (row[1], row[2], row[0]))
            if del_cursor is not None:
                
                for del_row in del_cursor:
                    del_row_count += 1
                    print(f"DUPLICATE row {row_count}: Lot ID: {del_row[1]}, amount : {del_row[2]}, bid ID: {del_row[0]}")
                    del2_cursor = del_cursor.execute("DELETE FROM bid WHERE bid_id = ?", (del_row[0],))
                    connection.commit()

            if del_row_count >= 5:
                break

    
    return 


if __name__ == "__main__":
  # Connect to the database.
  connection = sqlite3.connect(DB_PATH)

  # Deduplicate the rows in the `users` table where the `name` column has the same value.
  deduplicate_rows(connection, "bid", "lot_id, amount_GBP")

  # Close the connection.
  connection.close()