# HANDOFF: pattern sikhane ke niyam aur facts (jo bhi naya aaye, yahin jodna)

Ye file naye session/engineer ke liye hai taaki aap ko baar-baar samjhana na pade.

## Kaam ka tareeka
1. Aap ek-ek pattern sikhate ho. **Aap poora bata do tab tak main sawal nahi poochta / kuch test nahi karta.** Phir main apne shabdon me README likhta hoon aur ek-ek sawal poochta hoon. Aap ki pushti ke baad hi pattern pakka.
2. Pattern ke folder (`patterns/NNN_naam/`) me: README.md, examples.csv (har nishaan data se jaancha hua), reference pic, (zarurat par) spec.json aur Excel.
3. **Sirf wahi pattern software me jayega jo parakh me fayda dikhaye** (kachra jama nahi karna).
4. Pattern sirf **3-6 mahine** valid hai. Parakh sirf pichle 3-6 mahine par, 13 saal par nahi (jab tak aap na kaho).
5. Typing ki chhoti galtiyan (jaise "jun 2017" = Jan 2017) sandarbh se khud sudhaar lo.
6. Data aur copy Google Drive ke folder "Pattern Learning" me bhi rakhi jati hai; 5 pattern ho jayein to software me push aur Drive STATUS me "PUSH HUA".

## Game / data ke facts
- Game: FB (code me FD), GB, GL, DS. Number 00-99.
- FB GB GL tarikh wale din 12 baje se pehle; DS agli subah 5-6 baje. **DS pichli tarikh ki line me likhte hain.** Galat likhne par har pattern bigad jata hai.
- Mahine ke aakhri din ki chhuti. Isse game ek din aage-peeche (vibration). Mahine ke aas-paas +-1 din ka farak pass maana jata hai.
- Gap Excel jaise ginte hain: row ki duri. Chhuti ki row nahi hoti.
- Excel me rang sirf aankhon ke liye; ek jaisa rang = ek dusre se jodidaar. Kaala rang nahi (ank chhup jata hai).

## Shabd
Rashi, cross, jodi, half jodi, gap: `GLOSSARY.md`. Mapping/naksha pattern: `002_mapping_pattern/README.md`.

## Software me pattern (Pattern Scan tab)
- `lab/scanner.py`: har sikhaya hua pattern ek `scan_xxx(rows, asof)` hai aur `PATTERNS` list me ek entry. **Naya pattern sikhaya to yahin jodo** (scan function + PATTERNS + SCANNERS), phir wo apne aap roz chalega.
- Roz subah data aate hi `lab/update.py` (GitHub Action) scan chalata hai aur `data/patterns_today.json` banata hai. App me tab **Pattern Scan** hai: aaj kya ban raha hai, saaf rang wala chart, Excel download, aur **manual "Script abhi chalao"** button (galti aaye to wahi dikhti hai).
- Har pattern ko apna naam milta hai (Naksha-Hathi-44, Copy-Sher-50) taaki mix na ho. `lab/scan_view.py` chart aur Excel banata hai.
- 001 Jodi-Copy aur 002 Naksha scan chalte hain. 002 abhi 'Naksha' ke naam se same/palat links ka milan dekhta hai (aap ke pic ke design ko poora nahi pakadta, sudhar baaki).

## Game ke window aur samay (aap ne bataya, 2026-11-22)
FB, GB, GL, DS ek hi company ke 4 window hain (ek game hota to log 60-80 number khelte aur company ko nuksan hota, isliye load baant diya).
FB result 6:15-6:30 pm | GB 10:00-10:15 pm | GL 12:00-12:15 am | DS 5:20-5:40 am (window 2:30 am band). Mere samajh se baaki window result se 40 minute pehle band (pakka nahi).
Isliye DS agli subah ka hai aur pichli tarikh ki line me likhte hain. App ka auto-fetch DS ke liye subah 5:45 ke baad chalta hai.

## Pass ke prakar (sab pattern ke liye, jab tak aap alag na kaho)
Din par pattern ka koi number kisi bhi game me aaya = PASS, nahi aaya = FAIL. Pattern ne jis location (game) ka andaza diya wahan aaya = with location, doosre game me aaya = out of location (variation); dono PASS.

## Sikhane ka kram (zaroori)
1. Pattern poora sikhao, main apne shabdon me README likhunga, phir ek-ek sawal poochunga. 2. Aap ke sawal main uttar dunga, galti ho to turant sahi karunga. 3. **Pushti ke baad hi software me**, pushti se pehle app me "pushti baaki" ka nishan rahega. 4. Jab tak pichla pattern sahi na ho, agle par nahi jaunga. Kachra jama nahi karna.

