# scrape_bid_details.py
# From teh current lot, scrape and record hte bids
import re, time
import sqlite3
from sqlite3 import Error
from selenium import webdriver  
from selenium.webdriver.common.by import By
from auction_functions import log_msg, output_program_banner


# Re-create the function *******
def get_bids(lot_id: int, driver, db_cursor, db_conn, log_level: int) -> int:
    output_program_banner(__file__)

    bids_created = 0
    bids = None


    log_msg(log_level, 1, __file__, f"Looking for bids to scrape for lot ID: {lot_id}, on this page: {driver.title}")
    try:
        bid_container = driver.find_element(By.ID, 'bidHistoryContainer')
        log_msg(log_level, 2, __file__, f"bid container: found")
        if bid_container:
            bids = bid_container.find_elements(By.CLASS_NAME, 'amount')
            who_bids = bid_container.find_elements(By.CLASS_NAME, 'whoBid')
            time_bids = bid_container.find_elements(By.CLASS_NAME, 'time')
    except Exception as errorMsg:
        log_msg(log_level, 3, __file__, f"No bid container found for lot: {lot_id}")
        pass #continue execution


    loop_counter = 0
    if bids:
        for bid in bids[::-1]:
            
            amount = bid.get_attribute('innerText') # text returns blank, only innerText works
            amount = re.sub(r"[^\d]", "", amount)
            # figure out how to get the corresponding who_bid and time_bid from those lists
            who_bid = who_bids[loop_counter].get_attribute('innerText')
            time_bid = time_bids[loop_counter].get_attribute('innerText')

            log_msg(log_level, 3, __file__, f"bid amount: {amount}, Who: {who_bid}, Time: {time_bid}")

            query = f"SELECT amount_gbp FROM bid WHERE lot_id = {lot_id} AND amount_GBP = {amount}"
            log_msg(log_level, 3, __file__, f"Does this bid already exist for this lot? (Next line)...")
            log_msg(log_level, 3, __file__, f"  Query: {query}")

            row = None
            try:
                print(f"about to execute query...")
                db_cursor.execute(query)
                print(f"about to fetchone() query...")
                row = db_cursor.fetchone()
                print(f"After fetchone() query...")
            except Exception as errorMsg:
                log_msg(log_level, 3, __file__, f"Error selecting bid record: {errorMsg}")
            
            log_msg(log_level, 3, __file__, f"bid rec found on DB?:  {amount} : {row}")
            if row is None:
                try:
                    # So that consecutive bids are recorded in the correct sequence, pause 1 sec between adding them
                    time.sleep(1)

                    insert_query = f"INSERT INTO bid (lot_id, amount_GBP, recorded_at, bid_time_label) VALUES ({lot_id}, {amount}, strftime('%Y-%m-%dT%H:%M:%S', 'now', 'utc'), '{time_bid}')"
                    log_msg(log_level, 3, __file__, f"INSERTing bid rec {insert_query}")
                    db_cursor.execute(insert_query)
                    bids_created += 1
                except Exception as errorMsg:
                    log_msg(log_level, 3, __file__, f"Error inserting bid record: {errorMsg}")

            db_conn.commit()
            loop_counter += 1     

    log_msg(log_level, 3, __file__, f"Bids found for lot {lot_id}: {bids_created}")
    return bids_created

