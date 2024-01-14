# scrape_auction_list.py
# Get one or more auctions and call getauctions() to scrape the lots for them
import time
import re
import sys
import datetime
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager 
#from selenium.webdriver.common.by import By
import sqlite3
from sqlite3 import Error
from auction_functions import log_msg, output_program_banner
from scrape_auction_details import *
from db_functions import *


output_program_banner(__file__)
log_level = 2
url_aggregator = ""
aggregator_ref = ""


#process commend line arguments
arg_counter = 1
for arg in sys.argv[1:]:
    print(f"Argument {arg_counter}: {arg}")
    # 1 - Log level (1-Terse, 2-Normal, 3-Verbose)
    if arg_counter == 1:
        log_level = arg
    
    if arg_counter == 2:
        for aggregator in AUCTION_AGGREGATORS:
            if arg == aggregator[0]:
                url_aggregator = aggregator[1]
                aggregator_ref = aggregator[0]
    if arg_counter == 3:
        priority_window == arg

    arg_counter += 1


#Just for testing - quit here   
#sys.exit(0)

driver = setup_driver()

url_count = 0

output_file = f'./output/{aggregator_ref}_auction list_{TIMESTR}.csv'

total_auctions = 0
max_pages = 10 
page_count = 0


scrape_start_DateTime = datetime.datetime.now()
currentDateTime = None
auctions_count = 0
auctions_created = 0

# Construct an XPath expression to find anchor elements to the Next Page
# Define the attribute and its value to search for
#Set this at page 1 of the auction list pages instead?
A_ATTRIBUTE_NAME = "rel"
A_DESIRED_VALUE = "next"  # Replace with the desired attribute value
a_xpath_expression = f'//a[@{A_ATTRIBUTE_NAME}="{A_DESIRED_VALUE}"]'

auction_listing_page = f'{url_aggregator}{AUCTION_URL_PATTERN}/search-filter?auctions=current&AuctionType=Timed'

log_msg(log_level, 1, __file__, f"Starting scrape of {aggregator_ref} auction list\n Auction list page URL {auction_listing_page}\n Output file: {output_file}")

driver.implicitly_wait(2.0)

#Connect to DB to write the new auctions to:
db_conn = sqlite3.connect(DB_PATH)
db_cursor = db_conn.cursor()

#*** Change to build a list of urls & close this driver (window) then call the auction_scrape. Also, change to only used first/last page and fill the rest is an the page is only a URL arg
while page_count <= max_pages and auction_listing_page != None:

    page_count += 1
    result = None
    driver.get(auction_listing_page)
    
    #First page only - Get the total number of auctions which will then be used to control the pagination of the auction list
    if page_count == 1:
        auction_list = driver.find_elements(By.TAG_NAME, "h1")

        log_msg(log_level, 3, __file__, f"Auctions list: {auction_list}")

        for element in auction_list:
            numbers = []
            if element.text.find("We found") > -1:
                numbers = re.findall(NUMBER_FIND_PATTERN, element.text)
                if numbers:
                    total_auctions = numbers[0]
                    log_msg(log_level, 1, __file__, f"Number of auctions listed (count displayed on first page): {total_auctions}")
 
    #Scrape & store the list of auctions from the current page
    result = get_auctions(auction_listing_page, output_file, db_cursor, log_level)
    auctions_count += result[0]
    auctions_created += result[1]
    log_msg(log_level, 2, __file__, f"Page {page_count} processed.\n  Auctions processed: {result[0]}, Auction records created: {result[1]}")

    #Get next page url, find all "next" anchor elements
    matching_elements = driver.find_elements(By.XPATH, a_xpath_expression)

    next_page_url = None
    for a in matching_elements:
        next_page_url = a.get_attribute("href")
        break   #only need first instance of url

    log_msg(log_level, 2, __file__, f"Found next page (url) : {next_page_url}")
    auction_listing_page = next_page_url

#Close the browser driver
driver.quit()

#Update the scrape record 
currentDateTime = datetime.datetime.now() # to calc the duration

#Create a scrape record
scrape_duration = currentDateTime - scrape_start_DateTime
seconds = scrape_duration.total_seconds()
try:
    db_cursor.execute("INSERT INTO scrape (scrape_entity_type_id, datetime, duration, crawled_url_count) VALUES (?, ?, ?, ?)", (SCRAPE_ENTITY_AUCITON, currentDateTime, seconds, auctions_created))
except Exception as errorMsg:
    log_msg(log_level, 1, __file__, f"Couldn't create scrape record: {errorMsg}")

# Commit changes and close the connection
db_conn.commit()
db_conn.close()

log_msg(log_level, 1, __file__, f"Program completed. {auctions_count} auction catalogues processed\n{auctions_created} auction records created")
