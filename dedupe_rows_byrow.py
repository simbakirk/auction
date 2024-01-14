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
    cursor = connection.execute("SELECT * FROM (SELECT lot_id, amount_GBP FROM bid GROUP BY lot_id, amount_GBP)")

    # SELECT COUNT(*)  
    # FROM (
    #   SELECT lot_id, amount_GBP
    #   FROM bid
    #   GROUP BY lot_id, amount_GBP
    # );

    row_count = 0
    for row in cursor:
        row_count += 1
        print(f"Distinct row {row_count}: Lot ID: {row[1]}, amount : {row[2]}, bid ID: {row[0]}")



    # Cneommit the changes.
    # conction.commit()


if __name__ == "__main__":
  # Connect to the database.
  connection = sqlite3.connect(DB_PATH)

  # Deduplicate the rows in the `users` table where the `name` column has the same value.
  deduplicate_rows(connection, "bid", "lot_id, amount_GBP")

  # Close the connection.
  connection.close()