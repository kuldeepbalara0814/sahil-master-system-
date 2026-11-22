# 004 Baar tokri (weekday ke zyada aaye number)

Aap ne (2026-11-22) sikhaya. Ye **main ne jaisa samjha waisa** likha hai. Aap ki **pushti baaki**. Software me ye **hint (highlight)** ki tarah hai, koi number hatata nahi. Koi pic nahi, isliye ref_screenshot nahi.

## Aap ne kya kaha (maine apne shabdon me)
1. **Baar** = weekday (Sunday, Monday, Tuesday ...). Har baar ki apni alag list banti hai.
2. Us baar ko jo number **baar-baar sabse zyada** aaye unko ek **tokri** me daalo, **6 number**. (Aap ne Jan 2026 se Oct 2026 ke din liye.)
3. Un 6 ke **palat** jodo. Kul lagbhag 12 number (kuch number ka palat khud wahi ya list me pehle se hota hai).
4. Ek mahine me ek baar mostly **4 baar** aata hai, kabhi **5 baar**. Dekhna hai ki us mahine us baar ko tokri ka koi number **kam se kam ek baar hit** hua ya nahi.
5. **Mahine ka chakkar:** mahine ke pehle baar se khelna shuru, **5 baar tak try**. Agar mahine me sirf 4 baar hain to **agle mahine ka pehla baar** 5th ginte hain (jaise Jan me 4 Monday to 2 Feb bhi). Dekhna ki kisi mahine me 5 baar me ek bhi hit nahi aaya, yani fail.
6. **Stake ka tareeka (aap ka sawal):** pehle baar 5 Rs (number par), fail to 10, fail to 20 ... aise chale to loss ya profit? Aur sirf un baar ke liye jo zyada pass dete hain.
7. **Filter ki tarah:** agar aaj aap ke paas koi 30 jodi hai aur aaj Budhvar hai, to Budhvar ki tokri ke number highlight ho jayen, taaki chhantna aasan ho. Faisla aap ka.
8. Aapne poocha: 1 saal ki jagah **13 saal** ke data se 6 jodi chune to kaisa rahega.

## Jan-Oct 2026 ki tokri (aap ke kehne par, har baar ke 6 number, zyada se kam kram me)
Ravi: 88 (6), 06 (5), 21, 23, 31, 40 | Som: 39 (5), 59 (5), 10, 19, 46, 54 | Mangal: 08, 13, 49, 58, 83, 00 | Budh: 90 (6), 85 (5), 19, 42, 84, 01 | Guru: 26 (5), 33 (5), 40, 47, 53, 74 | Shukra: 35 (7), 71, 72, 74 (5 each), 02, 34 | Shani: 32, 58, 62, 04, 16, 21.
(Barabari par chhota number pehle liya. 4/3 baar wale aur number bhi barabar ke the.)

## Mere check (sirf dekhne ke liye, parakh nahi)
- **Mahine me ek baar hit (7 baar, 24 mahine, saaf tareeka: har mahine ki tokri sirf us mahine se pehle ke 365 din se):** Budh aur Shukra sabse achhe (2/24 fail), Som sabse kharab (7/24 fail). Par random me bhi 12 number ke saath ~10% mahine fail hote hain, isliye **koi weekday random se behtar nahi** dikha.
- **Stake 5, 10, 20, 40, 80 (chaaron game, 95 guna, pehle hit par ruko):** 24 mahine me Budh +8,495 Rs, Shukra +1,110 Rs, baaki ghate me, saaton ka kul **-46,520 Rs**. Ek jeet wala mahina 425-818 Rs deta hai, ek fail mahina 4,750-6,820 Rs le jata hai (5 baar fail par ek mahine me 7,440 Rs tak). Double karne se hit ka chance nahi badhta.
- **Tokri ko family pattern par filter ki tarah:** 8-number rashi me tokri ka number tha to pass 30.1%, nahi tha to 29.7%. Farak nahi. Pass me aaye number tokri me 13% (random 12%).
- **Kitne purane data se tokri (36 mahine, 252 jodi):** 1 saal ki tokri me 32 fail, 3 saal 23, 5 saal 26, 13 saal 23; random me ~25. 13 saal wali bhi **random ke barabar**, din-wise hit 37.5% (random 38.4%).

## Software me
- **Aaj ki List tab → "Baar Filter":** aaj ka baar (ya koi bhi weekday) ki tokri dikhti hai (1 saal, 3 saal, 5 saal ya 13 saal ke data se). Apni jodi (jaise 30) paste karo, jo tokri me hain wo narangi me chamkti hain. Sirf hint hai.
- Ye faisla **insaan ka** hai, software sirf dikhata hai (HANDOFF item 10).

## Baaki (aap bataoge)
- Tokri kitne purane data se banani hai (1 saal ya 13 saal): abhi 1 saal rakha hai, chunne ka option hai.
- 16 number ka set (aap ne ek baar "16 number" kaha tha): 6 + palat = ~12, 8 + palat = ~16. Dono ki jaanch ki, aap bataoge kaun sa.
- Is hint ko kahan aur dikhana hai (pattern card me bhi?).
