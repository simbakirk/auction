#One-time code to create the auction DB and populate static tables

import sqlite3
from sqlite3 import Error
import datetime

#My libraries
import db_functions

# Connect to the database (this will create a new file if it doesn't exist)
conn = sqlite3.connect('./db/auction.db')

# Create a cursor object
cursor = conn.cursor()

tableRowValuesList = []

print(f"Running program {__file__}")

#Create the country table
try:
    cursor.execute("DROP TABLE country")
except Error as errorMsg:
    print(f"Table country not dropped because it doesn't exist {errorMsg}")

try:        
    cursor.execute("CREATE TABLE IF NOT EXISTS country (country_id INTEGER PRIMARY KEY, short_name TEXT, name TEXT)")
except Error as errorMsg:
    print(f"Couldn't create country table: {errorMsg}")
try:
    tableRowValuesList = [(1, "UK", "United Kingdom"), 
                        (2, "US", "United States"),
                        (3, "NL", "Netherlands"),
                        (4, "FR", "France"),
                        (5, "DE", "Germany"),
                        (6, "ES", "Spain"),
                        (7, "IT", "Italy") ]
    cursor.executemany("INSERT INTO country VALUES (?, ?, ?)", tableRowValuesList)
    conn.commit()
except Error as errorMsg:
    print(f"Couldn't populate country table: {errorMsg}")


#Create the auction_type table
table_name = "auction_type"
try:
    cursor.execute(f"DROP TABLE {table_name}")
except:
        print(f"Table {table_name} not dropped because it doesn't exist")
try:        
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({table_name}_id INTEGER PRIMARY KEY, short_name TEXT, name TEXT, timed INTEGER, online INTEGER)")
except Error as errorMsg:
    print(f"Couldn't create {table_name} table: {errorMsg}")
try:
    tableRowValuesList = [(1, "webcast", "Live webcast", 0, 1), 
                        (2, "tender", "Tender online", 0, 1),
                        (3, "timed", "Timed online", 1, 1) ]
    cursor.executemany(f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?)", tableRowValuesList)
    conn.commit()
except Error as errorMsg:
    print(f"Couldn't populate {table_name} table: {errorMsg}")

#Create the product_category table
table_name = "product_category"
try:
    cursor.execute(f"DROP TABLE {table_name}")
except:
        print(f"Table {table_name} not dropped because it doesn't exist")
try:        
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({table_name}_id INTEGER PRIMARY KEY, short_name TEXT, name TEXT)")
except Error as errorMsg:
    print(f"Couldn't create {table_name} table: {errorMsg}")
try:
    #Does this vary by auction platform?
    tableRowValuesList = [(1, "COG", "Consumer goods"), 
                        (2, "ELP", "IT & electricals"),
                        (3, "CAT", "Food & beverage quipment"),
                        (4, "COV", "Automotive & vehicles"),
                        (5, "IND", "Industrial"),
                        (6, "OTI", "Other industries"),
                        (7, "PAM", "Plant & machinery") ]
    cursor.executemany(f"INSERT INTO {table_name} VALUES (?, ?, ?)", tableRowValuesList)
    conn.commit()
except Error as errorMsg:
    print(f"Couldn't populate {table_name} table: {errorMsg}")


# Add try/catch
#Create the auction_platform table
cursor.execute("DROP TABLE auction_platform")
cursor.execute("CREATE TABLE IF NOT EXISTS auction_platform (auction_platform_id INTEGER PRIMARY KEY, short_name TEXT, name TEXT, auctions_url TEXT)")

# Populate the auction_platform table
cursor.execute("INSERT INTO auction_platform (short_name, name, auctions_url) VALUES (?, ?, ?)", ("bidspotter", "Bidspotter", "https://www.bidspotter.co.uk/en-gb/auction-catalogues"))
cursor.execute("INSERT INTO auction_platform (short_name, name, auctions_url) VALUES (?, ?, ?)", ("i_bidder", "I-bidder", "https://www.i-bidder.com/en-gb/auction-catalogues" ))

# Create the auctioneer table
try:    
    cursor.execute("DROP TABLE auctioneer")
except:
        print("Table actioneer not dropped because it doesn't exist")

#FOREIGN KEY (group_id) REFERENCES supplier_groups (group_id) 
cursor.execute("CREATE TABLE IF NOT EXISTS auctioneer (auctioneer_id INTEGER PRIMARY KEY, short_name TEXT, name TEXT, country_id INTEGER, address TEXT, FOREIGN KEY (country_id) REFERENCES country (country_id))")
cursor.execute("CREATE INDEX indexAuctioneerID ON auctioneer (auctioneer_id)")

