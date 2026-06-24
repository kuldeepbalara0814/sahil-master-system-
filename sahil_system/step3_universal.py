# File Name: step3_universal.py
# Description: Checks if the jodi is in the Universal list and if today is the 1st, 2nd, or 3rd of the month.

import datetime

UNIVERSAL_NUMBERS = [2, 20, 4, 40, 6, 60, 24, 42, 28, 82, 46, 64, 68, 86]

def check_universal(jodi, today_date):
    bonus_point = 0
    detail = ""
    
    # Check if today is the 1st, 2nd, or 3rd of the month, AND jodi is in the list
    if today_date.day in [1, 2, 3] and jodi in UNIVERSAL_NUMBERS:
        bonus_point = 10
        detail = "Univ(+10)"
        
    return bonus_point, detail
