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

## 3. Muse AI (24 Nov 2026, PDF "sahil_lab_audit_and_ds_report_24nov2026.pdf") - live app khol kar dekha

### Part 1: App audit (19 baatein). Jaanch ke baad:
| # | Daava | Nateeja |
|---|---|---|
| 1 | Paper Trading me pending bet ko loss gin liya | **Galat padha.** `paper.summary()` sirf poori hui bet ginta hai (list10: 30 poori, Net -150 = 30x5; 10 pending alag). Par card ka likha "Bet 30 (baaki 10)" aisa lagta hai jaise 30 me se 10 baaki. **Label sudhar** ("30 poori + 10 baaki") |
| 2 | 24 Nov ko 53 bet duplicate / List se match nahi | **Duplicate nahi.** (date, game, number, strategy) par koi repeat nahi. 3 strategy (list10, list10s, single) alag-alag khate hain, isliye ek hi number kayi me aata hai; "game se pehle" list baad wali List se alag hoti hai. Par label saaf nahi: **label sudhar** |
| 3 | Manual scan ke baad Active batch 0 -> 21 | Dekha nahi, scan ke saath count judna normal; "kya ginta hai" likhna achha rahega |
| 4 | Dost Khojo: 73 is mahine 0 baar, Record me GB 73 on 23 Nov | **SAHI (asli kamzori).** `friends.counts()` aakhri din ko ginta hi nahi (uska agle din ka window poora nahi). Isliye 23 Nov ka 73 nahi gina. Fix: card par likho "aakhri din ginti me nahi" ya aakhri din alag dikhao |
| 5 | Monitor header "koi chetavani nahi" par 30-din table laal | **SAHI (label).** `alerts` sirf pichle 3 mahine dekhta hai (30 din ka sample bahut chhota). Header me likhna: "3 mahine ke hisaab se koi chetavani nahi" |
| 6 | Dost Khojo drift "72 -> 87" aur "Dost Drift: badlaav nahi" | Do alag paimane (periods ka milan vs roz ka drift log). Label alag-alag karna |
| 7 | "Hit hue map (1 din)" 0 par "PASS hue (1 din)" 1 | Alag cheez (map ka number aaya vs pattern poora hua). Label saaf karna |
| 8 | Time zone IST/UTC ka mel nahi | **SAHI.** Active scan IST dikhata hai, Pattern Scan ka "chali" time UTC (naive). Sab IST me dikhana |
| 9-19 | kat-te jumle, Naksha Active me nahi, Puzzle-Steps scoreboard nahi, bade kale khaali hisse, clipping, "1vi jagah", raw JSON dump (Data tab), bina label rang button, chhote sample par bada x4.85 | Zyadatar UI. Naksha/Puzzle-Steps scoreboard me **jaan-boojh kar nahi** (pass/fail rule user sikha raha hai: HANDOFF 20). Date "MM/DD/YYYY" phone ke date picker ki wajah se (app nahi). "Chhote sample par bada multiplier" achha sujhav: kam data par headline na dikhao |

Fix list jo "haan" par karunga (sab chhote, paise ka hisaab nahi badalta): 1,2 label; 4 aakhri din ka note; 5 header; 8 IST; 007 ke "?" aur flat link (Gemini wali baat); 19 kam sample par chetavani.

### Part 2: DS research (1966-2026, 21,431 din, 62 test, Bonferroni 0.0008)
- C5 = DS 2 din + 3 din pehle wale number: 2.83% (2 number, **1.42%/number**), lift 1.42, z 6.83 (1990-2026). **Hamare khate se mel khata hai** (hamara ek number 1.47%).
- Lag-2 1.44%, Lag-3 1.39%, GB->DS 1.57% (2013+), FB+GB+GL->DS 1.36x, hot-10 11.09% (sirf 95x par layak; 90x par -0.19/day): **sab hamari randomness/recency report se mel khate hain.**
- **Ulte (bure) nateeje:** longest-unseen number 0.48% (lift 0.48, z -6.0): "kab se nahi aaya wo ab aayega" DS me ulta hai (band number aadhe chance par); 1-saal ka hot-10 7.5% (regression to mean); lag-1 repeat 0.92%; cold-10 7.54%; Naksha-DS link random se kam (1.59-1.68% vs shuffle 1.82-1.89%), predict 1.52% vs 1.91%; weekday/baar tokri DS par nahi chalti. **Ye hamare recycling-pool findings ko pakka karte hain** (pichle 2-5 result ke number dobara aate hain, purane gayab number kam).
- Aaj ke number (24 Nov): C5 = 59 + 67, hamare khate ka aaj ka number 59 (lag-2) **same**.
- Imaandari: C5 par 1 saal ka expected +Rs 2,515 par SD +-Rs 3,010: 1-2 saal paper edge sabit nahi karega. **Hamare power-analysis se same.**
- Muse AI ki ek hi ulti baat Gemini se: "forward 90 din se faisla" nahi likha, "sirf nigrani" likha - sahi.

### Gemini + Muse milakar
Dono ke DS ke nateeje hamare apne nateejon se **alag-alag raste se mil gaye** (lag-2/3 repeat, GB->DS, hot-10 sirf 95x par). Ye bharosa badhata hai ki ye meri ginti ki galti nahi, par ye ab bhi "purane data par mila signal" hai; kamai ka vaada nahi. App ke bug (label, IST, Dost Khojo last day) Muse AI ne asli pakde, Gemini ne nahi (usne live app dekha hi nahi).

