import sqlite3
import pandas as pd
from db_functions import DB_PATH


def output_lot_bids(conn, lot_UID, UID_type):

    if UID_type == "ID":
        query = f"SELECT * FROM lot LEFT OUTER JOIN bid ON lot.lot_id = bid.lot_id WHERE lot.lot_id = {lot_UID} ORDER BY bid.amount_GBP DESC"
   
    else:
        query = f"SELECT * FROM lot LEFT OUTER JOIN bid ON lot.lot_id = bid.lot_id WHERE lot.lot_ref = '{lot_UID}'"
   
    # Perform a query (replace this with your own query)
    df = pd.read_sql_query(query, conn)

    # Convert DataFrame to HTML table - if HTML wanted
    # html_table = df.to_html(index=False)
    # with open(f'./output/lot_{lot_UID}.html', 'w') as f:
    #     f.write(html_table)

    # Output to CSV
    df.to_csv(f'./output/lot_bids_{lot_UID}.csv', index=False)

    return


if __name__ == "__main__":
    # Connect to the database.
    connection = sqlite3.connect(DB_PATH)

    output_lot_bids(connection, "47911", "ID")

    # Close the database connection
    connection.close()
