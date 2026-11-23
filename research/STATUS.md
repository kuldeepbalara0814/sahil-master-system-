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
