import datetime
import time
from datetime import timedelta
from element_processing import extract_price


print(extract_price("abc £123"))


currentDateTime = datetime.datetime.now() # to calc the duration
time.sleep(2)
duration = datetime.datetime.now() - currentDateTime


# Convert timedelta to seconds
seconds = duration.total_seconds()


print(duration, seconds)
print(type(duration))