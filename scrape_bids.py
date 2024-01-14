# scrape_bids.py
# Get one or more auctions and call getauctions() to scrape the lots for them
import time
import re
import sys
from datetime import *
import sqlite3
from sqlite3 import Error
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options #can remove 
from selenium.webdriver.chrome.service import Service #can remove 
from auction_functions import log_msg, output_program_banner, setup_driver
from scrape_auction_details import *
from scrape_bid_details import *
from db_functions import *


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


driver = setup_driver()

url_count = 0
scrape_start_DateTime = datetime.now()
currentDateTime = None
bids_created = 0
LOT_LIMIT = 100
lot_log_line = "-" * 40


driver.implicitly_wait(2.0)

#Connect to DB to write the new auctions to:
db_conn = sqlite3.connect(DB_PATH)
db_cursor = db_conn.cursor()

# Datetime format in DB lot schema: 2023-10-25T20:26:49.3795010Z
# strftime('%Y-%m-%dT%H:%M:%S', 'now', '+1 hour', 'utc) - gives the upper range limit to get the next hour
db_cursor.execute(f"SELECT * FROM lot WHERE end_datetime > strftime('%Y-%m-%dT%H:%M:%S', 'now', 'utc') AND end_datetime < strftime('%Y-%m-%dT%H:%M:%S', 'now', '+{end_time_window} hour', 'utc') ORDER BY end_datetime LIMIT {LOT_LIMIT}")
rows = db_cursor.fetchall()
log_msg(log_level, 2, __file__, f"Number of lots ending in the next {end_time_window} hour(s) {len(rows)}, capped at {LOT_LIMIT}")


for lot in rows:
    log_msg(log_level, 1, __file__, f"Date-time {lot[16]}: Title {lot[2]}: URL {lot[7]}")
    bid_container = None
    bids = None
    amount = 0

    # Use more robust syntax - like this example:
    # Search = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, '//*[@id="book-search-form"]/div[1]/input[1]'))
    #         )

    driver.get(lot[7])
    log_msg(log_level, 1, __file__, f"Lot page loaded: {driver.title}")

    bids_recorded = get_bids(lot[0], driver, db_cursor, db_conn, log_level)
    log_msg(log_level, 1, __file__, f"Bids recorded on DB: {bids_recorded}")
    log_msg(log_level, 1, __file__, "{lot_log_line}\n\n")

    
#Create scrape record
currentDateTime = datetime.now() # to calc the duration

#Create a scrape record
scrape_duration = currentDateTime - scrape_start_DateTime
seconds = scrape_duration.total_seconds()
    
try:
    db_cursor.execute("INSERT INTO scrape (scrape_entity_type_id, datetime, duration, crawled_url_count) VALUES (?, ?, ?, ?)", (SCRAPE_ENTITY_BID, currentDateTime, seconds, len(rows)))
except Exception as errorMsg:
    log_msg(log_level, 1, __file__, f"Couldn't create scrape record: {errorMsg}")

if db_connected(db_cursor):
    db_cursor.close()
    db_conn.close()

