#Generic functions to manage SQL DB activity and reporting
DB_PATH = './db/auction.db'
SCRAPE_ENTITY_AUCITON = 1
SCRAPE_ENTITY_LOT = 2
SCRAPE_ENTITY_BID = 3


# Generic function to show all rows and col values for the given table
def showAllValues(cursor, tableName):
  # first check that the table exists
  cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
  schemaTableList = cursor.fetchall()  
  print(schemaTableList)
  tableTuple = (tableName,)
  if tableTuple in schemaTableList:
    print(f"Table {tableName} exists")
    queryString = f"SELECT * FROM {tableName}"
    tableRowsList = cursor.execute(queryString).fetchall()
    for row in tableRowsList:
      print(row)

  else:
    print(f"Table {tableName} doesn't exist")
    
# Show All Tables
def showAllTables(cursor, showValues = False, showIndeces = False):
  """Generic function to display all tables in a DB schema, and their values"""
  print(f"Showing all tables, with values? {showValues}")
  cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
  schemaTableList = cursor.fetchall()

  for row in schemaTableList:
    #print(row)
    if showValues:
        # SQL injection risk  
        queryString = f"SELECT * FROM {row[0]}" 
        showAllValues(cursor, row[0])

  #Currently this isn't linked to the table so just shows all indeces - only show per table and then include in for loop above
  if showIndeces:
      print(f"Showing all indeces")
      indexList = cursor.execute("SELECT name FROM sqlite_schema WHERE type='index'").fetchall() 
      for indexRow in indexList:
          print(f"Index {indexRow}")
  return

def db_connected(arg_cursor):
    connected = True
    try:
      arg_cursor.execute("Select 1")
    except Exception as errorMsg:
       connected = False
    return connected