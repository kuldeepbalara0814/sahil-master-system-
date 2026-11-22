# 002 Mapping pattern (naksha pattern)

Aap ne (2026-11-22) Telegram se save ki hui ek pic se sikhaya. Pic: `ref_screenshot.jpg` (is folder me). Ye **main ne jaisa samjha waisa** likha hai. **Abhi poora nahi sikhaya gaya**: "step 1, step 2, 3rd step khelna" wala hissa aap baad me bataoge. Isliye ye pattern abhi software me NAHI daala, aur koi test (3-6 mahine) bhi nahi chalaya. Aap ki pushti baaki.

## Pic me kya hai (data se milaya, examples.csv me har cell)
- Do mahine side-by-side. **Baayein = Jan 2017** (pic ki row 16 = 1 Jan 2017, row 15 = 30 Dec 2016 ki line; 31 Dec chhuti). **Daayein = Nov 2026** (row 15 = 2 Nov, row 32 = 19 Nov).
- Pic Nov 2026 ke 19 tarikh ko li gayi (daayein row 32 me sirf 12, 47 the, aage khaali).
- Baayein mahina **poora ban chuka reference** hai (aakhri step row 32 DS = 73). Daayein mahina **aadha bana** hai.
- Rang: narangi, hara, peela, gajari (pic me gulabi dikhti hai), laal dabba. Rang ka koi niyam nahi, sirf aankhon ko saaf dikhe (kaala nahi lete, ank chhup jata hai). **Ek jaisa rang = ek dusre se jodidaar.**
- Gajari chain: baayein 37 (24), 73 (27), 37 (30), 73 (32 DS). Daayein 54 (24 DS), 54 (27 GB), 45 (30 GL), aur **row 32 DS ka khaali gajari cell** = pattern banane wale ka kehna: yahan 54/45 aane ke zyada chance hain, kyunki baayein reference me aakhri 73 DS me hi aaya.

## Mapping pattern kya hai (aap ki baat)
1. Do mahine ek dusre ka **naksha** (map) hain, jaise gali/sadak ka naksha: ek mahine me jo cheez jis jagah (game column, row) aur jitni **Excel row-duri** par hai, dusre me bhi wahi duri par honi chahiye. Gap Excel jaise ginte hain, chhuti ki row hoti hi nahi.
2. Link **number me nahi, design/naksha me** ho sakta hai. Ya to number same ho (62 aur 62, 69 aur 69), ya palat (26 aur 62), ya rashi family (26 ki family: 12 17 21 26 62 67 71 76), ya aapas me koi link na ho bas design same ho: 09 aur 79 peele hain (dono row 20 FB me), 6 din baad baayein 90 (DS) peela, daayein 97 (GL) peela, dono palat bane.
3. Hara-hara: 67 (row 19 FB) aur 75 (row 19 FB); agle din baayein 76, daayein 57 (GL). Number alag, naksha same.
4. **Standing** = do cheezein ek hi column me upar-neeche (jaise GL me 62 aur 69). **Crossing** = aadi-tirchhi.
5. Mahine ko **design ke shuru ke saath barabar** khisakate hain, tarikh ke saath nahi (baayein 1 Jan, daayein 3 Nov row 16 par). Sirf kaam ka hissa crop karte hain (jaise 10 row), baaki ko chhod sakte ho. 7-8 din design banta dikh jaye to pakda gaya.
6. Pattern mahine ke paar bhi chalta hai (May-June ek ke neeche ek, July-Aug aur Aug chal raha). Alag-alag mahine ke pattern ek saath alag-alag jagah chalte hain. **Current mahine ka pattern zyada chalta hai**; purana kam.
7. **Khelna:** current mahine me kam se kam **2 step** ban chuke hon to **3rd step** khelte hain. Us din **FB GB GL DS chaaron khano me** khelte hain; jo location (jaise DS) naksha batata hai wahan aa jaye to fayda zyada. Single, 2 jodi, zyada se zyada 4 jodi; palat bhi chalta hai.
8. 100% pakka nahi: pattern kitna solid match hai aur khojne wale ne kitna khoja, us par depend.

