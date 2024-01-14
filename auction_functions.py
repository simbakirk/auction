'''Standard functions used in the Auction processing code'''
import time
import sqlite3
from sqlite3 import Error
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


#Global contants
I_BIDDER_SHORT_CODE = "i_bidder" 
BIDSPOTTER_SHORT_CODE = "bidspotter" 
AUCTION_AGGREGATORS = [['bidspotter',"http://https://www.bidspotter.co.uk/en-gb/auction-catalogues/"],['i-bidder','https://www.i-bidder.com/en-gb/auction-catalogues/']]
NUMBER_FIND_PATTERN = r'\d+' # This pattern matches one or more digits
AUCTION_URL_PATTERN = r'auction-catalogues'
TIMESTR = time.strftime("%Y%m%d-%H%M%S")
DEFAULT_URL_COUNTRY_LANG = "en-gb"
# Define the regular expression pattern to match prices
PRICE_PATTERN = r"\£(\d+(?:\.\d{2})?)"

def output_program_banner(program_name):
    print("\n\n+", "-" * 38, "+")
    # print("-" * 38)
    # print("+")
    print(f"Program name : {program_name}")
    return

def log_msg(log_level_arg : int, log_level : int, program_name, msg_text):
    msg_text = msg_text.encode('utf-8')
    '''Output log messages in a standard format and to the level specificed in the cmd line arg'''
    # Would be better handled as an object with a log_msg method
    #keep here for now to improve later
    timestr = time.strftime("%Y%m%d-%H%M%S")

    if int(log_level) <= int(log_level_arg):
        print(f"{timestr}: {program_name}: {msg_text}")

    return

def clean_date(input_date):
    #2023-09-21T14:54:24+01:00 -> "2023-09-21 14:54:24"

    #NOT USED
    return

def get_country_id(log_level, country_ref):
    country_id = 0

    # Connect to the database (this will create a new file if it doesn't exist)
    db_conn = sqlite3.connect('./db/auction.db')
    db_cursor = db_conn.cursor()

    log_msg(log_level, 3, __file__, f"Finding country record {country_ref}...")
    try:
        query_string = f"SELECT * FROM country WHERE short_name='{country_ref}'"
        country_rec = db_cursor.execute(query_string).fetchall()
        log_msg(log_level, 3, __file__, f"Does exist {country_ref} exist? : {country_rec}")
    except Error as errorMsg:
        log_msg(log_level, 3, __file__, f"Msg after finding country, with error {country_ref}: {errorMsg}")
    else:
        log_msg(log_level, 3, __file__, f"Msg after finding country, no error {country_ref}: {country_rec}") 
        country_id = country_rec[0][0]

    db_conn.close()

    return country_id

def setup_driver(arg_options="default"):
    options = Options()
    if arg_options == "default":
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument('--blink-settings=imagesEnabled=false') #save bandwidth
        options.add_argument("--incognito")
        
    else:
        options.add_argument(arg_options)

    path = '/usr/bin/chromedriver'
    service = Service(executable_path=path) 
    driver = webdriver.Chrome(options=options, service=service) 
    return driver