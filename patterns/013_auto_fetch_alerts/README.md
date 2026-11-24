# 013 Auto fetch (result aate hi) + banner khabar + 007 aage badhe  (24 Nov 2026, user ki maang)

User ne kaha: FB ka result 6:30-6:45 pm, GB 10:30 pm, GL 12:15 am, DS subah; har result par auto lo, current month ke 3-mahine wale pattern dekho, naye active ho to **upar banner**; subah 7 baje final: sab pattern naye sire se. 007 ka card result aate hi aage banna chahiye.

## Kya badla
1. **Schedule** (`.github/workflows/daily.yml`, IST): FB ke baad 18:45 (+retry 19:15), GB ke baad 22:45 (+23:15), GL ke baad 00:30 (+01:00), subah 07:00 final (+09:00). Roz 8 baar. GitHub kabhi 10-30 min der karta hai, isliye retry. Render `data/**` par dobara deploy nahi karta, isliye zyada commit se nuksan nahi.
2. **Aadhi line** (`lab/partial.py`, `data/partial_results.json`): site FB/GB/GL aate hi dikha deti hai, DS agli subah. Line `results.csv` me tabhi judti hai jab chaaron aa jayen (record kharab nahi hota). Tab tak aaj ke aa chuke game alag file me, **sirf scan/dikhane ke liye**. Line poori hote hi file bekaar (apne aap hat jati hai).
3. **007 aage badhta hai** (`lab/steps.py`): Step 3 ab aadhi line ke saath banta hai, isliye FB ka result aate hi design aage (cell rang, '?' box bharta hai). Aadhi line me jo game abhi nahi aaya wo khali dikhta hai. Boundary ki aakhri tarikh par bhi DS baaki ho to design khuli maani jati hai (jaldi PASS/FAIL nahi).
4. **Mahina badalna:** window (Step 1/2/3 = pichle se pichla, pichla, current mahina) apne aap khisakti hai: Nov khatam -> Sep hat, Oct/Nov/Dec. Pehle naye mahine ki pehli 2 line tak 0 card aate the (3 line ki shart); ab 1 line (ya aadhi line) se hi card bante hain. Jaanch: 1-3 Nov par 8 live card.
5. **Banner khabar** (`lab/alerts.py`, `data/alerts.json`, `lab_static/alerts.js`): har result par scan ke baad jo pattern pehle active nahi the aur ab hain, unki khabar app ke upar: pattern ka naam, game aur number. Naksha-Rashi ke 44 items sirf ginti me. "Active tab kholo" button, x se hat jati hai. Subah 7:00 par label "final scan". Aaj ke aa chuke game ek line me ("Aaj aa chuke: FB 53").
6. **Meri Window:** "Aaj ke Dost + Baar number" card (sirf dikhane ke liye; Top 30 isse nahi bani, backtest research/dost_top30: 28.6% vs random 30%).

## Dhyan rakho
- Software dikhata hai, faisla aapka. Banner khabar "pattern active hua" batati hai, "jeetega" nahi.
- Hits/paper: aadhi line ka result `hit_log` me bhi jaata hai (src manual jaisa), site ka asli result alag nikle to purana wala hat jata hai.
- Wapas: `git revert <hash>`.
