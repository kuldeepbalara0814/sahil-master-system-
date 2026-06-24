# File Name: step6_murda.py
# Description: Checks if the jodi is a direct Murda (previous result) or belongs to a Murda Family.

def get_family(jodi):
    """
    Creates the complete family (rashi/half-rashi/palat) for a given jodi.
    """
    rashi_map = {'0':'5', '1':'6', '2':'7', '3':'8', '4':'9', '5':'0', '6':'1', '7':'2', '8':'3', '9':'4'}
    j_str = f"{jodi:02d}" if jodi != 100 else "00"
    a, b = j_str[0], j_str[1]
    ar, br = rashi_map[a], rashi_map[b]
    
    return [
        int(a+b) if int(a+b)!=0 else 100, 
        int(b+a) if int(b+a)!=0 else 100, 
        int(a+br) if int(a+br)!=0 else 100, 
        int(br+a) if int(br+a)!=0 else 100, 
        int(ar+b) if int(ar+b)!=0 else 100, 
        int(b+ar) if int(b+ar)!=0 else 100, 
        int(ar+br) if int(ar+br)!=0 else 100, 
        int(br+ar) if int(br+ar)!=0 else 100
    ]

def check_murda(jodi, past_murda_list):
    bonus_point = 0
    detail = ""
    
    # Check if jodi is a direct Murda
    if jodi in past_murda_list:
        bonus_point = 10
        detail = "Murda(+10)"
    else:
        # Check if jodi is in the family of any past Murda
        is_family = False
        for pm in past_murda_list:
            if jodi in get_family(pm):
                is_family = True
                break
        
        if is_family:
            bonus_point = 6
            detail = "MurFam(+6)"
            
    return bonus_point, detail
