#!/bin/zsh
# Declare variables (if needed)
variable_name="\nRunning cron_test script"
log_level="2"
BASEDIR=/samba/auction

#Capture output to file -n, supress terminal output
exec > $BASEDIR/output_shell/cron_test_basedir.log
exec 2> $BASEDIR/output_shell/cron_test_basedir.err

# Main script logic
echo $variable_name
echo "Script location: $BASEDIR"
echo "Start " $(date "+%Y%m%d-%H%M%S") "Log level: " $log_level
echo "End " $(date "+%Y%m%d-%H%M%S")

# Exit the script with a status code (optional)
exit 0
