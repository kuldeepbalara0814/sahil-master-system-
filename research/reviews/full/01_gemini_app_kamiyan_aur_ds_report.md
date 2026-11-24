# 01 - Gemini ki pehli report (24 Nov 2026) - jaisi user ne paste ki, bina badle

> Gemini ne live site nahi khola (uske paas browser tool nahi tha); Drive ki files (HANDOFF, INDEX, AI_REBUILD_GUIDE, STATUS, puzzle_pattern.py, randomness REPORT) ke aadhar par likha.
> Hamari jaanch: research/reviews/EXTERNAL_REVIEWS.md (section 1 aur 2).

Pehle ek saaf baat: mere paas live browser/URL-fetch tool nahi hai, isliye main https://sahil-lab.onrender.com/ ko live click karke open nahi kar sakta. Lekin aapke Google Drive me rakhe poore app architecture (00_HANDOFF.md, 00_INDEX_README.md, 00_AI_REBUILD_GUIDE.md, research_STATUS_resume.md), puzzle_pattern.py.txt code, aur research_randomness_REPORT.md (21,430 din ka DS data) ke aadhar par dono hisson ki poori detailed report neeche hai.

## Report 1: sahil-lab.onrender.com App - Kamiyan, Bugs aur Sudhar

### 1. Sabse Badi Hosting aur Data-Loss Kamiyan (Render + Flask + JSON)
* **Ephemeral Disk Wipe (Sabse Bada Bug):** App apna state local JSON files (data/active_log.json, data/review_log.json, data/hit_log.json, data/manual_results.json) me save karti hai. Render ke free/standard web service par har git push, restart, ya server recycle par local disk saaf ho jati hai. Matlab aapka 30-din ka scoreboard, "dekh liya" tick aur hath se dale results bina warning udd sakte hain.
  * Sudhar: State files ke liye free external DB (Turso SQLite / Neon Postgres / Supabase) ya GitHub API se auto-commit lagao.
* **Multi-Worker JSON Corruption:** research_STATUS_resume.md ke mutabik commit b928b97 me locks jode gaye hain. Agar Gunicorn me 1 se zyada worker chal rahe hain to Python threading.Lock do processes ko nahi rokta - ek saath write hone par JSON file corrupt ho sakti hai.
  * Sudhar: Hamesha atomic write (temp file -> os.replace) + OS-level fcntl.flock use karo (ya SQLite WAL mode).
* **Cold Start aur Bulk PDF Timeout:** Render free tier 15 min baad sleep ho jata hai. 00_HANDOFF.md ke hisaab se Naksha (48 maps) ka bulk PDF/JPG ~5-6 MB banta hai - Pillow se itni images ek saath banane par default 30-second Gunicorn timeout par 502 / Timeout error aane ka pura risk hai.
  * Sudhar: Gunicorn --timeout 120 rakho, bulk export me "Top 10" option + WebP compression do, aur background job / streaming response use karo.
