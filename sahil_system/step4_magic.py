# File Name: step4_magic.py
# Description: Checks if the jodi is in the Magic list.

MAGIC_NUMBERS = [12, 23, 84, 96]

def check_magic(jodi):
    bonus_point = 0
    detail = ""
    
    # Check if the jodi is in the magic list
    if jodi in MAGIC_NUMBERS:
        bonus_point = 15
        detail = "Magic(+15)"
        
    return bonus_point, detail