## 4. Gemini "Deep Research Report + RooFlow Blueprint" (Drive doc 1ryGZHx5AMnsP4s_de-1yRdIq-lnZcACT, 24 Nov 2026)
Status: **sirf note. Kuch banaya/push nahi kiya** (user: "abhi kuch mat karo").

**Achha / rakhne layak (user ke go par):**
- Online empirical-Bayes weight with decay (half-life ~460 din) + shrinkage: signal toote to apne aap 0 ke paas. Samajhdari ka vichar, hamare "DS rule" ke saath ek **paper-only side-by-side mode** ban sakta hai.
- Walk-forward leakage test (kal ka result aaj ke weight par asar na kare), year-by-year audit (hamne 2013-26 par kar liya: A pool 12/14 saal plus), 90-din drawdown circuit breaker, Nov-Dec "saal bhar 0 baar aaye number" ka test (naya, jaanch layak: FB/GB/GL ka saalana spread random se ~12-15% kam hai).
- Flat stake, no martingale: sahi.

**Dikkat / kyun abhi nahi:**
1. **Poora rebuild** (Neon Postgres, 4-tab redesign): zaroorat nahi. State pehle se GitHub sync me hai (gh.py FILES), workers 1, timeout 120. Approved cheezein toot sakti hain.
2. **Signal ko exp(sum of weights) se milana** maanta hai ki signal alag-alag aur jodne layak hain. Muse AI ne khud dikhaya ki combos stack nahi hote (C2, C3 random/fail). Isse "Pool lift" aur confidence badha-chadha dikhega.
3. **HIGH_EDGE gate model ke apne andaze (pool lift >= 1.2) par**: ghoomta tark. Asli gate sirf **asli hit-rate (realised) vs random** hona chahiye.
4. Cross-game (GB/FB/GL->DS) hissa 2020+ me kamzor (1.51% -> 1.22%); decay se kuch sambhalta hai par poora nahi.
5. Dahai-bias, hot/cold-10 jaise kamzor signal jod kar zyada shor, 90x par hot-10 -0.2%.
6. 007 ke bug 5-8 wahi jo pehle note kiye; baaki doc ke bug (disk wipe, workers, timeout) pehle jaise **purani/galat baat**.
7. Doc me emoji kharab encode (kuch jagah): sirf dikhawat.

## 5. Teesri report (PDF "Sahil_Lab_Report_24Nov2026.pdf", repo clone karke code padha) - user ne "dekho" kaha
Status: **sirf note, kuch badla nahi.** Is report ke daave maine apne data par dobara chalaye.

**Dobara ginne par mel khaye:**
- DS lag-2 1.554% (333/21429), lag-3 1.433%, lag-4 1.447%, lag-5 1.456%; 1966-2012 1.516%, 2013-26 1.368%, 2022-26 1.468%: hamare nateejo se mel.
- **Naya (B4): DS ka aakhri ank (unit digit) 2 din pehle jaisa.** Maine dobara chalaya: poora 12.71% (2724/21429), 2013-26 11.71%, 2020-26 11.57%; shuffle control (saal-saal shuffle, 100 baar) mean 9.95%, max 10.34% => sanyog nahi. Exact number repeat hata kar bhi 11.33% (random ~9.1% se upar) => ank-level ka asli asar, number repeat ka hi roop nahi. Lag-3 ank 2013-26 10.84%.
- Break-even: ank par 9.5x = 10.53%, **9x = 11.11%** (isliye 9x par margin sirf ~+5%, 9.5x par +11%). Pehle kisi report me ye ank-wala hissa nahi tha.
- Is naye test ko bhi baaki jaisa maano: ye bahut saare digit-tests me se ek hai (multiple testing), purane data par mila. **Paper-only, alag khate me** forward dekhna.

**App ke naye bug (code se):**
1. `lab/picks.py` (list10): DS ke liye apna lag 2-5 signal hai hi nahi (grep: picks.py me "lag" nahi). Aaj ki DS list me 47 aur 76 nahi hai (jo 008 ke aaj ke sabse mazboot number). **Sahi.**
2. DS par "single" bet cross-game (kal ka GB) hai; 2022-26 me ye kamzor (+9%, CI -13..+34).
3. Paper payout: 95x har jagah; asli market 90/9.5 hota hai: ledger ROI thoda zyada dikhta hai.
4. Fetch fail ho to purani tarikh ki list chalti rehti hai (banner nahi).
5. Active log: `first_seen` = pehli scan ka din, isliye "kitne din chala/kab pass hua" ginti galat ban sakti hai.
6. List ke weights usi data par set (monitor ka "list10 +14.6%" poora walk-forward nahi).
7-12. Chhote: bina settle holiday-bet pending rehti hai; /api/paper GET aur /api/monitor GET bina lock file likhte hain; fetch_log ulti tarteeb/duplicate; backtest cache ki chaabi me data badalne par safayi nahi; hits.py ka default "aaj" UTC se.
(Inme se 2-3 pehle wali reports ke saath milte hain; jaanch pending: kaun sa pehle ho sakta hai user tay karega.)

**Report ke sujhav:** pehle bug 1+2 (DS ke liye lag number list me), payout setting (95/90/9.5), haruf paper mode alag, purani list par banner, first_seen sahi, weights walk-forward, forward-test ka niyam likh dena ("90 din = chalu hai ya toota; faisla ~5 saal").
