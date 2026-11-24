# Doosre AI ki reports (user ne site/Drive data dikhaya) aur unki jaanch

Niyam: koi bhi daava tab maana jab apne data par parakha. Jo sahi nikla wo yahan likha; jo galat/purana tha uski wajah bhi.
Sab ginti 24 Nov 2026 ke data (4909 din) par, `data/results.csv`.

## 1. Gemini (24 Nov 2026) - Report 1: app ki kamiyan

| Daava | Jaanch | Nateeja |
|---|---|---|
| Render disk saaf hone par state (active_log, hit_log, manual_results...) ud jayega | `lab/gh.py` FILES me ye sab hain; har save GitHub par jata hai, boot par wahin se aata hai | **Purani/galat baat** (Gemini ne ye hissa nahi dekha) |
| Gunicorn me kai worker se JSON corrupt | `render.yaml`: `--workers 1 --threads 4`, locks `_wlock/_run_lock` | **Pehle se theek** |
| Bulk PDF par timeout | `--timeout 120` pehle se | **Pehle se theek** (bhari export ke liye "Top 10" option ka sujhav achha, abhi nahi kiya) |
| Kuch POST route bina PIN ke | PIN wale: manual result, board save/delete, play, paper, fetch. **Bina PIN**: `/api/active/scan`, `/api/scanner/run`, `/api/review`, `/api/scanner/to_board`, `/api/lab/parse`, `/api/lab/test` | **Aadha sahi.** Link jisko mile wo scan chala/spam kar sakta hai. Sujhav: scan par cooldown (jaise 60 sec) - user ki haan par |
| 007 Puzzle-Steps: flat link ka same-row doosra location check nahi hota (Step 3 `c+i+1` se shuru) | `scripts/puzzle_pattern.py` `analyse()` me search `rr in range(c+i+1, ...)`. Flat link me doosra cell usi row me hota hai | **SAHI (latent bug).** Aaj ke data par 0 PASS chhoota, par aage chhoot sakta hai |
| 007: jo "?" box beet chuki tarikh par ban jata hai wo asli result ke upar likha jata hai | Aaj ke data par 8 pattern me 11 aise "?" (6 flat + 5 non-flat) jo declared row par hain | **SAHI.** Dikhawe ki galti (asli number dab jata hai). Fix: beet chuki tarikh par "?" mat likho (gaya/fail dikhao). **User ki haan ke baad** (007 approved hai, chup-chap nahi badla) |
| Number Rank: bade pool wale pattern (002b ~44 maps) vote hijack karte hain | Sahi hai ki 1 map = 1 vote, pool bada to numbers zyada. User ka tay kiya niyam: "ek map ek vote" | **Soch ka vishay.** Sujhav: pool-wazan (1/numbers) ka vikalp, alag switch. User tay kare |
| Manual result results.csv me merge nahi hota, isliye live same-day signal nahi | By design: manual sirf hit ginne ke liye, line tab banti hai jab FB GB GL teeno aa jayen (DS ke liye) | **Design hai**, bug nahi |
| NOT_STORED=naksha, naksha2, isliye scoreboard me nahi | `lab/active.py:9` | **Sahi**, jaan-boojh kar (inka pass/fail rule user abhi sikha raha hai: HANDOFF 20) |
| 13 tab ka bikhrao, ek "Aaj ka Control Room" | UX raay | Achha vichar; user ka tay karna |
| DS data me MISSING/OFF tarikh se lag khisakta hai | Hamara data audit saaf (4909 din, koi dupe/missing nahi); lag row-wise hai (chhuti wale din row nahi) | **Hamare current data par lagu nahi** (1966-2012 purani file par ho sakta hai, wo alag rakhi hai) |

## 2. Gemini - Report 2: DS signals

- Break-even (95x: 1.053%, 90x: 1.111% per number) **sahi**. Lag-2 1.55% / 1.47%, GB->DS 1.57%, FB->DS 1.37%, GL->DS 1.14%, hot-10 11.09%, doubles/cold-10 kam: **hamari randomness report se uthaye, sahi**.
- Naya jaanch (maine kiya, 24 Nov): "Tarika A" pool = aaj ka GB+FB+GL + DS 2 aur 3 row pehle (set, duplicate ek ginte):

| Pool | Poora 2013-26 | 2013-19 | 2020-26 |
|---|---|---|---|
| A (Gemini 5-number) | 1.40%/number, ROI@95x +32% | 1.51%, +43% | 1.28%, +22% |
| sirf DS lag2+lag3 | 1.40%, +33% | 1.47%, +39% | 1.34%, +27% |
| sirf cross-game GB+FB+GL | 1.37%, +30% | 1.51%, +43% | **1.22%, +16%** |

  Saal-dar-saal ROI (A): 2013 +50, 14 +21, 15 +44, 16 +70, 17 +38, 18 +36, 19 +42, **20 -7**, 21 +54, 22 +21, 23 +32, **24 -12**, 25 +26, 26 +41 (14 me se 12 saal plus).
- Matlab: A poora sample me plus hai par **cross-game hissa ghat raha hai** (1.51% -> 1.22%), DS-apna lag hissa zyada tika hai (1.47 -> 1.34). Hamari recency report ka "cross-game fading" wahi baat. Isliye hamare paper khate me sirf DS-apna lag rakha.
- **Sab in-sample** (jis data par signal mila usi par ROI). 95x par commission/kati nahi. Asli test sirf aage ka forward hai.
- Gemini ka "60-90 din forward test se faisla" **galat**: itne din me hit-count itna kam hota hai ki 1.4% aur 1.0% me fark nahi pata chalta (power ~10%). Faisle ke liye ~5 saal. 90 din sirf "kaam kar raha hai ya toota" ki jaanch hai.
- Gemini ke FB/GB/GL ke samay (6:15 PM, 10 PM...) data se nahi liye gaye; hamari line: DS = us line ki agli subah ka. Sab teen game DS se pehle aate hain, isliye same-line cross-game signal usable hai (par fading ke saath).
- "Martingale kabhi nahi", "flat stake" - **sahi** (hamara loss-cover test bhi yahi dikhata hai).
- Sujhav (user ki haan par): paper khate me teesra mode "A pool" jodna **sirf side-by-side tulna** ke liye, DS-apna 4-number mode ke saath. Tulna ek jaisi shart par hogi.

## 3. Muse AI - report aane par yahan judegi
(pending: user copy-paste karega)
