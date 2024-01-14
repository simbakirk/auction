#When running from cron, check /var/log/system.log for errors/output

import sys
import datetime as dt
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
        priority_window = int(arg)

    arg_counter += 1

log_msg(log_level, 3, __file__, f"Priority scrape of lots? : {priority_window!=0} : {priority_window}")

#Just for testing - quit here   
# sys.exit(0)

ONE_DAY_MINS = 1440
SEVEN_DAY_MINS = 10080
priority_window_start = ONE_DAY_MINS
priority_window_end = SEVEN_DAY_MINS

time_delta_start = timedelta(minutes=priority_window_start)
print(time_delta_start)
time_delta_end = timedelta(minutes=priority_window_end)
print(time_delta_end)

current_datetime = datetime.now(timezone(timedelta(hours=1)))
print(current_datetime)
current_datetime = datetime.now()
print(current_datetime)
start__datetime = current_datetime + time_delta_start
print(start__datetime)
end__datetime = current_datetime + time_delta_end
print(end__datetime)


# ending_datetime = datetime.now(timezone(timedelta(hours=1))) + time_delta
# formatted_ending_datetime = ending_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
# current_datetime = datetime.now(timezone(timedelta(hours=1)))
# formatted_current_datetime =current_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")