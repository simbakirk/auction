#When running from cron, check /var/log/system.log for errors/output

import sys
from datetime import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import element_processing
from auction_functions import *
from db_functions import *
from scrape_lot_details import *


url_aggregator = ""
url_auctioneer = ""
url_start_page = ""
aggregator_name = ""
log_level = 3
auction_ref = ""
priority_window = 0
result = 0, 0
total_lots_processed =0
total_lots_created = 0

output_program_banner(__file__)

#process commend line arguments
arg_counter = 1
priority_window_start = 0
priority_window_end = 0
for arg in sys.argv[1:]:
    log_msg(log_level, 3, __file__, f"Command line arg {arg_counter} : {arg}")
    if arg_counter == 1:
        log_level = arg
    if arg_counter == 2:
        for aggregator in AUCTION_AGGREGATORS:
            if arg == aggregator[0]:
                url_aggregator = aggregator[1]
    if arg_counter == 3:
        # not supported to scrape a single catalog yet
        auction_ref = arg 
    if arg_counter == 4:
        priority_window_start = int(arg)
    if arg_counter == 5:
        priority_window_end = int(arg)

    arg_counter += 1

log_msg(log_level, 3, __file__, f"Priority scrape of lots? : {priority_window!=0} : {priority_window}")

scrape_start_DateTime = datetime.now()

#loop through the auction records - with less than 2 hours before the end - if it's a priority scrape
db_conn = sqlite3.connect(DB_PATH)
db_cursor = db_conn.cursor()

driver = setup_driver()
driver.implicitly_wait(5.0)

time_delta_start = timedelta(minutes=priority_window_start)
time_delta_end = timedelta(minutes=priority_window_end)
start_datetime = datetime.now() + time_delta_start
end_datetime = datetime.now() + time_delta_end
formatted_start_datetime = start_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
formatted_end_datetime = end_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")


query = f"SELECT * FROM auction WHERE end_datetime <= '{formatted_end_datetime}' AND end_datetime >= '{formatted_start_datetime}' AND auction_type_id = 3"


log_msg(log_level, 2, __file__, f"About to run near-to-end auctions query : {query}")

db_cursor.execute(query)

# Fetch all rows or fetch one row at a time in a loop
auction_rec_count = 0
rows = db_cursor.fetchall()
log_msg(log_level, 2, __file__, f"Found {len(rows)} auctions within the time window")

for row in rows:
    auction_rec_count += 1
    auction_rec_ID = row[0]
    log_msg(log_level, 2, __file__, f"Processing auction {auction_rec_count} {row}")

    # Navigate to the page containing the auction lot
    driver.get(row[5])

    # Find the title link element by its CSS selector
    # title_link = driver.find_element_by_css_selector(".lot-header h3 a")
    try:
        title_link = driver.find_element(By.CSS_SELECTOR, ".lot-header h3 a")
        if title_link:
            first_lot_url = title_link.get_attribute('href')
    except Exception as errorMsg:
        log_msg(log_level, 3, __file__, f"Error finding title of current auction, catalogue may not have been loaded yet {url_listing_page}")
    else:
        result = get_lots(log_level, first_lot_url, auction_rec_ID)
        total_lots_processed += result[0]
        total_lots_created += result[1]


driver.quit()

log_msg(log_level, 1, __file__, f"END of scrape_auction_lots\nAuctions processed: {auction_rec_count}\nLots processed: {result[0]}\nLot records created: {result[1]}")

#Create scrape record
currentDateTime = datetime.now() # to calc the duration

#Create a scrape record
scrape_duration = currentDateTime - scrape_start_DateTime
seconds = scrape_duration.total_seconds()
try:
    db_cursor.execute("INSERT INTO scrape (scrape_entity_type_id, datetime, duration, crawled_url_count) VALUES (?, ?, ?, ?)", (SCRAPE_ENTITY_LOT, currentDateTime, seconds, total_lots_created))
except Exception as errorMsg:
    log_msg(log_level, 1, __file__, f"Couldn't create scrape record: {errorMsg}")

# Commit changes and close the connection
db_conn.commit()
db_conn.close()
