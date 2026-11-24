"""Sahil Lab Help: aam sawaalon ke TAIYAR jawab (bina AI ke, zero token). README/HANDOFF/Guide se, sahi aur chhote.

Mel khane ka niyam sakht rakha hai (galat jawab se achha hai ki AI se pooch liya jaye): sawaal me ek 'group' ke SAARE shabd hone chahiye.
Live sthiti (aaj ke number, tarikh) wale sawaal yahan nahi aate: unhe AI live data ke saath jawab deta hai.
"""
FAQ = [
    {"id": "copy", "groups": [["copy", "number"], ["copy", "jodi"], ["copy", "kaise"], ["copy", "button"]],
     "answer": "Number Rank ya Meri Window me jodi ke saamne 'Copy' button hai (Meri Window me 'Sab jodi copy' aur Top 30 ka Copy bhi). Dabate hi numbers copy ho jate hain, phir kahin bhi paste karo."},
    {"id": "open_by_number", "groups": [["pattern", "number", "khol"], ["pattern", "number", "open"], ["number", "se", "khol"], ["pattern", "khol"]],
     "answer": "Aur menu -> Meri Window -> 'Pattern number se kholo'. Kind chuno (Naksha, Family...), number likho (jaise 03) aur 'Kholo' dabao. Rang wala chart khulega aur 'Excel me dekho' button bhi hai. Number wahi hai jo Pattern Scan aur Number Rank me 'Pattern 03' likha dikhta hai."},
    {"id": "scan_time", "groups": [["scan", "kab"], ["scan", "time"], ["scan", "baje"], ["scan", "kitni", "baar"], ["auto", "scan"]],
     "answer": "Roz 3 baar apne aap scan: subah 7:00, shaam 7:00 (19:00) aur raat 12:30 IST. Subah 9:00 baje ek dobara koshish hoti hai (agar pehla der se chala). Manual 'Abhi scan karo' par 30 second ka cooldown hai."},
    {"id": "p009", "groups": [["009"]],
     "answer": "009 Ank-Chal: 2 draw pehle wale number ka ank (andar = dahai, bahar = ikayi) aaj usi game me usi jagah aaye to PASS. Sirf 3 line: DS andar, DS bahar, FB andar. Ye ek ANK (0-9) ka khel hai, jodi ka nahi: 'DS andar 5' = DS ke sirf 50-59, 'DS bahar 9' = 09, 19, ..., 99. Payout 9.5 guna, break-even 10.53%, hit lagbhag 12%. Sirf kagaz ka research hai; asli sabut 24 Nov 2026 se ke record se milega."},
    {"id": "ladder", "groups": [["ladder"], ["fb", "10", "gb", "15"]],
     "answer": "Meri Window ki ladder: pehle FB par har jodi Rs 10; na aaye to GB par Rs 15; na aaye to GL par Rs 20; na aaye to DS par Rs 25. Jis game me hit aaya, us din wahin ruk jao. Hit par har jodi ka 95 guna (40 ya zyada jodi par 90 guna). Do alag pocket hain (Naksha ki jodi, Top 30), har ek Rs 10,000 ka, sirf kagaz par."},
    {"id": "pocket_start", "groups": [["pocket", "kab"], ["pocket", "khaali"], ["pocket", "shuru"], ["graph", "khaali"], ["graph", "kab"]],
     "answer": "Meri Window ki pocket ki ginti 25 Nov 2026 se shuru hai. Pehla poora din tab banta hai jab us din ki line (DS samet) poori ho, isliye graph aur roz ka hisaab pehle poore din ke baad bharte hain. Roz ki tokri subah ke pehle scan me lock hoti hai aur baad me badalti nahi."},
    {"id": "paper_trading", "groups": [["paper", "trading", "kya"], ["paper", "trading", "kaise"], ["paper", "khata"]],
     "answer": "Paper Trading = kalpnik paisa (Rs 10,000), asli paisa nahi. Bet ka result aate hi jeet/haar apne aap likh jati hai. 4 khate alag chalte hain (list10, list10s, single, manual), isliye ek hi number kayi khate me dikh sakta hai; wo duplicate nahi hai. Payout 95 guna (40 se kam number ki list), warna 90 guna."},
    {"id": "wrong_result", "groups": [["galat", "result"], ["result", "galat"], ["result", "badal"], ["result", "hata"], ["result", "delete"]],
     "answer": "Active tab me 'Result dalo (hath se)': wahi game dubara dalo to hath wala result badal jata hai, ya 'Hatao' dabao. Site ka asli result aate hi app wahi ginta hai aur hath wala hat jata hai. Ye kaam PIN se hota hai."},
    {"id": "breakeven", "groups": [["break", "even"], ["breakeven"]],
     "answer": "Break-even = kharcha nikalne ke liye jitna hit-rate chahiye. Jodi par: 1.05% (95 guna payout) ya 1.11% (90 guna). Ank par: 10.53% (9.5 guna) ya 11.11% (9 guna). Isse upar lamba rehna hi fayde ki shart hai."},
    {"id": "andar_bahar", "groups": [["andar", "bahar", "kya"], ["andar", "bahar", "matlab"]],
     "answer": "Kisi bhi number me andar = pehla ank (dahai), bahar = doosra ank (ikayi). Jaise 59 me andar 5 aur bahar 9."},
    {"id": "excel", "groups": [["excel", "download"], ["excel", "kaise"], ["excel", "dekh"]],
     "answer": "Pattern Scan ya Meri Window me pattern ke saamne 'Excel' button hai. Record tab me har game ka poora chart Excel/CSV me milta hai. Sab pattern ek saath ke liye Pattern Scan me 'Sab download' (PDF/JPG/Excel) hai."},
    {"id": "stale", "groups": [["data", "purana"], ["laal", "banner"], ["data", "update", "nahi"]],
     "answer": "Upar laal banner aata hai jab site se naya result nahi aaya. Data tab me 'Abhi fetch karo' (PIN) dabao, ya roz ke 3 auto scan ka intezaar karo. Tab tak 'Aaj ki List' aur pattern purane ho sakte hain."},
    {"id": "ds_rule", "groups": [["008"], ["ds", "rule", "kya"], ["ds", "rule", "kaise"]],
     "answer": "008 DS rule: DS ke 2, 3, 4, 5 draw pehle wale exact number (4 number) roz. Asli hit lagbhag 1.4% vs break-even 1.05% (95 guna). Kagaz ka khata Rs 30 har number, Rs 10,000 se, 24 Nov 2026 se. Active tab me khata dikhta hai. 90 din me faisla nahi hota (kai saal chahiye)."},
    {"id": "pin", "groups": [["pin", "kyun"], ["pin", "kahan"], ["pin", "kya"]],
     "answer": "PIN sirf likhne wale kaam ke liye hai: hath se result dalna, fetch, paper bet lagana, pattern save/delete, Lab idea save/delete. Padhne/dekhne ke liye PIN nahi lagta. PIN yahan bataya nahi jata."},
]
