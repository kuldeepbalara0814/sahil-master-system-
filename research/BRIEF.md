# R&D BRIEF (sab agent pehle ye padhen)

## Kya hai
Ek **puzzle-logic R&D**: 4 game (FB GB GL DS) ke roz ke number (00-99) me **design/copy** kaise banti hai, kya wo aage chalti hai, aur number nikalne wala system kaise kaam karta hai.
**Sirf paper (kalpnik) trading.** User ka maksad: logon ko vigyan/logic se samjhana; koi pakad sake to khele, nahi to jama-punji na bigade; user poori R&D par faisla lega.
Docs/likhai me jua-satte wala koi shabd mat likho (neutral: puzzle, result, chart, system). Bhasha: **saaf Hinglish (Roman)**, chhote vakya.
**Sabse zaroori: imandari.** Har nateeje ke saath **random (shuffle/permutation) baseline** do, **multiple-testing** ka dhyan (bahut parameters try karoge to kuch na kuch chamakega), **out-of-sample / walk-forward** (aage ka data kabhi mat dekho), confidence interval ya p-value. "Kuch nahi mila" bhi ek valid, kimti nateeja hai. Kisi cheez ko "pakka pattern" tabhi likho jab walk-forward me random se saaf upar ho aur doosre saal me bhi tike.

## Data (repo root = /tmp/claude-0/-root-myproject/d4afdbac-f07c-47bf-ad35-3dfa8ff63430/scratchpad/sms)
- `data/results.csv`: header `date,fd,gb,gl,ds,source`; 2013-01-01 se 2026-11-22 (~4908 din). FD = FB. Number 0-99.
- **DS ki tarikh:** DS usi tarikh ki line me jo agli subah khulta hai. **Mahine ka aakhri din chhuti** (us tarikh ki line nahi). Excel jaisi row ginti: duri hamesha row (box) se, chhuti ki row hoti hi nahi.
- Har game alag: `data/game_fb.csv`, `game_gb.csv`, `game_gl.csv` (2013 se), `game_ds.csv` (**1966 se**, ~21,400 din; col: date,ds). Loader/utility: `lab/gamefiles.py`, `lab/data.py`.
- Python: /data/data/com.termux/files/usr/bin/python3 (numpy, openpyxl, Pillow, flask hai; **scipy nahi** - chi-square/permutation khud numpy se). Repo me `lab/` module hai (`python -c "from lab import data"` repo root se).
- **Resource (phone):** RAM kam (~1 GB free), 8 core. Heavy script ko `nice -n 10` se, ek saath ek hi heavy process, har process <600 MB, foreground command <5 min (lambi cheez background me chalao aur file se nateeja padho). Numpy se vectorize karo.

## Jo user ne sikhaya (poora: patterns/README.md, patterns/HANDOFF.md items 1-46, patterns/006_single_sheet_naksha/README.md, patterns/007_puzzle_steps/README.md, patterns/GLOSSARY.md, patterns/AI_REBUILD_GUIDE.md)
- **Palat:** 28 aur 82 ek (class = min(n, palat)). **Rashi:** number ke har digit me optional +5 (15 rashi: 10 badi 8 number ki + 5 jodi rashi 4 number ki). Cross, jodi, half jodi: GLOSSARY.
- **Duri (gap) = samay (din/row).** Date se date, month se month (same date), dono mila ke (tirchhi), baar (7 din), cell ki jagah. **Same duri sabse zaroori;** number badal sakta hai.
- **Flat** = same din alag location; **Standing** = same location alag din. Seedha = upar se niche (01 se 30); ulta = niche se upar (abhi sikha nahi - mat banao).
- **Step 1, 2, 3, 4:** pehla design apne aap banta hai (system number shuffle karta hai) - kisi se pakda nahi ja sakta; step 2 me doosri copy poori (ab jude pata chalte); step 3 hum step 1-2 dekh kar andaza lagate hai; step 4 pass ke chance kam. Savdhani: pichle 1-2 mahine check karo ki design pehle hi chal chuka ho (to step ginti badhti hai).
- **Boundary:** design ke pehle cell se aakhri cell tak box ginti (dono sire samet), har step me wahi. Andaza wala number boundary ke andar **kisi bhi location me** aaye = PASS, bahar = FAIL.
- **Link** (repeat/cross/rashi), ek link = ek rang, wahi rang har step me wahi link. **Indicator** = ek number jo har boundary me aaya (palat valid), mile to achha, zaroori nahi.
- Ye sab app me bana hai: `lab/scanner.py` (001 copy, 002 naksha, 002b naksha-rashi, 003 family), `lab/dana_farak.py` (005), `lab/steps.py` (007 Puzzle-Steps), `lab/baar.py` (weekday tokri), `lab/gapchain.py`, `lab/band.py`; standalone: `scripts/puzzle_pattern.py`. Tests: `python -m unittest discover -s tests`.
- Ab tak ki jaanch (user ko bata di): koi pattern walk-forward me random se saaf behtar nahi nikla (copy, naksha, family, tokri random jaise; dana-farak saaf box me thoda upar par kamzor; steps random jaisa). Is R&D ka kaam isi ko **gehraai se, 13 saal (DS 66 saal) par** parakhna, sudhar dhundna, ya saaf bataana ki kuch nahi hai.

## Kya dena hai
- Apne folder `research/<naam>/` me: `REPORT.md` (shuruat me 10 line ka saar: kya poochha, kya mila, kya NAHI mila, kitna bharosa), tables (kam se kam ek tulna: asli vs random), `scripts/` (dobara chalane layak, README line ke saath), chhoti CSV/PNG/Excel agar kaam ki ho (bade file nahi, <2 MB, `/sdcard/Download/` me Excel/PDF `Research_<naam>_*.xlsx` bhi rakh sakte ho).
- **Repo ka koi purana code mat badlo** (sirf bug-fix agent badlega). `git commit/push` mat karo.
- Aakhri message (<=250 shabd): sabse zaroori 5 nateeje, kya sudhar sujhaya (code me kahan), kya aage ka kaam.