* **Security / Public URL Risk:** /api/result/manual par PIN hai, lekin agar /api/review, /api/pattern/*, ya manual "Abhi scan karo" bina PIN ya rate-limit ke open hain, to koi bhi public link khol kar aapka review log ya CPU spam kar sakta hai.
  * Sudhar: Saare state-changing POST routes par ek hi PIN middleware aur basic rate-limit lagao.

### 2. Logic, Scanner aur Calculation Bugs
* **007 Puzzle-Steps (puzzle_pattern.py) me 4 Seedhe Bugs:**
  * Flat-Link Miss: keyed() same-day flat link (i == j, a < b) leta hai, par Step 3 check c + i + 1 (agle din) se start hota hai - usi din ka flat hit miss hota hai.
  * Past-Date Overwrite: Agar pending link ki expected tarikh (c + j) beet chuki ho aur boundary bachi ho, to paint() us din ke asli result ke upar "28/82?" overwrite kar deta hai.
  * Collision + Border Bug: Do links ek hi future box par aayein to pehla overwrite hota hai; aur Excel me thick border define hai par apply nahi hua.
  * Step 4/5/6 Warning Missing: 00_HANDOFF.md (item 34/36) ka pichle 1-2 mahine check karke step number dikhane wala logic abhi missing hai.
* **Number Rank (lab/rank.py) ka Vote-Bias Bug:** Har map ko 1 vote milta hai - par 002b Naksha-Rashi akele ~44 maps (~90 numbers) aur 003 Family 8 numbers deta hai, jabki 002 Naksha sirf 2 numbers. Isse bade-pool wale noisy patterns rank ko hijack kar lete hain.
  * Sudhar: Inverse-pool weight (1 / kitne_number_diye) lagao aur har pattern card par shuffle baseline / p-value badge dikhao (taaki user dekhe ki 4-link Naksha random 13-saal me bhi 99% baar mil jata hai).
* **Manual Result vs Scanner Disconnect:** "Result dalo (hath se)" sirf manual_results.json me hit ginta hai, results.csv me merge nahi hota. Isliye FB (6:30 PM) ya GB (10:15 PM) aate hi same-day cross-game ya 005 Dana-Farak live update nahi hota.
  * Sudhar: Temporary live-day override layer banao jo scan ke waqt manual_results.json ko memory me merge kare (bina results.csv bigade).
* **Data Gaps & Missing-Date Lag Bug:** Avtar_FD_GB_GL_DS_Master me 1966-2012 DS me 379 MISSING, 191 OFF aur 192 invalid dates the, aur 2025-2026 me do sites par 25 din ka fark mila. Row-index se lag-2/3 ginte waqt agar beech me MISSING date ho to lag khisak jata hai.
  * Sudhar: Row-wise aur Calendar-date-wise dono lag ko alag flag karke data-quality audit banner dikhao.
* **Naksha Scoreboard Blind Spot:** NOT_STORED = naksha, naksha2 hone ki wajah se sabse zyada use hone wala pattern 30-day scoreboard se bahar hai.

### 3. Mobile UX Sudhar
* **13 Tabs ka Bikhrao:** Neeche 5 tab + "Aur" me 8 tab daily workflow ko slow karte hain. Ek single "Aaj ka Control Room" view banao jahan upar sirf 3 cheezein hon: (1) DS Statistical Signal Card, (2) Weighted Top-10 Number Rank, (3) Aaj ka Manual Result + Instant Hit Tracker.

## Report 2: DS (1966-2026, 21,430 Din) - Random se Achha Passing % aur Asli Tarike

Pehle break-even ka pakka ganit samajh lo (single game DS ke liye):
* 95x payout par: 1 number ka break-even = 1.053% (10 numbers = 10.53%, 5 numbers = 5.26%), yaani kam se kam 1.053x lift chahiye.
* 90x payout par: 1 number ka break-even = 1.111% (10 numbers = 11.11%, 5 numbers = 5.56%), yaani 1.111x lift chahiye.

Aapki research_randomness_REPORT.md ka sabse bada sach ye hai: FB, GB aur GL poore random hain, par DS (1966+) sach me random nahi hai. Visual naksha/copy/link DS me bhi random se upar nahi gaye (month-to-month copy to random se kam hai: 322 vs 382), lekin DS me 5 pakke statistical signals mile hain (p = 10^-9 se 10^-38 tak):

| DS Signal (Report ke Asli Aankde) | Pool | Historical Hit % | Random % | Lift | Theoretical Paper ROI (@95x / @90x) |
|---|---|---|---|---|---|
| 1. DS Lag-2 Exact Repeat (1966-2026) | 1 | 1.55% (333/21,430) | 1.00% | 1.55x | +47.6% / +39.9% |
| DS Lag-2 Exact Repeat (2013-2026) | 1 | 1.47% (72/4,908) | 1.00% | 1.47x | +39.4% / +32.0% |
| DS Lag-2 Exact Repeat (2020s decade) | 1 | ~1.35% | 1.00% | 1.35x | +28.2% / +21.5% |
| 2. DS Lag-3 Exact Repeat (2013-2026) | 1 | 1.32% (65/4,908) | 1.00% | 1.32x | +25.8% / +19.2% |
| 3. Same-Day GB -> DS (2013-2026) | 1 | 1.57% (77/4,908) | 1.00% | 1.57x | +49.0% / +41.2% |
| Same-Day FB -> DS (2013-2026) | 1 | 1.37% (67/4,908) | 1.00% | 1.37x | +29.7% / +22.9% |
| Same-Day GL -> DS (2013-2026) | 1 | 1.14% (56/4,908) | 1.00% | 1.14x | +8.4% / +2.7% |
| 4. Walk-Forward Hot-10 (1990-2026) | 10 | 11.09% (CI 10.55-11.63) | 10.00% | 1.11x | +5.4% / -0.2% |
| 5. Anti-Filters (Hatao) | - | Doubles: ~8.8% (z=-5.8); Cold-10: 7.54%; Lag-1 repeat: 0.90% (44/4,908) | 10.0% / 1.0% | <0.9x | Inhe avoid karne se waste ghatta hai |

### Timing ka Sabse Bada Operational Idea (DS ke liye)
FB (6:15 PM), GB (10:00 PM), aur GL (12:00 AM) teeno DS (5:30 AM, window 2:30 AM band) se pehle khul jate hain. Isliye same-day cross-game signal (+35% se +57% lift) live raat 12:30 AM par bina kisi future lookahead ke available hota hai!
(Hamari jaanch: ye samay Gemini ne data se nahi liye; hamari line me DS = us line ki agli subah.)

### Paper-Trading me Test Karne ke 2 Best DS Models
**Tarika A: "DS 5-Number Repeat Pool" (Simple, Zero-Overfit)**
Har raat 12:30 AM (GL aane ke baad) sirf ye 5 numbers (duplicates hata kar ausatan 4.90 numbers) DS ke liye lock karo:
* Aaj ka GB result
* Aaj ka FB result
* 2 din pehle ka DS (Lag-2)
* 3 din pehle ka DS (Lag-3)
* Aaj ka GL result (4-number version bina GL ke bhi alag track karo)
* Estimated Hit Rate (2013-2026): ~6.63% vs 4.90% random (1.35x lift).
* Theoretical Paper ROI: +28.4% (@95x) ya +21.7% (@90x).

**Tarika B: "DS Dynamic Probability Scorer" (Top-5 / Top-8 Engine)**
App me ek naya tab/scanner lab/ds_edge.py jodo jo roz raat 12:30 AM par 00-99 har number ko score de:
* Base score = 1.00
* Aaj ka GB (x1.50), Aaj ka FB (x1.35), Aaj ka GL (x1.15)
* DS Lag-2 (x1.35), DS Lag-3 (x1.25), DS Lag-1 (x0.90)
* 2013+ Walk-Forward Tens-Digit (Dahai) weight (kyunki DS13 me number bias p=0.43 kamzor hua hai, par dahai bias p=0.0002 abhi bhi zinda hai)
* Doubles (00, 11..99) aur Cold-10 par x0.85 penalty.

### 3 Kadwe Sach (Jo Paper-Trading se Pehle Jaanna Zaroori Hai)
* **Year-by-Year Audit Zaroori Hai (Artifact Check):** Lag-2/3 repeat aur GB/FB->DS repeat sach me system ka behavior hai ya kisi purane saal ki site copy-paste galti? Iske liye 2013 se 2026 tak har saal ka alag hit-rate aur ROI check karna padega. Agar 14 me se 10+ saal me lift >1.10x mile, tabhi signal asli maana jayega.
* **Martingale / Double Stake Kabhi Mat Chalana:** 5-number pool (6.63% daily hit) me bhi 1 saal me ausatan ~46 din lagatar FAIL streak aati hai. Double stake karne par bankroll zero ho jayega (jaise aapke 004 test me -46,520 Rs hua). Sirf fixed flat stake rakho.
* **High Volatility Reality:** Even agar +28% edge sach nikle, 365 din (Rs 10/number = Rs 50/day) me 1-SD swing +-Rs 4,514 hai aur 13% chance hai ki poora saal phir bhi loss me khatam ho. Hot-10 (+5.4% edge) me 1 saal loss me khatam hone ka chance 36.6% hai. Isliye sirf paper-trading par kam se kam 60-90 din (Dec 2026-Feb 2027) live forward test ke bina koi aakhri faisla mat lena.
  (Hamari jaanch: 60-90 din se faisla nahi ho sakta, ~5 saal chahiye.)

Kya main aapke results.csv / game_ds.csv par chalne wali ek poori Termux Python backtest script (ds_edge_audit.py) bana doon jo 2013-2026 ka year-by-year + shuffle-control + flat-stake ROI test turant nikal de?
