# process_bids.py
# Populate calculated fields on the bid record, post scraping

import sys
from datetime import *
import sqlite3
from sqlite3 import Error
from auction_functions import log_msg, output_program_banner, setup_driver
from db_functions import *
from get_bid_timestamp import *


output_program_banner(__file__)
log_level = 2

#process commend line arguments
arg_counter = 1
end_time_window = 1 #default

for arg in sys.argv[1:]:
    print(f"Argument {arg_counter}: {arg}")
    # 1 - Log level (1-Terse, 2-Normal, 3-Verbose)
    if arg_counter == 1:
        log_level = arg

    if arg_counter == 2:
        end_time_window = arg

    arg_counter += 1

# The bid limit is only to prevent the process running for too long and overalapping with another DB process
BID_LIMIT = 10000

#Connect to DB to read/write bids
db_conn = sqlite3.connect(DB_PATH)
db_cursor = db_conn.cursor()

# Datetime format in DB lot schema: 2023-10-25T20:26:49.3795010Z
# strftime('%Y-%m-%dT%H:%M:%S', 'now', '+1 hour', 'utc) - gives the upper range limit to get the next hour
db_cursor.execute(f"SELECT * FROM bid WHERE bid_datetime IS NULL LIMIT {BID_LIMIT}")
rows = db_cursor.fetchall()
log_msg(log_level, 2, __file__, f"Number of bids with Null bid_datetime: {len(rows)}, capped at {BID_LIMIT}")

bids_updated = 0
for bid in rows:

    # Convert DB STR datetime to python datetime object
    format = "%Y-%m-%dT%H:%M:%S"
    dt = datetime.datetime.strptime(bid[5], format)

    calc_bid_datetime = get_bid_datetime(log_level, dt, bid[3])

    # Execute the UPDATE statement
    rowid = bid[0]
    db_cursor.execute('UPDATE bid SET bid_datetime = ? WHERE rowid = ?', (calc_bid_datetime, rowid,))

    bids_updated += 1
    if bids_updated % 100 == 0:
         db_conn.commit()


if db_connected(db_cursor):
    db_conn.commit()
    db_cursor.close()
    db_conn.close()

log_msg(log_level, 1, __file__, f"Number of bids updated: {bids_updated}")


