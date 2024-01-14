# Code to idenitfy lots with low bids vs the RRP

import sqlite3
import datetime as dt
import pandas as pd
from db_functions import DB_PATH
TIMESTAMP_STR = "%Y-%m-%dT%H:%M:%S"
TIMESTAMP_STR_DATE_ONLY = "%Y-%m-%d"


def low_bid_lots(connection):
    """
    idenitfy lots with low bids vs the RRP

    Args:
        connection: A SQLite3 connection object.
    """

    # Get the highest bid for each lot
    # lot.lot_id, lot.title, 
    query = "SELECT lot.lot_id, lot.RRP_GBP, MAX(bid.amount_GBP) AS highest_price FROM lot JOIN bid ON lot.lot_id = bid.lot_id GROUP BY lot.lot_id ORDER BY highest_price DESC"

    # query1 = "SELECT lot.RRP_GBP, MAX(bid.amount_GBP) AS highest_price FROM lot JOIN bid ON lot.lot_id = bid.lot_id ORDER BY highest_price DESC"

    print(f"About to run query\n {query}")
    cursor = connection.execute(query)

    print(f"Cursor:  {cursor}")
    
    
    # Now identify which lots have a realtively big gap between RRP and highest bid
    # Need to identify pallets as they're difficult to know if the RRP is valid
    # Need to identify multiple items in a single lot (pallets being one kind). May need separate process for this


    # Get the results
    results = cursor.fetchall()

    row_count = 0
    for row in results:
        row_count += 1
        print(f"Low bid rows {row_count}: Row: {row}")
        cursor = connection.execute("SELECT * FROM lot WHERE ROWID = ?", (row[0],))
        lot_row = cursor.fetchone()
        if lot_row:
            print(f"Lot details: {lot_row[2]}")



    # Cneommit the changes.
    # conction.commit()

def get_lot_start_end(db_con, lot_id: int):
    """
    Return the auction start/end/duration as datetimes for an individual lot

    Args:
        connection: A SQLite3 connection object.
        Lot_id - the UID of a lot
    """

    start_time = None
    end_time = None
    lot_duration = None

    cursor = db_con.execute("SELECT start_date, end_datetime FROM lot WHERE ROWID = ?", (lot_id, ))
    lot_row = cursor.fetchone()
    if lot_row:
        start_time = dt.datetime.strptime(lot_row[0], TIMESTAMP_STR_DATE_ONLY) 
        if lot_row[1] is not None:
            truncated_timestamp_str = lot_row[1][:19]
            end_time = dt.datetime.fromisoformat(truncated_timestamp_str) 
            lot_duration = end_time - start_time

        return start_time, end_time, lot_duration


def show_lot(db_con, lot_id: int): 
    """
    Dsiplay a lot record

    Args:
        connection: A SQLite3 connection object.
        Lot_id - the UID of a lot
    """

    cursor = db_con.execute("SELECT * FROM lot WHERE ROWID = ?", (lot_id, ))
    lot_row = cursor.fetchone()
    if lot_row:
        col_names = cursor.description

        field_index = 0    
        for field in lot_row:
            print(f"{col_names[field_index][0].rjust(20, ' ')} : {field}")
            field_index += 1

        lot_times = get_lot_start_end(db_con, lot_id)

        print(f"Start time dt : {lot_times[0]}")
        print(f"Auction duration : {lot_times[2]}")
        print(f"End time dt : {lot_times[1]}")

    return


def show_bids_table(db_con, lot_id: int): 
    """
    Display the bids for a lot in  a table, with a relative time offset since the start of the auction

    Args:
        connection: A SQLite3 connection object.
        Lot_id - the UID of a lot
    """

    lot_times = get_lot_start_end(db_con, lot_id)

    cursor = db_con.execute("SELECT * FROM bid WHERE bid.lot_id = ? ORDER BY amount_GBP ASC", (lot_id, ))
    bid_rows = cursor.fetchall()
    if bid_rows:
        col_names = cursor.description

        print(f"Start Time: {lot_times[0]}")
        field_index = 0    
        prev_bid_time = lot_times[0]
        for bid in bid_rows:
            #    print(f"{col_names[field_index][0].rjust(20, ' ')} : {field}")
            print(f"Bid amount : ".rjust(20, ' '), f"{bid[2]}")

            print(f"Bid time : ".rjust(20, ' '), f"{bid[4]}")
            bid_time = dt.datetime.fromisoformat(bid[4]) 
            print(f"Since last : ".rjust(20, ' '), f"{bid_time - prev_bid_time}\n")
            prev_bid_time = bid_time
            field_index += 1

        print(f"End Time : ".rjust(20, ' '), f"{lot_times[2]}")
    return


def show_auction(db_con, auction_UID, UID_type):
    """
    Display the auction details and a count of hte number of lots in the auction

    Args:
        connection: A SQLite3 connection object.
        Auction_uid - the UID of a lot
        UID_type - whether that uid is teh id (int) or the reference (char)
    """


    if UID_type == "ID":
        query = f"SELECT auction.*, COUNT(lot.lot_id) FROM auction LEFT OUTER JOIN lot ON auction.auction_id = lot.auction_id WHERE auction.auction_id = {auction_UID}"
    else:
        query = f"SELECT auction.*, COUNT(lot.lot_id) FROM auction LEFT OUTER JOIN lot ON auction.auction_id = lot.auction_id WHERE auction.auction_catalog_ref = '{auction_UID}'"
    
    print(f"Query : {query}")
    # Perform a query (replace this with your own query)
    df = pd.read_sql_query(query, db_con)

    # Output to CSV
    df.to_csv(f'./output/auc_{auction_UID}.csv', index=False)

    return

if __name__ == "__main__":
    # Connect to the database.


    connection = sqlite3.connect(DB_PATH)

    # show_lot(connection, 20934)

    # get_lot_start_end(connection, 47911)

    # show_bids_table(connection, 20934)

    #   low_bid_lots(connection)


    # show_auction(connection, "964", "ID")
    show_auction(connection, "catalogue-id-ibnew10573", "REF")
    # catalogue-id-ibnew10573 - should give 726 low_bid_lots
    # catalogue-id-univer10008 / 964

    # Close the connection.
    connection.close()

    # Lot 47911 has about 80 bids