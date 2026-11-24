# 007 Puzzle-Steps (3 mahine ek sheet par step 1 / 2 / 3)  [APPROVED version, user ne kaha "push kar do live"]

Ye ek **puzzle-logic R&D** hai: number ke chart me design (copy) kaise banta hai aur wo aage kaise chalta hai. **Sirf paper trading, asli paisa kabhi nahi.**
Ye pattern user ne **kai baatein** alag-alag samjhayi (006 README me poori sikhaai); yaha unka **ek jagah, kaam karne wala roop** hai.

## Sheet kaise banti hai (Excel me)
- **Ek lambi sheet:** 3 mahine ek ke neeche: **sabse upar (current mahina - 2), beech me (current - 1), sabse neeche current mahina.** (Jaise Sep, Oct, Nov.)
- Har row = ek tarikh, 4 column: **FB GB GL DS**. Mahine ke aakhri din ki row hoti hi nahi (chhuti). **Duri hamesha Excel ke box (row) se ginte hai.**
- Current mahine ke neeche aane wali tarikhon ki **khali rows** (mahine ke aakhir tak) rakhte hai, wahi '?' wale box ke liye.

## Step aur boundary
- **Step 1** = upar wale mahine me bana design. **Step 2** = beech wale mahine me **waisa hi** design. **Step 3** = current mahine me **waisa hi bana raha** design (adhura). Hum step 1 aur 2 dekh kar step 3 ka andaza lagate hai.
- **Boundary** = design ke **pehle cell se aakhri cell tak box (row) ginti, dono sire samet.** Boundary ki lambai (L box) **teeno step me wahi.** App me L = 8, 10, 12 try hota hai.
- Excel/PDF me boundary **moti border** se dikhti hai.

## Link aur rang
- **Link** = boundary ke andar do cell jinme **wahi number ya uska palat** (28 aur 82 ek) aaye. Link = (pehla cell: boundary ka i-va box, location a) -> (doosra cell: j-va box, location b). **Jo link step 1 me hai wahi (wahi box, wahi location) step 2 me bhi hona chahiye;** kam se kam 2 link (shuruat ek se ho sakti hai, par app 2 se kam nahi dikhata).
- **Rang ka niyam:** **ek link = ek rang** (link ke dono cell ka ek hi rang). **Wahi rang step 1, step 2 aur step 3 me wahi link.** Alag link = alag rang. Rang hi pehchan hai. Digits kaale, rang chamakdaar.
- Rang list: narangi, baingani, aasmani, hara, gulabi, peela, neela, bhura (is kram me).
- **Ek link ke do hi cell mark** hote hai (kabhi do-do cell ek hi baat ke liye nahi).

## Step 3 ka adhura design aur '?' (jamuni/halka rang)
- Step 3 me jo link **pura ban chuka** (dono cell aa gaye), uske cell us link ke rang me.
- Jis link ka **pehla cell aa chuka, doosra cell abhi aage** hai: pehle cell ka rang, aur doosra box **halke rang me '?'** (aur likha hota hai kya aana chahiye: us number ka number/palat). **Boundary ke andar** wo number aaya to **PASS**; boundary ke **bahar** (ya boundary ke baad) aaya to **FAIL**. **User ne confirm kiya (23 Nov 2026): location ka koi chakkar nahi** - andaza wala number boundary ke andar **kisi bhi location me** aa jaye to PASS (jaise GB bataya aur DS me aa gaya to bhi theek). Step 3 me link ka doosra cell bhi isi tarah: pehle cell ke baad boundary ke andar wahi number/palat **kisi bhi game me** aaye to link bana; us cell ko link ke rang me rangte hai.
- Jis link ke **dono cell** abhi aage hai: **dono box '?'** (halke rang me), bina number ke. Jab pehla aa jaye to uska number (aur palat) agle box ki location me **single khelne layak** hai (software sirf dikhata hai).

## Indicator (laal)
- **Ek hi number** (palat valid) jo **teeno boundary me** aaya, **kahin bhi** (same duri zaroori nahi). **Har boundary me sirf EK cell** laal (agar wahi number ek boundary me do baar aaye to bhi ek hi cell). Link ka rang pehle se ho to us cell par **laal moti border**.
- **Indicator zaroori nahi.** Mile to pattern pakka hota hai; na mile to bhi design ban sakta hai.

## Dikhane ke tareeke (app me)
1. **Ek sheet** (upar Step 1, beech Step 2, niche Step 3): default.
2. **Side-by-side** 3 block: Step 1 | Step 2 | Step 3 ek ke baad ek.
3. **Excel** (har design ki sheet) aur **PDF/JPG** (Pattern Scan me "Sab download").
- Har design card par "Dekh liya", "Edit karo" (Pattern window me rang badlo), bhi aate hai.

## App me kaise chalta hai
- **Apne aap:** din me 8 baar scan (FB ke baad 18:45, GB ke baad 22:45, GL ke baad 00:30, subah 7:00 final; har ek ka retry), aadhi line (aaj ke aa chuke FB/GB/GL) ke saath Step 3 aage badhta hai + **manual "Abhi scan karo"** button (Pattern Scan aur Active tab). Script me galti aaye to sirf us pattern me dikhti hai (error box), baaki chalte rehte hai. **Har jagah manual option hai.**
- Naye result ke saath **roz naye design** banenge (Step 3 ki boundary aage badhti hai).
- Active tab aur Number Rank (aaj ke vote) me ye apne aap judta hai.
- **Result abhi site se fetch hota hai** (rakha hai). Aage user hath se Excel me result dekar bhi data de sakte hai.

## Imandari se (jaanch, 23 Nov 2026)
(Location ki chhoot dene se milan aur aasan ho gaya, isliye random me bhi ab zyada milega.)
Asli data me aise 2-3 link wale design mil jate hai, par number ko idhar-udhar (shuffle) karke wahi khoj chalayi to **random me bhi utne hi** mile (3 se 4 link). Yani **abhi koi saboot nahi ki ye aage chalta hai.** Paper trading se pass/fail naap ke dekhenge.

## Abhi NAHI banaya
Cross (X) ka shape, **ulta (reverse)** pattern, flat/standing ki alag jodi, "location koi bhi" wale link, **2 mahine jod ke** wala roop (sirf 3 mahine wala hai), rashi/cross link (sirf wahi number/palat).

## Script (kisi bhi AI/Termux me dobara banane ke liye)
`scripts/puzzle_pattern.py` (ek file, copy-paste): `python puzzle_pattern.py data/results.csv --out <folder>` -> `puzzle_steps.xlsx` aur `puzzle_steps.pdf`. App ka code: `lab/steps.py`. Poori vidhi: `patterns/AI_REBUILD_GUIDE.md`.
