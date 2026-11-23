> **AI ya naye insaan ke liye:** pehle `AI_REBUILD_GUIDE.md` padho (bina puchhe poora mapping + script).
>
> **Ye kya hai:** ek **puzzle-logic R&D** (khoj) hai. Hum jaanna chahte hai ki number ke chart me design/copy kaise banti hai aur koi system/machine kaise kaam karti hai. **Sirf paper trading** (kalpnik), asli paisa kabhi nahi. Maksad: jo log is lat se jude hai unhe **vigyan aur logic ke aadhar par** samjhana. Agar koi sach me pakad sake to wo khele; agar nahi pakad sakta to apni jama-punji kharab na kare. Faisla poori R&D ke baad.

# Pattern library (aap sikhate ho, main likhta hoon)
Har pattern ka folder: README.md (main kaise samjha), examples.csv (aap ke nishaan), spec.json, Excel copy (scripts/pattern_excel.py), screenshot.
Niyam: pattern sirf 3-6 mahine me parkho. Aap ki pushti ke baad hi pakka maano. Bahut pattern ikathe hone par software (lab/) me daalna: roz pattern pakde, app me dikhaye, Excel me rang se mark kare, aur jo pattern ruk jaye use band kare.
| id | naam | haal |
|---|---|---|
| 001 | copy pattern | likha, aap ki pushti baaki |
| 002 | mapping pattern (naksha) | dikhane ka version APPROVED (23 Nov 2026, tag naksha-approved-2026-11-23); kamai ki pushti baaki |
| 002b | naksha part 2 (rashi movement) | dikhane ka version APPROVED (23 Nov 2026); kamai ki pushti baaki |
| 003 | family pattern (rashi chain) | sikhana jari, pichle 1 saal ki jaanch likhi, aap ki pushti baaki |
| 004 | baar tokri (weekday ke zyada aaye 6 number) | likha, hint (highlight) ki tarah software me, aap ki pushti baaki |
| 007 | **Puzzle-Steps** (3 mahine ek sheet, step 1/2/3, boundary, link-rang, indicator) | APPROVED, live (23 Nov 2026), jaanch: random jaisa |
| 006 | single sheet pattern ke niyam (same duri, rang, flat/standing) | sikhana jari, kuch banaya nahi |
| 005 | dana-farak (4 din box) | likha, aap ki pushti baaki, 6 mahine ki jaanch likhi, software (Pattern Scan) me hai |

HANDOFF.md = niyam aur facts. GLOSSARY.md = shabd (rashi, cross, jodi, half jodi, gap).

App me roz ka batch (dekh liya), sab pattern ka PDF/JPG/Excel aur Edit karo (HANDOFF item 21). App me **Active** tab: jo pattern abhi chal rahe ya pichle 1-3 din me pass hue, sab ek jagah (HANDOFF item 19). Naksha ka pass/fail abhi baaki (item 20, user baad me batayega).

App me pattern ki index (Pattern Scan tab): naam par click karo to wo pattern jitne chal rahe hain sab dikhte hain, har pattern ka README bhi. Details: HANDOFF.md.

## App ka naksha (har hissa kahan hai) - sirf APPROVED/live cheezein (23 Nov 2026)
Niyam: jo push hota hai wo user ne approve kiya hai. Naya sikhna baaki ho to wo push nahi hota.
Neeche ki bar: **Active | Aaj ki List | Pattern Scan | Paper Trading | Aur**. "Aur" me: Dost Khojo, Lab, Monitor, Record, Pattern, Din (Baar), Data, Guide, Number Rank.

| Tab | Kya karta hai | Code |
|---|---|---|
| Active | abhi chal rahe pattern, pichle 1/2/3 din ke PASS, 30 din ka scoreboard, "Abhi scan karo" | tabs_active.js, lab/active.py, /api/active |
| Aaj ki List | dost jodi, Band Rashi/Number, Baar Filter | tabs_core.js, lab/band.py, lab/baar.py |
| Pattern Scan | har pattern (001 Copy, 002 Naksha, 002b Naksha-Rashi, 003 Family, 005 Dana-Farak) ke card, rang wala chart, mahine ki copy, PNG/Excel, README, "dekh liya", sab download PDF/JPG/Excel, Edit karo | tabs_scan.js, lab/scanner.py, lab/scan_view.py, lab/export_all.py |
| Number Rank | aaj ke saare map ke vote: ek map = ek vote, score = kitne map, +1 din ka point; har type me FB/GB/GL/DS aur All location + ALL IN ONE; copy button | tabs_rank.js, lab/rank.py, /api/rank |
| Din (Baar) | har weekday ki tokri (6 number + palat) | tabs_baar.js, lab/baar.py |
| Pattern | rang bharo, save, Excel download; Pattern Scan se "Edit karo" yahin khulta hai | tabs_pattern.js, /api/pattern/* |
| Record | Gap Filter (same gap se bane step, rang), Excel; **Har game ka alag record** (FB/GB/GL 2013 se, DS 1966 se; Excel/CSV) | tabs_guide.js, lab/gapchain.py |
| Paper Trading, Monitor, Lab, Dost, Data, Guide | pehle ke approved hisse | tabs_lab.js, tabs_core.js, tabs_guide.js |

**Scan:** din me 3 baar auto (subah 7:00, shaam 19:00, raat 00:30 IST) + manual button. Roz naya "batch" (dekh liya nishan roz 0 se). Pattern kabhi gayab nahi hote (data/active_log.json).
**Approved naksha version:** git tag `naksha-approved-2026-11-23`. **Abhi live nahi (user sikha raha hai):** current 3 mahine ka Naksha mapping, Naksha ka pass/fail niyam.
Poori detail: HANDOFF.md (items 1-24).