## Facts (pattern ki condition par depend)
- **Column same hona zaroori hai ya nahi, ye pattern ki condition par depend karta hai.** Sirf naksha (same duri par same behaviour) bhi kaam karta hai (09 FB -> 90 DS, 79 FB -> 97 GL). Jagah bhi same ho to pass ke chance badhte hain. **Na jagah ignore karni hai, na naksha.**
- **Mahine ke aakhri din ki chhuti** se game ek din aage-peeche aa jati hai (vibration of game). Isliye mahine ke aas-paas **ek din late/early** aana pass maana jata hai (aap ke 09/90 ek din late aaye, single me aaye = pass). Pakki 1-2 jodi ho to 2 din khelne me nuksan kam.
- 30 aur 31 ka mahina ginna padta hai.
- Result ka time: FB GB GL tarikh wale din 12 baje se pehle; **DS agli subah 5-6 baje, par pattern wale usko pichli tarikh ki line me likhte hain** (2 ka DS 1 ki line me). Ye hamare chart ka niyam hai. DS ko 2 tarikh me likhne par saare pattern ka dhancha bigad jata hai aur koi pattern nahi banega.
- Ye niyam saare pattern banane walon ke liye ek jaise hain, jaise Python ke niyam: usi ke hisab se likhoge to kaam karega. Koi aasan bhasha banaye aur nateeja same de to log wo le lenge.
- Aap ka maanna: pattern banane wala mahine ke shuru me 1-2 pattern pass karwata hai, phir logon ko phasane ke liye wahi banakar fail karta hai. Isliye apna dimaag tez rakhna.

## Is pic ke daayein naksha ka ab ka haal (sirf record, tay kuch nahi)
Daayein row 32 DS = 19 Nov DS. Data me **47** aaya. 20 Nov (95 15 47 76) aur 21 Nov (90 94 41 67) me bhi 54 ya 45 nahi aaya. Yani ye daayein naksha ab tak pura nahi hua.

## Abhi baaki (aap baad me bataoge)
- Step 1 / step 2 / 3rd step ka niyam aur 3rd step ka number kaise nikalte ho (Sawal 5).
- Pass-fail ki parakh ka tareeka (Sawal 6). Parakh sirf pichle 3-6 mahine par hogi.

## Udaharan: 22 Nov 2026, Naksha-Hathi-44 (Sep 2025 jaisa naksha) - aap ne PASS kaha (screenshot 2026-11-22)
Software ne andaza diya tha: **FB me 58 / 85**. Aaj ka FB result **13** aaya. Aap ke hisaab se ye pass hai, aur kyun:
1. **Solid number 4:** naye mahine ki taraf ka number **85** (aur uska palat 58), aur **dusri (purani) taraf ka number 63** (purane mahine me wahi location FB, 2 Oct ki row) aur uska palat **36**. Yani wahi location FB par 85, 58, 63, 36 "super solid" hain, kyunki banane wala udhar wala (purani taraf ka) number bhi de sakta hai.
2. **Family khelte hain:** 85 ki rashi (03 rashi: 03 08 30 35 53 58 80 85) aur 63 ki rashi (13 rashi: 13 18 31 36 63 68 81 86) = **16 number**, ek hi location FB par.
3. **Paise:** sab 16 par 10 Rs ho to 160 Rs. Aap ka tareeka: solid 85 aur 58 par 20 Rs (40 Rs) + baaki 14 number par 10 Rs (140 Rs) = **180 Rs**.
4. **Result:** 13 aaya. 13 63 ki rashi me hai (13 rashi), 10 Rs x 95 = **950 Rs**. Wahi 13 software me **band number** me tha: aakhri baar 24 Jun 2026, yaani **151 din band** (aap ne 150 kaha), aur ab FB me aa gaya.
Maine isko pass ki tarah note kiya. Mera sujhav (aap ki pushti ke baad): jab Naksha ka andaza aaye to software **dono** numbers dikhaye: naye taraf ka (85/58) aur purani taraf ka (63/36), aur dono ki rashi family (16 number), location FB. Solid 4 par zyada paise (jaise 20 Rs) aur baaki par 10 Rs.
Dhyan: ek location par 16 number ka random chance lagbhag 16% hai. 180 Rs lagakar 950 Rs milta hai, isliye faida tabhi jab ye pattern random se zyada baar pass ho. Isko paper trading me naapenge (abhi kuch pakka nahi).

## 23 Nov 2026: 13 saal me kitne milan hain? (aap ka sawal: "2-3 hi kyun?")
Pehle software har lambai (10/12/15/18 line) ka sirf **sabse achha 1** dikhata tha. Ab har lambai ke sabse achhe **6** (ek dusre se 20 din door), kul 24 dikhta hai.
Sach: jaise software milata hai (same/palat number, same jagah) 13 saal me bahut kam milte hain: 10 line me 3-4 jode hi milte hain, 12 me 4-5, 15 me 5-6, 18 me 5-6. Sab random ke best z (6 se 10) ke andar, yaani "kamzor". Sabse zyada milta: May 2022 (15 aur 18 line, 6 jode), Sep 2025 (12 line z 6.4), May 2021.
Aap ki aankh zyada milan dekhti hai (rashi aur sirf rang/design ke link bhi). Wo link software abhi nahi ginta, isliye kam milte hain. Aage: rashi-link bhi ginna.
