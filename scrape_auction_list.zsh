#!/bin/bash
# Description: run the auction list scraper script
# Note- cron errors arrive as command line "Mail"

# Declare variables (if needed)
variable_name='\nRunning scrape_auction_list script'
log_level="3"
BASEDIR=/samba/auction

#Capture output to file -n, supress terminal output
exec > $BASEDIR/output_shell/scrape_auction_list.log
exec 2> $BASEDIR/output_shell/scrape_auction_list_err.log

# Main script logic
echo $variable_name
echo "Code base dir: $BASEDIR"
echo "Start " $(date "+%Y%m%d-%H%M%S") "Log level: " $log_level

# Additional commands and logic
export PYTHONUNBUFFERED=1
cd $BASEDIR
/usr/bin/python3 $BASEDIR/scrape_auction_list.py $log_level i-bidder 

echo "End " $(date "+%Y%m%d-%H%M%S")

# Exit the script with a status code (optional)
exit 0
