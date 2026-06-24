# File Name: step8_baki.py
# Description: Checks if the "Baki" (100 - jodi) is in the past Murda list or the Magic list.

def check_baki(jodi, past_murda_list, magic_numbers_list):
    bonus_point = 0
    detail = ""
    
    # Calculate the Baki (remaining from 100)
    baki = 100 - jodi
    
    # Check if the Baki is in past Murdas or the Magic numbers list
    if baki in past_murda_list or baki in magic_numbers_list:
        bonus_point = 3
        detail = "Baki(+3)"
        
    return bonus_point, detail