## Software ka usool (aap ne bataya, 2026-11-22)
1. **Sikhane ka tareeka:** ek-ek cheez alag sikhate hain: rashi, design, gap, standing/cross/repeat, same duri ka matlab, variation, sab game me kyu khelna, chhuti kab, FB GB GL DS kya, rang kyu aur kaise. Sab saaf alag-alag, **mix-sabzi nahi** (na khud confuse, na saamne wale ko kachra dena).
2. **Rang sirf sikhane/dikhane ke liye** ki kaun sa pattern kaisa banta hai. Paper trading me **jo bhi pattern bane wo khela jayega.** Machine dekhega kaun sa zyada pass, kaun sa kam, aur graph banayega. Machine ka dimaag sirf feed kiye hue pattern tak seemit nahi, wo aur pattern bhi try karega.
3. **Dikhane ka tareeka (insani aankh ke liye):** ek mahine me ek jaise kai pattern bane hon to us mahine ki **ek se zyada copy** banao, har copy me **ek hi pattern saaf alag rang me**, phir sabhi copy ko **ek image me jod do.** (Abhi banana baaki, aap ki pushti ke baad.)
4. **Jab location ya design ek se zyada jagah saaf na ho** (ek din me family ke kai cell, kai jagah same design): software location tay nahi karta, sirf pattern dikhata hai aur "ek se zyada jagah ban raha hai" ka mark lagata hai. Insan aankh se dekh kar tay karta hai. Aap README me baad me jo bhi jodna/badalna chahein jod sakte hain, hum use time aur halat ke saath saaf karte rahenge.
5. **Paper trading ka stake:** aam taur par har number par 10 Rs, jahan pattern ka location saaf ho wahan 2 guna (20 Rs). Paise 5 ke multiple. Ye sirf software ko majboot karne ke liye paper trading hai, asli paise se khelna nahi.
6. **Pattern ki index (app me):** har pattern ka ek naam (jo main deta hoon, jaise Family, Naksha, Jodi-Copy) aur har ek ka apna README (kaise bana). Aap README me galti pakdo to mujhse sahi karwao. Index me naam par click karo (jaise Family pattern) to us pattern ke **jitne bhi abhi chal rahe hain** sab dikhte hain. Har chalta pattern bhi apna alag naam rakhta hai (Family-Sher-11).
7. **Ek mahine me kai pattern:** ek hi mahine me family pattern kai ek saath banta hai, to **same mahine ki sheet ki alag-alag copy** banti hai, har copy me ek pattern **alag rang** me. Rang koi bhi chalega, bas **niche ka ank saaf dikhe** (rang par kaala ank, kaala bhara cell nahi). Pattern bhi saaf dikhe. **Tarikh, mahina, saal saaf likha ho**, zarurat ho to remark. Saari copy ek image me jud sakti hain.
8. **README aur sikhna pehle, push baad me.** Pattern sahi sikha aur README sahi likha hona zyada zaroori hai; git push baad me bhi ho sakta hai.
9. **Naksha (mapping) me khelne ka tareeka (aap ka udaharan 22 Nov):** location par solid number = naye taraf ka number + palat aur purani taraf ka number + palat (4 number). Phir dono ki rashi family (16 number). Solid par zyada, baaki par 10 Rs. Pass tab jab family ka koi number us location par aaye. Band number (bahut din se band) agar family me aaye to wo bhi note karo.
10. **Kaam ka batwara (zaroori):** software ka kaam **dikhana** hai: pattern, band number/rashi, family, location, mark. **Faisla insaan ka** (aap ke dimaag ka): kya khelna hai, kitna, kahan. Jaise 22 Nov: software ne 13 ko "150 din se band" dikhaya, aap ne dekha ki 63 ki family me 13 hai aur wahi par khela. Software shuru me madad karta hai; aap decide karte ho; phir sudhar aap ki baat ya mere sujhav se, dheere-dheere. Koi cheez ek din me nahi banti.
11. **App me kya hai (2026-11-22):** tab **Pattern Scan** (index: pattern ka naam, README, abhi chal rahe pattern, mahine ki copy alag rang me, PNG image download, Excel, manual "Script abhi chalao"), **Pattern** tab (rang bharo/save), **Aaj ki List** me Dost jodi, Band Rashi/Number, **Baar Filter** (aaj ke baar ki tokri highlight), **Record** me Gap Filter. Roz subah GitHub Action aur app khulne par data aur scan apne aap. 001, 002, 003, 004 sab par "pushti baaki" jab tak aap pakka na karo.
12. **Jaanch ka sach (abhi tak):** koi bhi pattern (copy, naksha, family, baar tokri) random se behtar saabit nahi hua. Software dikhane aur sikhane ke liye hai; paper trading me napenge. Asli paise se khelna nahi.
