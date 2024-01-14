import sqlite3
import pandas as pd
from db_functions import DB_PATH


def output_auction_lots(conn, auction_UID, UID_type):


    # SELECT a.auction_id, a.auction_title, l.lot_id, l.lot_description, b.bid_amount
    # FROM auction AS a
    # INNER JOIN lot AS l ON a.auction_id = l.auction_id
    # LEFT JOIN bid AS b ON l.lot_id = b.lot_id;


    if UID_type == "ID":
        query = f"SELECT * FROM auction JOIN lot ON auction.auction_id = lot.auction_id LEFT OUTER JOIN bid ON lot.lot_id = bid.lot_id LEFT OUTER JOIN product_category ON lot.product_category_id = product_category.product_category_id WHERE auction.auction_id = {auction_UID} ORDER BY bid.lot_ID ASC, bid.amount_GBP DESC "
    else:
        query = f"SELECT * FROM auction JOIN lot ON auction.auction_id = lot.auction_id LEFT OUTER JOIN bid ON lot.lot_id = bid.lot_id LEFT OUTER JOIN product_category ON lot.product_category_id = product_category.product_category_id WHERE auction.auction_catalog_ref = '{auction_UID}' ORDER BY bid.lot_ID ASC, bid.amount_GBP DESC "
   
   
    # Perform a query (replace this with your own query)
    df = pd.read_sql_query(query, conn)

    # Convert DataFrame to HTML table - if HTML wanted
    # html_table = df.to_html(index=False)
    # with open(f'./output/lot_{lot_UID}.html', 'w') as f:
    #     f.write(html_table)

    # Output to CSV
    df.to_csv(f'./output/auc_lots_{auction_UID}.csv', index=False)

    return


if __name__ == "__main__":
    # Connect to the database.
    connection = sqlite3.connect(DB_PATH)

    # output_auction_lots(connection, "964", "ID")
    output_auction_lots(connection, "catalogue-id-intern1-10717", "REF")
    # catalogue-id-intern1-10717
    # catalogue-id-ibnew10573

    # Close the database connection
    connection.close()
