# get_bid_timestamp.py
# Work out the actual date-time that the bid was placed
import datetime
import random
import re
from auction_functions import log_msg


"""Returns the date-time that the bid was placed."""
def get_bid_datetime(log_level: int, bid_scraped_at: datetime.datetime, bid_label: str) -> datetime.datetime:
    bid_datetime = None
    secs_to_subtract = 0

    regex = re.compile(r'(\d+)\s+(minute|hour|day)')
    match = regex.match(bid_label)
    if match:
        log_msg(log_level, 3, __file__, f"Number: {match.group(1)}, Unit: {match.group(2)}")

        if match.group(2) == "day":
            secs_to_subtract = int(match.group(1)) * 24 * 60 * 60
        elif match.group(2) == "hour":
            secs_to_subtract = int(match.group(1)) * 60 * 60
        elif match.group(2) == "minute":
            secs_to_subtract = int(match.group(1)) * 60
    else:
        log_msg(log_level, 3, __file__, f"Non numeric label")

        if bid_label == "yesterday":
            secs_to_subtract = 24 * 60 * 60
        elif bid_label == "a few seconds ago":
            secs_to_subtract = 60 

    bid_datetime = bid_scraped_at - datetime.timedelta(seconds=secs_to_subtract)
    log_msg(log_level, 3, __file__, f"Recorded at : {bid_scraped_at}, {bid_label}, {secs_to_subtract}, Bid at : {bid_datetime}")

    return bid_datetime

