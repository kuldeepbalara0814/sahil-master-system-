# 005 Dana-Farak (4 Din Box)  [pushti baaki]

Aap ne sikhaya, maine apne shabdon me likha.

## Dana
Dana 10 aur dana 01 ek hi dana hai (sidha/palat pata nahi hota). Do number ka farak palat laga ke dekhte hai:
97-87=10, 79-78=01. Farak 10 ya 01 ho to "dana-farak" bana. Farak 20, 02, 30 jaisa nahi chalta.
Disha (badha/ghata) ka farak nahi: 10->20 ya 20->10 same pattern.

## 4 Din Box
- Box = din 1 se din 4. Din 1 = pehle number ki tarikh. Box ki aakhri line din 4 ka DS.
- Box ke andar kisi bhi din, kisi bhi game me do number aaye jinme dana ka farak ho (sidha ya palat) = pair ban gaya. Ek hi din me bhi ban sakta hai.
- Khelna pair banne ke baad wale game se (GL me bana to DS tak) -- din 4 ke DS tak. Location nahi.
- Pass: khelne ke number me se koi bhi ek aaye (dobara aana bhi pass). Nahi aaya to fail.

## Khelne ke number (part 1)
- 10 aur 20 aaye -> 10 01 20 02 (4 number). 54 aur 35 -> 54 45 35 53.
- Ek hi number do baar (45, 45): dono dana lagte hai -> 45 54, 46 64, 53 35 + jodi 55 = 7 number. (78,78 -> 78 87 79 97 86 68 + 88; 88 meri maan-ni, aap ne 6 gine the.)

## Part 2: 3 ki series
- 3 number lagatar (dana ke farak se) = series. 3 se zyada kabhi nahi. Jaise 40 41 + 42 ya 01 02 + 03.
- Pair ke saath series ke agle/pichle number "spot" ki tarah mark: 40,41 ke liye 39/93 aur 42/24; 01,02 ke liye 03/30 (aap ne 01 02 10 20 03 30 me koi bhi = pass kaha). Khelna aap ki marzi, software sirf yaad dilata hai. 04 jaisa (farak 2) galat.
- Series ka beech ka number gayab (40 aur 42, ya 14 aur 43->beech 24/42): sirf beech wala (41/14) khelte hai: ya wahi aayega ya fail. Usi 4 din box me. Ban jane ke baad ke game se din 4 DS tak.
- 3 ki series poori ho gayi to us series me aage kuch nahi khelte.

## Confusion
Ek box me ek se zyada pair bane: software khud skip nahi karta. Niche Hinglish note: "Game saaf nahi bana, confusion hai, khelne se pehle anubhav se soch-vichar karo, skip karna uchit ho sakta hai." Faisla aap ka.
Paper trading: saaf box aur confusion box ka pass rate alag alag dikhana (aap ne haan kaha).

## Baaki
- Overlap (pair B ka box A ke beech me shuru) ki exact skip ginti aap ne "ankho se dekho + note" kah ke tay ki.
- Pichle 6 mahine me bana ke dekhna (aap ne kaha) -- aap ke "end" ke baad.