#*** Just testing for now to check the foreign key contraint ***
cursor.execute("INSERT INTO auctioneer (short_name, name, country_id, address) VALUES (?, ?, ?, ?)", ("Vernon", "Vernon Auctions", 1, "Unit 3, industrial estate, Peterborough"))

#Create the auction table
table_name = "auction"
try:
    cursor.execute(f"DROP TABLE {table_name}")
except:
        print(f"Table {table_name} not dropped because it doesn't exist")
try:        
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({table_name}_id INTEGER PRIMARY KEY, auctioneer_id INTEGER, auction_type_id INTEGER, country_id INTEGER, end_datetime TIMESTAMP, url TEXT, auction_catalog_ref TEXT)")
except Error as errorMsg:
    print(f"Couldn't create {table_name} table: {errorMsg}")
try:
    cursor.execute("CREATE UNIQUE INDEX auctionID ON auction (auction_id)")
    cursor.execute("CREATE UNIQUE INDEX end_datetime ON auction (end_datetime)")
    conn.commit()
except Error as errorMsg:
    print(f"Couldn't populate {table_name} table: {errorMsg}")

#Create the lot table
table_name = "lot"
try:
    cursor.execute(f"DROP TABLE {table_name}")
except:
        print(f"Table {table_name} not dropped because it doesn't exist")
try:        
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({table_name}_id INTEGER PRIMARY KEY, auction_id INTEGER, title TEXT, description TEXT, RRP_GBP REAL, condition TEXT, reserve_bid_price_GBP REAL, url TEXT, product_category_id INTEGER, FOREIGN KEY (auction_id) REFERENCES auction (auction_id),FOREIGN KEY (product_category_id) REFERENCES product_category (product_category_id))")
    cursor.execute("CREATE UNIQUE INDEX indexLotID ON lot (lot_id)")
    cursor.execute("CREATE INDEX indexAuctionID ON lot (auction_id)")
    cursor.execute("CREATE INDEX indexProdCatID ON lot (product_category_id)")
    cursor.execute("CREATE INDEX indexRrpGbpID ON lot (RRP_GBP)")
except Error as errorMsg:
    print(f"Couldn't create {table_name} table: {errorMsg}")
try:
    #*** Just testing for now to check the foreign key contraint ***
    print("Nothing - ignore")
except Error as errorMsg:
    print(f"Couldn't populate {table_name} table: {errorMsg}")


#Create the bid table
table_name = "bid"
try:
    cursor.execute(f"DROP TABLE {table_name}")
except:
        print(f"Table {table_name} not dropped because it doesn't exist")
try:        
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({table_name}_id INTEGER PRIMARY KEY, lot_id INTEGER, amount_GBP REAL, datetime TIMESTAMP, FOREIGN KEY (lot_id) REFERENCES lot (lot_id))")
    cursor.execute("CREATE INDEX indexBidLotID ON bid (lot_id)")

except Error as errorMsg:
    print(f"Couldn't create {table_name} table: {errorMsg}")
try:
    #*** Just testing for now to check the foreign key contraint ***
    print("Nothing - ignore")
    # use this to get date-time to populate the date-time field
    # currentDateTime = datetime.datetime.now()
except Error as errorMsg:
    print(f"Couldn't populate {table_name} table: {errorMsg}")


#Create the scrape table
table_name = "scrape"
try:
    cursor.execute(f"DROP TABLE {table_name}")
except:
        print(f"Table {table_name} not dropped because it doesn't exist")
try:        
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({table_name}_id INTEGER PRIMARY KEY, scrape_entity_type_id INTEGER, entity_id INTEGER, datetime TIMESTAMP, duration TIMESTAMP, crawled_url_count INTEGER)")
    cursor.execute("CREATE UNIQUE INDEX indexScrapeID ON scrape (scrape_id)")
    cursor.execute("CREATE UNIQUE INDEX indexEntitiyIDTypeID ON scrape (entity_id, scrape_entity_type_id)")

except Error as errorMsg:
    print(f"Couldn't create {table_name} table: {errorMsg}")
try:
    #*** Just testing for now to check the foreign key contraint ***
    print("Nothing - ignore")
    # use this to get date-time to populate the date-time field
    # currentDateTime = datetime.datetime.now()
except Error as errorMsg:
    print(f"Couldn't populate {table_name} table: {errorMsg}")

# Commit changes and close the connection
conn.commit()

db_functions.showAllTables(cursor, True, True)

conn.close()
