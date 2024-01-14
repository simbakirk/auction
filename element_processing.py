# element_processing.py
# example usage
# myprice = extract_price("1, Lumos Ultra Plus Smart Commuter Helmet, Size M-L, Colour - Charcoal Black (RRP c. ¬£125)")

# This regular expression RRP\s+(\d+(\.\d{2})?) does the following:

# RRP: Matches the characters "RRP" literally.
# \s+: Matches one or more whitespace characters (including spaces or tabs).
# (\d+(\.\d{2})?): This is a capturing group that matches the price. It consists of:
# \d+: Matches one or more digits (the whole number part).
# (\.\d{2})?: This is an optional group that matches a period (decimal point) followed by exactly two digits (the decimal part). The ? at the end makes this group optional to handle prices with or without decimal places.
# This regular expression will capture the price, including both the whole number part and the optional decimal part, into the capturing group. The extracted price will be available in the match.group(1) variable.

import re

def extract_price(input_text):
    # Define the regular expression pattern to match prices - 4 expressions
    price_patterns = [r"\£\s*([0-9,]+(?:\.[0-9]{2})?)", r"RRP\s*([0-9,]+(?:\.[0-9]{2})?)"]

    for p in price_patterns:
        price_raw = ""
        price_as_float = 0.0
        formatted_price = ""
        matches = []

        # Find all matches of the price pattern in the description
        matches = re.findall(p, input_text)

        # If there are matches, convert the first match to a float (the extracted price)
        if matches:
            price_raw = matches[0]
            price_as_float = float(price_raw.replace(',', ''))
            formatted_price = "{:.2f}".format(price_as_float)
            break
        else:
            formatted_price = -0.0

    return formatted_price

#Degbug only - run various tests
# print("Test 1: £ and ,>>", extract_price(r"(REF2336410) 1 Pallet of Customer Returns - Retail value at new ¬£8,039.66 See attached pics of ma"))

# print("Test 2: £ no ,>>", extract_price(r"(REF2336410) 1 Pallet of Customer Returns - Retail value at new ¬£8039.66 See attached pics of ma"))

# print("Test 3: RRP and ,>>", extract_price(r" Brand New Sunred Valencia Heater RRP 779. New in the 2020 SunRed collection: the sleek Valencia lounge heater that combines style and comfort. Perfect to use on the terrace, in the garden, or on the balcony. Invite friends and family to a party and give them a warm welcome. "))

# print("Test 4: RRP no ,>>", extract_price(r" Brand New Sunred Valencia Heater RRP 7,79. New in the 2020 SunRed collection: the sleek Valencia lounge heater that combines style and comfort. Perfect to use on the terrace, in the garden, or on the balcony. Invite friends and family to a party and give them a warm welcome. "))



