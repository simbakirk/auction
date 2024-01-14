#!/bin/bash
# Description: run the auction lots scraper script
# Note- cron errors arrive as command line "Mail"

# Declare variables (if needed)
variable_name="\n<--- Running find_low_bid_lots.zsh script --->"
current_datetime=$(date "+%Y%m%d-%H%M%S")
log_level="3"
BASEDIR=/samba/auction

#Capture output to file -n, supress terminal output
exec > $BASEDIR/output_shell/find_low_bid_lots.log
exec 2> $BASEDIR/output_shell/find_low_bid_lots.err.log

# Main script logic
echo $variable_name
echo "Code base dir: " $BASEDIR
echo "Start " $current_datetime

# Additional commands and logic

cd $BASEDIR
/usr/bin/python3 $BASEDIR/find_low_bid_lots.py $log_level 

echo "End " $(date "+%Y%m%d-%H%M%S")

# Exit the script with a status code (optional)
exit 0
