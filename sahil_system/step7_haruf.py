# File Name: step7_haruf.py
# Description: Checks if the jodi contains today's date Haruf/Rashi or the weekly trending Harufs.

def check_haruf(jodi, today_date, use_haruf_bonus, top_harufs):
    bonus_point = 0
    details = [] # Using a list here because a jodi might pass both Haruf checks
    
    j_str = f"{jodi:02d}" if jodi != 100 else "00"
    
    # 1. Date Haruf & Rashi Logic
    # Get the last digit of today's date (e.g., if date is 23, outer_haruf is 3)
    outer_haruf = int(str(today_date.day)[-1])
    rashi = (outer_haruf + 5) % 10 # Adding 5 gives the rashi
    
    if str(outer_haruf) in j_str or str(rashi) in j_str:
        bonus_point += 5
        details.append("Haruf(+5)")
        
    # 2. Trending Haruf Logic (from last 7 days)
    if use_haruf_bonus == 'Y' and (j_str[0] in top_harufs or j_str[1] in top_harufs):
        bonus_point += 5
        details.append("TrendHaruf(+5)")
        
    return bonus_point, details
