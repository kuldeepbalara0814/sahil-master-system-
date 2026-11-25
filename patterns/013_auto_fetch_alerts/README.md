# 013 Auto fetch (result aate hi) + banner khabar + 007 aage badhe  (24 Nov 2026, user ki maang)

User ne kaha: FB ka result 6:30-6:45 pm, GB 10:30 pm, GL 12:15 am, DS subah; har result par auto lo, current month ke 3-mahine wale pattern dekho, naye active ho to **upar banner**; subah 7 baje final: sab pattern naye sire se. 007 ka card result aate hi aage banna chahiye.

## Kya badla
1. **Schedule** (`.github/workflows/daily.yml`, IST): FB ke baad 18:45 (+retry 19:15), GB ke baad 22:45 (+23:15), GL ke baad 00:30 (+01:00), subah 07:00 final (+09:00). Roz 8 baar. GitHub kabhi 10-30 min der karta hai, isliye retry. Render `data/**` par dobara deploy nahi karta, isliye zyada commit se nuksan nahi.
2. **Aadhi line** (`lab/partial.py`, `data/partial_results.json`): site FB/GB/GL aate hi dikha deti hai, DS agli subah. Line `results.csv` me tabhi judti hai jab chaaron aa jayen (record kharab nahi hota). Tab tak aaj ke aa chuke game alag file me, **sirf scan/dikhane ke liye**. Line poori hote hi file bekaar (apne aap hat jati hai).
3. **007 aage badhta hai** (`lab/steps.py`): Step 3 ab aadhi line ke saath banta hai, isliye FB ka result aate hi design aage (cell rang, '?' box bharta hai). Aadhi line me jo game abhi nahi aaya wo khali dikhta hai. Boundary ki aakhri tarikh par bhi DS baaki ho to design khuli maani jati hai (jaldi PASS/FAIL nahi).
4. **Mahina badalna aur boundary aage chale (user ki haan, 24 Nov):** window (Step 1/2/3 = pichle se pichla, pichla, current mahina) apne aap khisakti hai: Nov khatam -> Sep hat, Oct/Nov/Dec. **Step 3 ki boundary mahine ke aakhir par nahi rukti**, agle mahine me chalti hai (jaise 24 Oct se 8 box = 1 Nov tak). Mahina badalne par **purani window ke jo design abhi khule hain wo saath me (4 tak) dikhte rehte hain** jab tak boundary khatam na ho (pata lagta rahe PASS/FAIL). Naye mahine ki pehli line (ya aadhi line) se hi naye card bante hain (pehle 3 line ki shart se 1-2 tarikh 0 card the). Jaanch: 30 Oct ko 8 design Nov tak chalte dikhte; 1 Nov ko 8 naye + 4 purane.
5. **Banner khabar** (`lab/alerts.py`, `data/alerts.json`, `lab_static/alerts.js`): har result par scan ke baad jo pattern pehle active nahi the aur ab hain, unki khabar app ke upar: pattern ka naam, game aur number. Naksha-Rashi ke 44 items sirf ginti me. "Active tab kholo" button, x se hat jati hai. Subah 7:00 par label "final scan". Aaj ke aa chuke game ek line me ("Aaj aa chuke: FB 53").
6. **Meri Window:** "Aaj ke Dost + Baar number" card (sirf dikhane ke liye; Top 30 isse nahi bani, backtest research/dost_top30: 28.6% vs random 30%).

## Dhyan rakho
- Software dikhata hai, faisla aapka. Banner khabar "pattern active hua" batati hai, "jeetega" nahi.
- Hits/paper: aadhi line ka result `hit_log` me bhi jaata hai (src manual jaisa), site ka asli result alag nikle to purana wala hat jata hai.
- Wapas: `git revert <hash>`.

## 25 Nov 2026: raat ko auto fetch kyu nahi hua, aur ilaaj
- **Wajah:** GitHub ka schedule bharose ka nahi. 4 din me sirf 6 run chali; raat 00:30 wali ek bhi nahi; subah 7:00 wali 8:24 par aayi.
- **Ilaaj:** app ki apni ghadi (`lab/tick.py`): FB 18:35, GB 22:35, GL 00:20, DS 05:40 ke baad result baaki ho to server khud site se lata hai (10 min me ek koshish). Chalti hai jab app khuli ho (`/api/status`, `/api/alerts`) ya **`/api/tick`** ko ping mile. GitHub Action ab sirf backup hai.
- **Bahar ki ghadi (ek baar lagani hai):** cron-job.org (free) par job: URL `https://sahil-lab.onrender.com/api/tick`, timezone Asia/Kolkata, crontab `*/10 0,5,6,7,18,19,22,23 * * *`. Is URL me koi PIN/key nahi.
- **Sync suraksha:** GitHub ki file badli ho tabhi local badle; badli file hi push ho; takraav me haath se dali files aap ki, baaki GitHub wali; likhai atomic; update ke waqt pull band; Action takraav par dobara koshish karti hai.
- **Record suraksha:** beech ka din site ne na bhara ho to aage ki line 4 din tak nahi judti.
- **Roz Action me tests nahi:** data ki jaanch (`scripts/selfcheck.py --data`) chalti hai; code ke tests `code-tests` workflow me.

## Khud-jaanch
`python scripts/selfcheck.py --live --tests` -> `selfcheck_report.json` (git me nahi jati). Theek karke `--clean`.

