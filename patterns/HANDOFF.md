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
13. **Din (Baar) tab:** saatho weekday ki tokri (seedha 6 + palat box), kab-kab aaya, kaun sa din sabse zyada. Data chunav 1/3/5/13 saal.
14. **Har pattern 2-3 style me dikhao (aap ka kehna):** software me har pattern ko 2 se 3 tarah (style) se dikhana, taaki ek style samajh na aaye to doosre se samajh aa jaye. Jaise: (1) mahine ki sheet par rang me chart, (2) poora mahina har rashi family alag rang me (rashi par click karke sirf wahi family), (3) saaf list/timeline ("ye kaise bana", kab-kab aaya), (4) Excel/PNG download. Rang saaf nazar aane wale, ank kaala. Script ek hi ho sakti hai, par software me dikhana kai tarah se. Jo style aap ko bahut pasand aaya: **rashi par click karke family alag rang** (Family ka poora mahina).

15. (Baad ke liye, abhi nahi) Drive me Google Sheet jisme software ke nateeje likhe jayen, link sirf dekhne ke liye share ho. Script sheet me nahi (copy ho jati hai); software Google service account se likhe, copy me sirf us din ki tasveer aaye. Steps: Google Cloud project -> Sheets API -> service account + JSON key -> Sheet us email ko Editor -> Render env GOOGLE_SA_JSON + SHEET_ID. User ne kaha: lamba kaam hai, baad me kabhi.
16. Pattern 005 (Dana-Farak) software me hai, pushti baaki. 6 mahine ka nateeja 005 README me.
17. **Naksha ab zyada milan dikhata hai (23 Nov 2026):** har lambai ke sabse achhe 12 (pehle 1). **002b Naksha-Rashi (part 2)** bana: naksha ka wahi formula, par link same rashi (movement). Dono "kamzor" nikle (random ke best ke andar). Rashi ke liye random baseline alag naapa (BASE_R in lab/scanner.py). Id `naksha2:L:date`, README 002 me section hai. Aage: rang/design-only link (bina number/rashi), mahine wali copy Naksha ke liye.
18. **APPROVED (user, 23 Nov 2026): Naksha 002 + 002b ka ye version.** User ne kaha "mazza aa gaya, ab naksha me sare dikhata hai achhe se, bahut sunder, sahi samjh ke banaya; isko approved rakhna, khoye na". Approved cheezein: har lambai ke top 12 milan (part 1 same/palat number, part 2 rashi), rang wala purana/naya naksha view, aaj ka andaza, random baseline ke saath strength label. **Isko bina user ke kehne na badlo, na hatao.** Git tag `naksha-approved-2026-11-23` (commit 50452a6) is version ko pakka rakhta hai; wapas lene ke liye `git checkout naksha-approved-2026-11-23 -- lab/scanner.py lab/scan_view.py`. Dhyan: ye "dikhane ka tarika" approved hai; pattern kamai deta hai ya nahi (pushti) alag baat hai, paper trading se naapi jayegi.
19. **Naya look + Active window (23 Nov 2026):** app ka roop naya (indigo, saaf dark/light, neeche 5 tab: Active, Aaj ki List, Pattern Scan, Paper Trading, "Aur" me baaki 8). Andar ka koi formula nahi badla.
   **Active tab:** (1) "Abhi chal rahe" = aaj khelne layak, pattern ke hisab se; (2) "Pichle 1/2/3 din me PASS hue"; (3) Scoreboard pichle 30 din (pass/fail/rate har pattern ka); (4) "Abhi scan karo" manual button. Auto scan din me 2 baar: subah 7:00 IST aur raat 00:30 IST (GitHub Action, baaki cron retry). Agar auto na chala to manual scan se pattern is window me aa jate hain.
   **Registry (data/active_log.json, lab/active.py):** jo pattern ek baar bana wo hamesha rehta hai (gayab nahi hota); pass/fail ka din (`resolved_on`) ek baar likh gaya to badalta nahi. Naksha (002/002b) abhi store nahi hota (user ka pass/fail ka niyam baaki, item 20).
   **Naya pattern jodne ka niyam:** scanner (lab/scanner.py SCANNERS + PATTERNS) me jo bhi pattern items de, jinme `id`, `kind` (naksha/naksha2 ke alawa), `status` ("aaj"/"pass"/"fail") aur `end` (nateeje ki tarikh) ho, wo Active window me **apne aap** aa jata hai; alag code nahi likhna.
   Pattern 005 me ek hi number-set aur ek hi box ke kai pair ek card me dikhte hain (dedupe).
20. **PENDING (user batayega):** Naksha (002/002b) ka bhi pass/fail hota hai, aur wo Active window me aana chahiye. Maine galat likha tha ki Naksha me pass/fail nahi hota. Kaise naapna hai (step 1/2 ke baad 3rd step, kaun sa number/jagah, kitne din), ye user baad me batayega, jab alag-alag tarah ke pattern banna sikh lenge. Tab tak Naksha Active window / scoreboard me NAHI hai (lab/active.py me NOT_STORED = naksha, naksha2). Jab niyam mile: Naksha items me `status` (aaj/pass/fail) aur `end` jodo, phir NOT_STORED se hatao. Bina user ke bataye andaza mat lagao.
21. **Roz ka batch, sab download, Edit (23 Nov 2026):**
   - **Auto scan din me 3 baar:** subah 7:00 IST, shaam 19:00 IST (FB ke baad), raat 00:30 IST (GL ke baad); 9:00 IST dobara koshish. Manual: "Abhi scan karo" (Pattern Scan aur Active tab).
   - **Roz naya batch:** har pattern type ke upar "Aaj ka batch: N pattern | M dekhe". Har card par "Dekh liya" (data/review_log.json, `/api/review`); naya din = ginti 0 se, kal ke dekhe hue nahi ginte (purane pattern wapas aaye to bhi naye sire se). "Sirf bina dekhe" filter, "Sab dekh liya" button. Card par NAYA nishan = pehli baar dikha.
   - **Sab download (har pattern type ke liye):** PDF / JPG (ZIP of page images) / Excel (`/api/scanner/bulk?key=&fmt=&status=`), "Pattern 01, 02..." numbering, pehle Index page. lab/export_all.py (Pillow, PDF/JPG; openpyxl, Excel).
   - **Edit karo (har card par):** pattern ko Pattern window me kholta hai (`/api/scanner/to_board`, localStorage "pedit"); rang badlo, Save, "Excel download" (`/api/pattern/xlsx`). Naksha me do board: Purana mahina / Naya mahina. Sab pattern type (Naksha, Naksha-Rashi, Family, Copy, Dana-Farak) me wahi.
   - Naya pattern jodne par ye sab apne aap milta hai agar scanner ke items me `id`, `kind`, `status`, `name`, `title`, `lines` aur scan_view.view() me us id ka view ho.
   - Dhyan: bade pattern (Naksha ke 48) ka PDF/JPG ~5-6 MB; phone par der lag sakti hai.
