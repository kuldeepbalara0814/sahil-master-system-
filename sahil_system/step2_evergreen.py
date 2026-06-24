# File Name: step2_evergreen.py
# Description: Checks if both digits of a jodi belong to the Evergreen list.

EVERGREEN_DIGITS = ['3', '8', '6', '1', '9', '0', '7', '2']

def check_evergreen(jodi):
    bonus_point = 0
    detail = ""
    
    # Convert number to a 2-digit string
    j_str = f"{jodi:02d}" if jodi != 100 else "00"
    
    # Check if both digits are in the evergreen list
    if j_str[0] in EVERGREEN_DIGITS and j_str[1] in EVERGREEN_DIGITS:
        bonus_point = 7
        detail = "EverG(+7)"
        
    return bonus_point, detail
