#When running from cron, check /var/log/system.log for errors/output


import time
import random
import csv
import re
import json
from datetime import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import element_processing
from auction_functions import *
from db_functions import *


def get_lots(log_level=1, first_lot_url="", auction_rec_ID=0):
    
    output_program_banner(__file__)

    #Connect to DB and setup Chrome driver
    db_conn = sqlite3.connect(DB_PATH)
    db_cursor = db_conn.cursor()

    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument('--blink-settings=imagesEnabled=false') #save badnwidth
    options.add_argument("--incognito")

    # Initialize the WebDriver with the configured options
    path = '/usr/bin/chromedriver'
    service = Service(executable_path=path) 
    driver = webdriver.Chrome(options=options, service=service)
    driver.implicitly_wait(2.0)


    page_count = 0 #one page lists many lots, approx 60
    lots_processed = 0
    lot_records_created = 0
    href_info = "start"
    timestr = time.strftime("%Y%m%d-%H%M%S")
    url_listing_page = first_lot_url #from argument
    MAX_PAGE_COUNT = 240
    catalogue_ref = "cat-ref-unkown"
    JSON_DATA_PATTERN = r'{(.*?)}'
    json_data = None
    lot_data_list = []
    cat_code = None
    cat_ID = 0
    rowid_to_find = None

    db_cursor.execute("SELECT * FROM auction WHERE auction_ID=?", (auction_rec_ID,))
    auction_row = db_cursor.fetchone()
    log_msg(log_level, 3, __file__, f"Selected auction record : {auction_rec_ID} : {auction_row[6]}")
    catalogue_ref = auction_row[6]

    output_file = f'./output/{catalogue_ref}_auction-lots_' + timestr + '.csv'
    log_msg(log_level, 3, __file__, f"Output file : {output_file}")


    with open(output_file, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Lot ID", "URL", "Title", "Description", "Quantity", "Condition", "RRP", "Reserve", "Current bid"])

   
    while page_count < MAX_PAGE_COUNT and href_info != "": 

        href_info = ""
        # lot_number_list = []
        # lot_title_list = []
        next_listing_cta = []
        # current_bid = ""
        # lotnum = ""
        lot_desc = ""
        # matches = []
        extracted_price = 0.0
        reserve_bid = 0.0 # to be added later
        lot_current_bid = 0
        lot_data_list = []

        log_msg(log_level, 2, __file__, f"Getting next lot URL : {url_listing_page}")
        # Generate a random delay & Pause the program for the random delay (anti-blacklisting)
        random_delay = random.uniform(0.05, 0.3)
        time.sleep(random_delay)

        driver.get(url_listing_page)

        lot_title = driver.title
        driver.implicitly_wait(1.2)
      
        try:
            # Lot Number
            #<p class="lot-number">1</p>
            lot_number = driver.find_element(By.CLASS_NAME, value="lot-number").text
            log_msg(log_level, 2, __file__, f"\n\n\nNew page scraped ({page_count}): Lot number: {lot_number} : {lot_title}")
            
            #Description <div class="tinyMCEContent translate">MATE. City Electric Bike 250w Olive Gold With 3 Keys 1 Battery and a Charger (Unboxed &amp; used mileage 5km. Scratched Display ) (RRP £1995)</div>
            #<div class="ui bottom attached active tab segment" data-tab="description" role="tabpanel">
                        #         <div class="tinyMCEContent translate">MATE. City Electric Bike 250w Olive Gold With 3 Keys 1 Battery and a Charger (Unboxed &amp; used mileage 5km. Scratched Display ) (RRP £1995)</div>
                        # </div>
        
            lot_desc_list = driver.find_elements(By.CLASS_NAME, value="tinyMCEContent")
            for element in lot_desc_list:
                if element.text != "" and element.text != None:
                    lot_desc = element.text
                    lot_desc = lot_desc.replace('\n', '|')
        except Exception as errorMsg:
            log_msg(log_level, 3, __file__, f"Error getting lot number or  description (ignore it) {errorMsg}")
            continue

        log_msg(log_level, 3, __file__, f"Lot Description : {lot_desc}")

        # RRP - Find all matches of the price pattern in the description
        extracted_price = element_processing.extract_price(lot_desc)


        #Script list won't exist for closed auctions
        script_list = driver.find_elements(By.TAG_NAME, 'script')
        # log_msg(log_level, 3, __file__, f"Found SCRIPT? : {script_list != None}")

        for s in script_list:
            json_data = None
            lot_data_list = []
            cat_code = None
            cat_ID = 0

            try:
                script_content = s.get_attribute('textContent')
            except Exception as errorMsg:
                log_msg(log_level, 3, __file__, f"Error getting script content (ignore it) {errorMsg}")
                continue
            
            if "categoryCode" in script_content:
                # log_msg(log_level, 3, __file__, f"Processing SCRIPT : {script_content}")

                match_cleaned = ""
                match = re.search(JSON_DATA_PATTERN, script_content, re.DOTALL)

                if match:
                    # log_msg(log_level, 3, __file__, f"Match group(1) :\n >>{match.group(1)}<<\n Ends with comma : {match.group(1).endswith(', ')}")
                    #use STRIP to remove spaces
                    match_cleaned = match.group(1).strip()
                    if match_cleaned.endswith(','):
                        match_cleaned = match_cleaned[:-1] #remove the comma
                    json_data = '{' + match_cleaned + '}'
                    # log_msg(log_level, 3, __file__, f"right script tag? :\n {json_data}\n")
                    script_data = json.loads(json_data)

                    cat_code = script_data.get('categoryCode').strip()

                    try:
                        db_cursor.execute("SELECT * FROM product_category WHERE short_name=?", (cat_code,))
                        row = db_cursor.fetchone()
                        if row:
                            cat_ID = row[0]
                        else:
                            try:
                                rowid_to_find = None
                                db_cursor.execute("INSERT INTO product_category (short_name, name) VALUES (?, ?)", (cat_code, 'unknown')) 
                                rowid_to_find = db_cursor.lastrowid
                                db_cursor.execute("SELECT * FROM product_category WHERE ROWID = ?", (rowid_to_find,))
                                row = db_cursor.fetchone()  
                                cat_ID = row[0]
                            except Exception as errorMsg:
                                log_msg(log_level, 3, __file__, f"Error creating product_category record {errorMsg}")
                    except Exception as errorMsg:
                        log_msg(log_level, 3, __file__, f"Error selecting product_category record {errorMsg}")


                    log_msg(log_level, 3, __file__, f"After selecting/inserting prod_cat :  {cat_code} : {cat_ID}")
                    db_conn.commit()

                    #There's more data in the script tag but this is hwat's useful now
                    lot_data_list.append(auction_rec_ID)
                    lot_data_list.append(lot_title)
                    lot_data_list.append(lot_desc)
                    lot_data_list.append(extracted_price)
                    lot_data_list.append("Condition unknown")
                    lot_data_list.append(script_data.get('openingPrice'))
                    lot_data_list.append(url_listing_page)
                    lot_data_list.append(cat_ID)
                    lot_data_list.append(script_data.get('lotId')) 
                    lot_data_list.append(script_data.get('lotTags'))
                    lot_data_list.append(script_data.get('lotItemType'))
                    lot_data_list.append(script_data.get('minEstimate'))
                    lot_data_list.append(script_data.get('maxEstimate'))
                    lot_data_list.append(script_data.get('lotStartDate'))
                    lot_data_list.append(script_data.get('lotEndDate'))
                    lot_data_list.append(script_data.get('lotEndsFrom'))
                    lot_data_list.append(script_data.get('lotBrand'))
                    lot_data_list.append(script_data.get('lotStatus'))
                    lot_data_list.append(script_data.get('currentWatchers'))
                    lot_data_list.append(script_data.get('currentBids'))
                    lot_data_list.append(script_data.get('deliveryAvailable'))

                    log_msg(log_level, 2, __file__, f"Lot data collected\n : {len(lot_data_list)} : \n{lot_data_list[0]}\n{lot_data_list[1]}")

                    #<span class="amount"><strong>300</strong></span>
                    #*** amend this to look for the list of bids - not just the latets one shown

                    try:
                        lot_current_bid_element = driver.find_element(By.CLASS_NAME, value="amount")
                        if lot_current_bid_element:
                            lot_current_bid = lot_current_bid_element.text
                    except Exception as errorMsg:
                        #Don't output the error msg as it's massive and not useful as we know the cause
                        log_msg(log_level, 3, __file__, f"Error finding current bid (lot probably ended) {url_listing_page}")
                    
                    #Output to file
                    with open(output_file, 'a', encoding='UTF8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([lot_number, url_listing_page, lot_title, lot_desc, "1", "condition unknown", extracted_price, reserve_bid, lot_current_bid])


                    #Create LOT record (if not exists) - don't use list/loop if just one 
                    if lot_data_list:
                        try:
                            db_cursor.execute("SELECT * FROM lot WHERE lot_ref=?", (lot_data_list[8],))
                            row = db_cursor.fetchone()
                            if row:
                                #New code on 5th Oct - needs debugging

                                log_msg(log_level, 3, __file__, f"Found existing lot with lot ref {lot_data_list[8]} : {row}")
                                rowid_to_find = db_cursor.lastrowid
                                log_msg(log_level, 3, __file__, f"Updating watchers from {row[18]} to : {lot_data_list[18]}, bids from {row[19]} to {lot_data_list[19]}")
                               
                                db_cursor.execute("UPDATE lot SET current_watchers = ?, current_bids = ? WHERE ROWID = ?", (lot_data_list[18], lot_data_list[19], rowid_to_find))
                                
                                # cursor.execute("UPDATE your_table SET column1 = ?, column2 = ?, column3 = ? WHERE ROWID = ?",
                                #     (new_value1, new_value2, new_value3, rowid_to_update))


                            else:
                                try:
                                    query = """INSERT INTO lot (auction_id, title, description, RRP_GBP, condition, reserve_bid_price_GBP, URL, product_category_id, lot_ref, tags, item_type, min_estimate, max_estimate, start_date, end_date, end_datetime, brand, status, current_watchers, current_bids, delivery_available) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                                    db_cursor.execute(query, lot_data_list)
                                    db_conn.commit() #Commit each individual lot
                                    lot_records_created += 1
                                except Exception as errorMsg:
                                    log_msg(log_level, 3, __file__, f"Error INSERTing lot {lot_data_list} : {errorMsg}")
                        except Exception as errorMsg:
                            log_msg(log_level, 3, __file__, f"Error SELECTing lot {lot_data_list[8]} : {errorMsg}")

                        db_conn.commit()
                        #Create BID record - always
 
        page_count += 1
        lots_processed += 1

        #Next listing
        # <a id="lot-details-nav-next-lot" href="/en-gb/auction-catalogues/hilco/catalogue-id-hilco-1-10046/lot-621bc639-f4cb-479a-bb10-b03700f9cbce" title="MATE. City Electric Bike 250w Olive Gold">Next lot: 2<i class="icon right chevron"></i></a>
        try:
            #TEMP 5th Oct
            log_msg(log_level, 3, __file__, f"Problem with driver handle? {driver} ")

            next_listing_cta = driver.find_elements(By.ID, value="lot-details-nav-next-lot")
            log_msg(log_level, 2, __file__, f"Next listing (list?): {next_listing_cta} {type(next_listing_cta)}")
            for next_listing in next_listing_cta:
                href_info = next_listing.get_attribute("href")
                url_listing_page = href_info
            # else:
            #     raise ValueError("Driver does not have a ready status, so can't get next page URL : {driver}")
        except Exception as errorMsg:
            log_msg(log_level, 3, __file__, f"Error finding next page element")
            url_listing_page = ""
            href_info = ""


        #if we've already seen this page before ie looped round to the first lot, leave the loop
        pass    
            


    #Close
    driver.quit()
    db_conn.commit()
    db_conn.close()

    # url_listing_page = f"{url_aggregator}{url_auctioneer}/{url_start_page}"

    log_msg(log_level, 2, __file__, f"END of get_lots(), processed : {lots_processed}, created : {lot_records_created}")

     #Just for testing - quit here   
    return lots_processed, lot_records_created

        # sys.exit(0)