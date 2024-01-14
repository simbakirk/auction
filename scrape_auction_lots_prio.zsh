#!/bin/bash
# Description: run the auction lots scraper script, look 1-2 days ahead only
# Note- cron errors arrive as command line "Mail"

# Declare variables (if needed)
variable_name='\nRunning scrape_auction_lots PRIO script'
current_datetime=$(date "+%Y%m%d-%H%M%S")
log_level="3"
BASEDIR=/samba/auction

#Capture output to file -n, supress terminal output
exec > $BASEDIR/output_shell/scrape_auction_lots_prio.log
exec 2> $BASEDIR/output_shell/scrape_auction_lots_prio.err.log

# Main script logic
echo $variable_name
echo "Code base dir: " $BASEDIR
echo "Start " $current_datetime

# Additional commands and logic
cd $BASEDIR
/usr/bin/python3 $BASEDIR/scrape_auction_lots.py $log_level i-bidder none 1440 2880 

echo "End " $(date "+%Y%m%d-%H%M%S")

# Exit the script with a status code (optional)
exit 0
