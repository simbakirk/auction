# Code to de-dupe a table bsed on a specific column
# used to remove duplicate bid rows where teh same lot has more than one bid of the same amunt - due to coding error

# *** DON'T USE - DROPPED TABLE BUT DIDNT' RECREATE IT ***

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
  unique_values = set()
  cursor = connection.execute("SELECT DISTINCT {} FROM {}".format(column_name, table))
  for row in cursor:
    unique_values.add(row[0])

  # Create a temporary table to store the deduplicated rows.
  connection.execute("CREATE TEMPORARY TABLE deduplicated_rows AS SELECT * FROM {} WHERE {} IN ({})".format(table, column_name, ','.join(str(v) for v in unique_values)))

  # Drop the original table.
  connection.execute("DROP TABLE {}".format(table))

  # Rename the temporary table to the original table.
  connection.execute("ALTER TABLE deduplicated_rows RENAME TO {}".format(table))

  # Commit the changes.
  connection.commit()


if __name__ == "__main__":
  # Connect to the database.
  connection = sqlite3.connect(DB_PATH)

  # Deduplicate the rows in the `users` table where the `name` column has the same value.
  deduplicate_rows(connection, "bid", "amount_GBP")

  # Close the connection.
  connection.close()