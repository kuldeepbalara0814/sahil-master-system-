# File Name: step9_monthtrend.py
# Description: Checks if the jodi has already appeared in the current month's results.

def check_monthtrend(jodi, current_month_nums):
    bonus_point = 0
    detail = ""
    
    # Check if the jodi is in the list of numbers that have appeared this month
    if jodi in current_month_nums:
        bonus_point = 3
        detail = "MonthTrend(+3)"
        
    return bonus_point, detail
