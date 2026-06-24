# File Name: step5_dayfix.py
# Description: Checks if the jodi is in the fixed list for the current day of the week.

# Day keys: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
DAY_WISE_FIXED = {
    0: [3, 92, 83, 82, 75, 71, 26, 25, 23, 22, 4], 
    1: [72, 98, 97, 91, 87, 82, 71, 62, 54, 41, 40, 29, 23, 18, 13, 10], 
    2: [51, 98, 97, 96, 92, 84, 62, 58, 57, 55, 53, 52, 33, 28, 27, 23, 16, 7], 
    3: [70, 69, 68, 67, 64, 60, 94, 92, 83, 82, 77, 73, 71, 66, 65, 62, 52, 41, 40, 36, 35, 32, 30, 22, 5, 0], 
    4: [95, 90, 89, 88, 87, 84, 82, 72, 40, 39, 38, 37, 34, 33], 
    5: [97, 83, 81, 73, 72, 71, 58, 40, 36, 34, 33, 24, 21, 19, 8, 3], 
    6: [93, 92, 75, 73, 71, 62, 52, 38, 13, 9, 4] 
}

def check_dayfix(jodi, today_weekday):
    bonus_point = 0
    detail = ""
    
    # Get the fixed numbers for today
    todays_fixed_numbers = DAY_WISE_FIXED.get(today_weekday, [])
    
    # Check if the jodi is in today's fixed list
    if jodi in todays_fixed_numbers:
        bonus_point = 5
        detail = "DayFix(+5)"
        
    return bonus_point, detail
