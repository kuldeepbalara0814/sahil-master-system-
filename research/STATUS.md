# R&D status (23 Nov 2026, shaam; phone ki battery kam hone par roka gaya)
**Resume kaise:** phone charge hone ke baad Claude Code me bolo: "research/STATUS.md padho aur R&D resume karo". Har agent ko BRIEF.md + is file se shuru karna hai; **ek hi heavy python process**, `free -m` dekh ke; nateeje turant file me.

## Ho chuka
- **randomness/ - POORA.** REPORT.md + Excel (`/sdcard/Download/Research_randomness_summary.xlsx`). Nateeja: FB/GB/GL (2013+) random jaise; DS (1966+) me sthayi halka jhukav (41 zyada, 05 kam; walk-forward hot-10 = 11.1% vs random 10%), lag-2/3 repeat ~1.4x; games me same din same number ~1.4% vs 1%; link/copy shuffle se zyada nahi; koi drift/shuffle ka nishan nahi.
- **bugfix (repo me, commit b928b97):** IST tarikh fix, locks, /api/health, input checks. Research/bugfix/REPORT.md baaki.
- **hits / result dalo:** live.

## Baaki (resume karna)
1. **backtest/** - harness bana (scripts/harness.py), light cache poora (cache/, git me nahi). Heavy run chhote sample (~60 block) se dobara; dana-farak ke lift 1.14 (z 6.3) par shuffle control; sweeps (LIFT + multiple-testing), persistence (hit hue map), vote calibration; REPORT. Dekho: backtest/PROGRESS.txt.
2. **singlesheet/** - runner `scripts/run_all2.sh` (part 1-5, 4 game, 100 shuffle); `out/PROGRESS_run.txt` dekho; phir `analyse_all.py`; REPORT.
3. **bugfix agent** - baaki bug-hunt, data ki jaanch (results.csv), jsdom smoke, research/bugfix/REPORT.md.
4. Subagent REPORT.md nahi likh sakta: report **text me** bheje, lead file likhe.

## singlesheet - beech ka nateeja (agent ne roka, 23 Nov shaam)
Resume: `cd research/singlesheet/scripts`; run_all2.sh se `rm -f ../out/p1_DS_month.npz` wali line hatao (nahi to DS month dobara hoga); `nohup ./run_all2.sh >/dev/null 2>&1 &` (jo .npz ban chuki hai use chhod deta hai).
Ho chuka: Part 1 DS month (100 shuffle), FB month (150), FB 30-row (100), GB month (100). Baaki: GL month, DS/GB/GL 30-row, parts 2,3,5 (4 game), part 4, phir analyse_all.py + held-out + report.
Beech ka nateeja (within-year shuffle, DS bias ka credit pattern ko nahi): FB month max z 0.98 (family-wise p 0.83) random; FB 30-row z 2.3 (p 0.26) random; GB month z 1.57 (p 0.53) random; **DS month z 4.34 (p 0.030) borderline**: lift sirf 1.02-1.04; rashi link, L 12-15, >=2 link me dikha. Shak: DS ka lag-2/3 repeat jhukav (shuffle me toot jata hai) - serial asar, design nahi; abhi jaancha nahi, held-out saal aur dashak-wise baaki. Isliye pakka pattern nahi, koi code badlav nahi.
