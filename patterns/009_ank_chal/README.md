# 009 Ank-Chal  [naya, 24 Nov 2026 - pushti baaki, SIRF paper/research, software sirf dikhata hai, faisla insaan ka]

Kuldeep ke kehne par: "jaise pattern banate hain waise hi, par apne deemak se behtar".
Deep analysis (21,431 DS draw + 4,909 line, 2,040 test, BH + holdout) ke baad jo ek naya asar
aage ke data par bhi tika, wahi ye hai.

## Niyam (ek line me)

**2 draw pehle wale number ka ank (andar ya bahar) aaj usi game me usi jagah aaye = PASS.**

- Andar = dahai ka ank (41 me 4), Bahar = ikayi ka ank (41 me 1).
- Andar/andar aur bahar/bahar alag line hain. Cross (andar se bahar) NAHI - wo random se neeche nikla.
- Har line ka apna hisaab; paper me sirf un line par dekho jahan 13 saal ka rate 10.53% (9.5x ka break-even) se upar ho.

## Kaun si line khelein (2013-2026, 4,907 din)

| Line | Hit | Rate | ROI @9.5x | z | Faisla |
|---|---|---|---|---|---|
| DS andar | 604/4,907 | 12.31% | +16.9% | +5.4 | chuni line |
| DS bahar | 575/4,907 | 11.72% | +11.3% | +4.0 | chuni line |
| FB andar (FD) | 580/4,907 | 11.82% | +12.3% | +4.3 | chuni line |
| GB bahar | 559/4,907 | 11.39% | +8.2% | +3.3 | halka |
| GB andar / GL andar | 537/4,907 | 10.94% | +4.0% | +2.2 | halka |
| GL bahar | 509/4,907 | 10.37% | -1.5% | +0.9 | nahi chuni |
| FB bahar | 498/4,907 | 10.15% | -3.6% | +0.4 | nahi chuni |

Chuni hui 3 line (DS andar, DS bahar, FB andar): **1,759/14,721 = 11.95%, ROI +13.5%**.
Discovery 2013-19: 12.13% | holdout 2020-26: **11.76% (z +5.0)** - yaani aage ke data par bhi tika.
Saal-dar-saal DS andar: 14 me se 10 saal break-even se upar.

## Risk (isse pehle padho)

- 3 ank/din. Jeet wale din 31.6% (mahine me ~9 din), DS 4-number rule me 5.4% (mahine me ~1.6 din).
- 90 din: 270 bet, ~32 hit. Profit ka chance 76%, 5% kharab case -42 unit, median +34 unit.
- Pichhle 90 din (Jun-Nov 2026) sirf 24/270 = 8.9% raha - break-even se neeche. Ye normal jhoola hai, par
  iska matlab bhi hai: 90 din me kuch bhi sabit nahi hota. Faisla 6-12 mahine ke paper par.
- 9.5x par haruf ki katauti/limit jodi se zyada hoti hai. Asli +13% aasani se 0 ho sakta hai.
- 2020 ke baad rate dheere gir raha hai (DS andar 13.9% (2018) se 10.7% (2026)). Isliye monitor zaroori hai.

## Code

`lab/ank_chal.py` - `stats()`, `scan()`, `scoreboard()`, `next_ank()`. Sab kuch sirf paas ka data dekhta hai.
Chalane ke liye: `LAB_DATA_FILE=data/results.csv python3 -m lab.ank_chal`


## App me kaise juda hai (24 Nov 2026, review ke baad)
- `lab/scanner.py` me pattern 009 (key `ank`), Pattern Scan me dikhta hai. README yahi file.
- Item me `ank_targets` hai, `targets` nahi: `targets` poore number (00-99) ke liye hai aur hit-log / Number Rank use karte hain; ank (0-9) wahan galat ginta.
- Active window ke 30-din scoreboard me nahi (`active.NOT_STORED`): iska apna record `scoreboard()` (pichhle 90 din) aur `forward()` (24 Nov 2026 se asli aage ka record) se aata hai.
- 24 Nov 2026 se pehle ka sab chuni hui line par **in-sample** hai (line discovery 2013-19 me chuni, holdout 2020-26). Asli sabut sirf forward record.
- Payout 9.5x maana gaya; 9x par break-even 11.11% hai, margin bahut kam (3 line ~+7.6%). Katauti/limit jodi se zyada hoti hai.
- **Ye ank-level asar hai (24 Nov 2026 ki sudhaar):** DS ka dahai ank 12.16% aur ikai ank 12.71% baar 2 draw pehle jaisa aata hai (random 10%). Dono aapas me **alag-alag (independent)** hain: dono ek saath 1.554% aate hain = 12.16% x 12.71% = 1.545% (z +0.1). Yaani **number ka lag-2 repeat (1.55%) isi ka jod (product) hai**, ulta nahi. (Pehle yahan galat likha tha ki ank number-repeat ka roop hai aur andar/bahar ek hi number se saath hit hote hain.) FB andar alag game ki alag line hai (DS ke saath bhi independent: 1.47% vs 1.45%). Isse ye banta hai ki DS me har ank-position par apna repeat-jhukav hai.
- Source: teesri report ki zip (research/reviews/full/06_...zip). Hamari jaanch: research/reviews/EXTERNAL_REVIEWS.md sec 6.
