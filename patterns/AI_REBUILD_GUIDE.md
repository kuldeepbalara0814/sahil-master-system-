# AI ke liye: is puzzle-logic R&D ko bina puchhe dobara banane ki guide

**Ye kya hai:** ek **puzzle-logic R&D** (research) hai. Maksad: number ke chart me design/copy kaise banti hai aur koi system kaise kaam karta hai, ye vigyan aur logic se samajhna. **Sirf paper (kalpnik) trading; asli paisa nahi.** Isse user ko apni jama-punji bachani hai: agar koi sach me pakad sake to wo apna faisla le, nahi to na bigade. Docs/app me jua-satte wala koi shabd mat likho (user ka kehna, jab tak R&D poori na ho); neutral "puzzle", "result", "chart", "system" likho.

**Agar tum koi AI ho jise user ne ye file di hai:**
1. **Pehle kuch mat poochho.** Sabse pehle repo ke upar `CLAUDE.md` aur `patterns/SAMAJH.md` padho; phir is guide, `patterns/README.md`, `patterns/HANDOFF.md` (poori), `patterns/006_single_sheet_naksha/README.md` (sikhaai ke niyam) aur `patterns/007_puzzle_steps/README.md` padho. Wahin poora mapping hai.
2. **User ko ek poori script do** jise wo **Termux me copy-paste** karke chala sake (taaki jab chahe model dobara bana le). Seedhi chalne wali script pehle se hai: `scripts/puzzle_pattern.py` (ek file). Agar bug ho to **poori sahi ki hui file** do, "ye line badlo" jaisa adhura jawab nahi.
3. User ki **bhasha: saaf Hinglish (Roman)**, chhote vakya; phone screen par table saaf.
4. **Software sirf dikhata hai, faisla insaan ka.** Koi mark bina logic ke nahi.

## Data
- `data/results.csv`: header `date,fd,gb,gl,ds`. FD = FB (Faridabad). Number 0 se 99 (`0` ko `00` likho). **DS** usi tarikh ki line me likha jata hai (jo agli subah khulta hai). **Mahine ka aakhri din chhuti:** us tarikh ki line nahi.
- Har game ka alag record: `data/game_fb.csv`, `game_gb.csv`, `game_gl.csv`, `game_ds.csv` (DS 1966 se, baaki 2013 se).

## Excel me pattern kaise banate hai (hath se bhi)
1. Teen mahine ek ke neeche ek (Sep upar, Oct beech, Nov neeche), 4 column FB GB GL DS, har row ek tarikh. Box/row se gap ginte hai.
2. **Step 1** = pehle mahine me ek design (kuch cell jude hue). **Step 2** = doosre mahine me **waisa hi** design: **wahi duri (row ka gap) aur wahi jagah (column)**. Number badal sakta hai par yaha script wahi number/palat leti hai.
3. **Boundary** = design ke pehle cell se aakhri cell tak box ginti (dono sire samet). Teeno step me wahi.
4. **Rang:** jude hue cell (ek link) ka **ek hi rang**; wahi rang har step me wahi link. Alag link alag rang. Digits kaale. **Ek link ke sirf do cell** mark karo, bina logic koi cell nahi.
5. **Indicator** = ek number jo teeno boundary me aaya (palat valid), **laal rang**, har boundary me ek cell. Zaroori nahi.
6. **Step 3** = current mahina, adhura: jo link ka pehla cell aaya, uska doosra cell '?' (halka rang). Boundary ke andar andaza wala number **kisi bhi location me** aaya = **PASS** (user ne confirm kiya), bahar = **FAIL**.
7. Pichle 1-2 mahine check karo ki design pehle hi chal chuka ho to step ginke (4th, 5th...) likho; insaan faisla karega.

## Shabd
- **Duri (gap):** samay (din); Excel box se ginti. **Flat:** ek hi din, alag location. **Standing:** ek hi location, alag din. **Palat:** 28 aur 82. **Rashi:** number ke har digit me optional +5 (15 rashi). **Seedha:** upar se niche (01 se 30). **Ulta:** niche se upar (abhi sikha nahi).
- **Step 1/2/3/4:** taal (dhun) ki tarah: pehli thaap random, doosri se dhun pata, teesri hum bata sakte, chauthi kam pakki.

## App ka code (agar app me sudhaar karna ho)
Flask app: `lab_server.py`; pattern ki khoj `lab/scanner.py`, `lab/steps.py` (007), `lab/dana_farak.py` (005); dikhana `lab/scan_view.py`; frontend `lab_static/`. Tests: `python -m unittest discover -s tests` (sab pass hone chahiye). Push se pehle test, aur **sirf wahi push karo jo user ne approve kiya**.

## Kya mat karna
- User ne jo sikhaya nahi (ulta pattern, cross shape, Naksha ka pass/fail niyam) usme **andaza mat lagao**; HANDOFF ke "PENDING" dekho.
- Asli paisa lagane ki salah mat do. Imandari se batao: ab tak koi pattern random se behtar saabit nahi hua.
