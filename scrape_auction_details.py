#scrape_auction_details.py
#When running from cron, check /var/log/system.log for errors/output
# if the Chromedriver gets out of date then run: sudo python -m pip install --upgrade pip
import csv
import json
import sys
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pathlib import Path
from sqlite3 import Error
from auction_functions import *
from db_functions import *


def get_auctions(auction_listing_page, output_file, db_cursor, log_level=1): 
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument('--blink-settings=imagesEnabled=false') #save badnwidth
    options.add_argument("--incognito")

    # Initialize the WebDriver with the configured options
    path = '/usr/bin/chromedriver'
    service = Service(executable_path=path) 
    driver = webdriver.Chrome(options=options, service=service)

    output_program_banner(__file__)
    log_msg(log_level, 3, __file__, f"Starting scrape of auction list\n Auction list page URL {auction_listing_page}\n Output file: {output_file}")

    #get page
    driver.implicitly_wait(2.0)
    driver.get(auction_listing_page)

    #Connect to DB to write the new auctions to:
    db_conn = sqlite3.connect(DB_PATH)
    db_cursor = db_conn.cursor()

    #iterate through the auction container elements
    auctions_count = 0
    auctions_created = 0

    auction_container = driver.find_elements(By.CLASS_NAME, 'auction-container')
    for element in auction_container:
        auctions_count += 1
        auctioneer_id = 0
        auctioneer_rec = []
        auctioneer_ref = ""
        organizer_object = None
        auctioneer_fullname = ""

        log_msg(log_level, 3, __file__, f"Processing auction container : {auctions_count} : {element}")

        #Get auctioneer
        auction_title_list = element.find_elements(By.CLASS_NAME, 'auction-auctioneer')
        for sub_element in auction_title_list:
            auctioneer_url = sub_element.get_attribute("href")
            auctioneer_url_bits = auctioneer_url.split('/')
            auctioneer_ref = auctioneer_url_bits[5] #Replace magic number
            
            log_msg(log_level, 3, __file__, f"Auctioneer ref : {auctioneer_ref} : from {auctioneer_url}\n")

        #Get auction category list
        auction_cat_list = element.find_elements(By.CLASS_NAME, 'auction-category-list')
        log_msg(log_level, 3, __file__, f"Auction category list : {auction_cat_list}")

        cat_ref_list = []
        for cat in auction_cat_list:
            # Find all the a elements within the div
            a_elements = cat.find_elements(By.TAG_NAME, 'a')

            for sub_element in a_elements:
                auction_cat_url = sub_element.get_attribute("href")
                auction_cat_url_bits = auction_cat_url.split("/")
                cat_ref_bits = auction_cat_url_bits[len(auction_cat_url_bits)-1].split("=")
                cat_ref = cat_ref_bits[1]
                cat_ref_list.append(cat_ref)

            # Convert the list to a pipe-separated string
            pipe_separated_cats = '|'.join(cat_ref_list)
            log_msg(log_level, 3, __file__, f"List of categories for this auction : {cat_ref_list} : {pipe_separated_cats}")

            #To-do - extarct number of lots in each category? TBC

        #Get the auction URL & (in future) other data from the script/Schema.org JSON
        #Note - json gets are case sensitive
        #Script list won't exist for closed auctions
        script_list = element.find_elements(By.TAG_NAME, 'script')

        for s in script_list:

            script_content = s.get_attribute('textContent')
            log_msg(log_level, 3, __file__, f"Processing SCRIPT : {script_content}")
            
            script_data = json.loads(script_content)
            auction_url = script_data.get('url')
            log_msg(log_level, 3, __file__, f"Auction URL (from script content) : {auction_url}")

            auction_ref_bits = auction_url.split("/")
            auction_ref = auction_ref_bits[6]
            log_msg(log_level, 3, __file__, f"Auction REF (from script content) : {auction_ref}")

            auction_start_datetime = script_data.get('startDate')
            auction_end_datetime = script_data.get('endDate')
            auction_title = script_data.get('name')
            auction_desc = script_data.get('description')
            organizer_object = script_data.get('organizer')
            auctioneer_fullname = organizer_object.get('name')

            #Get auction type - timed vs webcast - not in schema (?) but visible on page

        #CSV output is primarily for debug and can be turned off when SQL is in place
        #If first catalogue then write the CSV header
        if Path(output_file).is_file():
            print(f"The file '{output_file}' exists.")
        else:
            print(f"The file '{output_file}' does not exist.")
            with open(output_file, 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Row count", "Auctioneer Ref", "Auctioneer name", "Auctioneer URL", "Catalogue Ref", "Catalogue URL", "Categories list (PSV)", "Catalogue title", "Catalogue Description", "Number of lots", "Start Datetime", "End Datetime"])

        with open(output_file, 'a', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([auctions_count, auctioneer_ref, auctioneer_url, auction_ref, auctioneer_fullname, auction_url, pipe_separated_cats, auction_title, auction_desc, "Number of lots", auction_start_datetime, auction_end_datetime])

        #find the auctioneer by ref - if not exists then create it
        log_msg(log_level, 1, __file__, f"select auctioneer {auctioneer_ref} : {auctioneer_fullname}...")
        try:
            query_string = f"SELECT * FROM auctioneer WHERE short_name='{auctioneer_ref}'"
            auctioneer_rec = db_cursor.execute(query_string).fetchone()
            if auctioneer_rec:
                log_msg(log_level, 2, __file__, f"Auctioneer {auctioneer_ref} already exists : {auctioneer_rec}")
            else:
                log_msg(log_level, 2, __file__, f"Auctioneer {auctioneer_ref} does not already exist? Let's create it...")

                try:
                    db_cursor.execute("INSERT INTO auctioneer (short_name, name, country_id) VALUES (?, ?, ?)", (auctioneer_ref, auctioneer_fullname, get_country_id(log_level, 'UK')))

                    # This is necessary because execute doesn't return a record, so we have to re-find it
                    rowid_to_find = db_cursor.lastrowid
                    db_cursor.execute("SELECT * FROM auctioneer WHERE ROWID = ?", (rowid_to_find,))
                    auctioneer_rec = db_cursor.fetchone()

                    if auctioneer_rec:
                        log_msg(log_level, 2, __file__, f"Auctioneer {auctioneer_ref} successfully inserted : {auctioneer_rec}")
                    else:
                        log_msg(log_level, 2, __file__, f"Auctioneer {auctioneer_ref} unsuccessfully inserted : {auctioneer_rec}")
                        auctioneer_rec = None

                except Error as errorMsg:
                    log_msg(log_level, 3, __file__, f"Error inserting aucitoneer record {auctioneer_ref}: {errorMsg}")
                    auctioneer_rec = None
        except Error as errorMsg:
            log_msg(log_level, 3, __file__, f"Error selecting auctioneer record {auctioneer_ref}: {errorMsg}")
            auctioneer_rec = None
  
        db_conn.commit()

        # Create the auction record
        log_msg(log_level, 1, __file__, f"Do we have a valid auctioneer record? : auctioneer_rec {auctioneer_rec}")
        
        if auctioneer_rec:
            try:
                log_msg(log_level, 1, __file__, f"Does auction {auction_ref} already exist? ...")
                query_string = f"SELECT * FROM auction WHERE auction_catalog_ref='{auction_ref}'"
                auction_rec = db_cursor.execute(query_string).fetchone()

                if auction_rec:
                    log_msg(log_level, 2, __file__, f"Auction  {auction_ref} rec found : {auction_rec}")
                else:
                    log_msg(log_level, 2, __file__, f"Auction {auction_ref} not found, let's create it")
                    db_cursor.execute("INSERT INTO auction (auctioneer_id, country_id, end_datetime, url, auction_catalog_ref, auction_type_id) VALUES (?, ?, ?, ?, ?, ?)", (auctioneer_rec[0], get_country_id(log_level, 'UK'), auction_end_datetime, auction_url, auction_ref, 3))

                    log_msg(log_level, 2, __file__, f"Row count after auction INSERT {db_cursor.rowcount}")
                    auctions_created += 1

            except Error as errorMsg:
                log_msg(log_level, 3, __file__, f"Msg after finding auction, ERROR {auction_ref}: {errorMsg}")
       
        db_conn.commit()
        # Store auction_product_categories
        # CREATE auction_product_category in schema first!!!!!!


        # if auctions_count >= 10:
        #     #*** TEMP ***
        #     driver.quit()
        #     sys.exit()

    log_msg(log_level, 2, __file__, f"Found {auctions_count} auction catalogues on this page")

    #Close
    driver.quit()

    return auctions_count, auctions_created

