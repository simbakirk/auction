#!/bin/bash
# Description: run the auction lots scraper script
# Note- cron errors arrive as command line "Mail"

# Declare variables (if needed)
variable_name="<--- Running scrape_bids script --->"
current_datetime=$(date "+%Y%m%d-%H%M%S")
log_level="3"
BASEDIR=/samba/auction

#Capture output to file -n, supress terminal output
exec > $BASEDIR/output_shell/scrape_bids.log
exec 2> $BASEDIR/output_shell/scrape_bids.err.log

# Main script logic
echo $variable_name
echo "Code base dir: " $BASEDIR
echo "Start " $current_datetime

# Additional commands and logic

cd $BASEDIR
/usr/bin/python3 $BASEDIR/scrape_bids.py $log_level 48

echo "End " $(date "+%Y%m%d-%H%M%S")

# Exit the script with a status code (optional)
exit 0
