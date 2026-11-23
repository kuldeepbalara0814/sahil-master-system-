# Randomness R&D: kya FB/GB/GL (2013+) aur DS (1966+) ke result sach me random hain?
(Agent rnd-randomness-2 ka kaam; report lead ne likhi. Asli aankde: `out/*.csv`; agar koi table ka ank CSV se alag ho to **CSV sahi**.)

Data: data/game_*.csv. FB/GB/GL = 4908 din (2013-01-01 se 2026-11-22), DS = 21,430 din (1966+). DS13 = DS ka sirf 2013+ hissa. Sab p-value numpy se (chi2, permutation/shuffle/circular-shift Monte Carlo 200-5000, BH). scipy nahi.

## Saar (10 line)
1. FB, GB, GL (2013+) lagbhag poore random: koi number/digit/class/rashi bias nahi (p 0.5-0.99), na periodicity, na compression, na seeded-generator (LCG/lagged-Fibonacci) ka nishan.
2. DS (1966+) random nahi, par chhupa design bhi nahi: ek sthayi bias (41 sabse zyada 271 baar vs 214 expected; 05 sabse kam 140), jo 60 saal me badla nahi. 2013+ DS me number-wise bias nahi (p 0.43), sirf tens-digit me halka (p 0.0002).
3. DS walk-forward (1990-2026, 13,019 din): hot-10 hit 11.09% (CI 10.55-11.63, random 10%), cold-10 7.54%. Asli par chhota edge. DS ka bias FB/GB/GL par nahi chalta.
4. Teeno 2013+ games me saal ke andar counts random se thode zyada barabar: chi2 84-93 vs 99 (z -3.5, -4.2, -1.6), variance ~12-15% kam. Halka gair-random saboot, design nahi.
5. DS serial dependence saaf: lag-1 r = -0.066 (p 1e-22); lag 2/3 par repeat ~1.5x (333 vs 217), har dashak me, ab ~1.3-1.4x.
6. Games aapas me alag nahi: same din same number 6 jodiyo me 417 vs 295 (+41%, z 7.1, BH ke baad bhi). Absolute 1.0% se 1.4%. 3-way match sirf 1 (random ~0.5).
7. Same-distance link/copy shuffle se zyada nahi, thoda kam (FB month-to-month same-class 46 vs 83.7). 150 jaanch me 19 p<0.05 (~7.5 expected), BH ke baad 0.
8. Calendar (weekday, tarikh, mahina, chhuti ke baad): 130 jaanch me 15 p<0.05 (~6.5 expected), BH ke baad 0.
9. Drift/change-point: koi nahi (permutation p 0.12-0.99); DS ka bias dashako me sthir.
10. Bharosa: FB/GB/GL "random jaisa" uchch, par sirf bade asar (> ~+40% ek number par) ke liye; DS bias/serial/cross-game asar statistically pakke par design/pattern hone ka saboot nahi.

## 1. Frequency/bias (poora data, chi2 p)
| Game | number(100) | tens | unit | class(55) | rashi(15) | tens x unit indep | Matlab |
|---|---|---|---|---|---|---|---|
| FB | 0.92 | 0.91 | 0.80 | 0.95 | 0.90 | 0.79 | random |
| GB | 0.50 | 0.007 | 0.09 | 0.72 | 0.85 | 0.94 | tens halka (BH se pakka nahi) |
| GL | 0.98 | 0.54 | 0.82 | 0.99 | 0.91 | 0.96 | random |
| DS 1966+ | 7e-38 | 1e-21 | 1e-13 | 2e-32 | 4e-24 | 2e-13 | bias pakka |
| DS13 | 0.43 | 0.0002 | 0.27 | - | - | - | tens halka |
- Aadha-aadha split (1996-07-22) frequency correlation r=0.81, permutation p 0.0002. DS doubles kam (z -5.8, p 6e-9).
- Walk-forward: DS 1966-2012 se seekha bias FB/GB/GL par: hot-10 10.5%, 10.1%, 10.2% (random ke andar).

## 2. Band/gaps/repeats (obs vs expected)
| Game | lag1 | lag2 | lag3 | mean band vs shuffle | longest unseen vs shuffle |
|---|---|---|---|---|---|
| FB | 55 vs 48.9 (p .38) | 61 (p .08) | 77 vs 48.9 (p 5e-5) | 97.90 vs 97.96 (p .75) | 1181 vs 871 (p .05) |
| GB | 52 vs 49.1 (.67) | 65 (.02) | 46 (.66) | 97.99 vs 97.95 | 1046 vs 889 (.24) |
| GL | 47 vs 48.8 (.79) | 57 (.24) | 53 (.54) | 97.91 vs 97.95 | 1450 vs 891 (.003) |
| DS | 222 vs 217 (.75) | 333 vs 217 (3e-15) | 307 vs 217 (1e-9) | 99.31 vs 99.52 (.003) | 1505 vs 1162 (.12) |
| DS13 | 44 vs 49 | 72 vs 49 (.001) | 65 vs 49 (.02) | - | - |
DS lag-2 ratio by decade (obs/exp): 1960s 2.17, 70s 1.77, 80s 1.38, 90s 1.27, 2000s 1.49, 2010s 1.47, 2020s 1.35 (lag 3: 1.90, 1.55, 1.16, 1.44, 1.33, 1.39, 1.23).

## 3. Serial structure
- Autocorrelation lags 1..60: FB/GB/GL lag-1 r lagbhag -0.02 (band ke andar), Bonferroni ke baad koi nahi. **DS** lag-1 r -0.066 (Ljung-Box p 4e-22), r^2 = 0.4%.
- Runs test: DS saaf (above/below median z 6.6); FB/GB/GL me ek-do halke (BH se pakke nahi).
- **Cross-game (same din same number, circular-shift null):** FB-GB 68 vs 49.2, FB-GL 78, GB-GL 71, GB-DS13 77, FB-DS13 67, GL-DS13 56; kul 417 vs 295 (z 7.1). Har saal aur har source me barabar (data galti nahi lagti). 3-way same din: 1,1,1,0 (random 0.49 each). Naye data par confirm karna.
- Calendar 130 jaanch: 15 p<0.05 (exp 6.5), BH 0.

## 4. Same-distance link / copy vs within-year shuffle (200)
| Game | link pair obs | shuffle mean | z | p |
|---|---|---|---|---|
| FB | 723 | 707.7 | 0.41 | 0.63 |
| GB | 665 | 704.5 | -1.10 | 0.28 |
| GL | 742 | 736.0 | 0.16 | 0.86 |
| DS | 3431 | 3328.7 | 1.25 | 0.23 |
| DS13 | 739 | 743.8 | -0.14 | 0.92 |
- Mahine-se-mahine same tarikh same class: FB 46 vs 83.7 (z -4.3), GB 60 vs 83.8, GL 69 vs 85.2, DS 322 vs 382 (z -3.2). **Copy random se kam, zyada nahi.**
- Steps-type (3 mahine, L=8/10/12): poora step design (>=2 saanjhe link) = 0 FB/DS13; DS L=12 common links 570 vs 474.9 (z 1.6, p .06).

## 5. Drift / change-point
- Saal-wise (DS dashak-wise) homogeneity chi2 sab df se neeche => random se zyada ek jaise (drift ki ulti baat). CUSUM change-point (200 perm) 20 series: p 0.12-0.99.
- Under-dispersion (3000 iid sims): FB/GB/GL saal-wise chi2 85.6, 83.6, 93.0 vs 99 (z -3.5, -4.2, -1.6): counts chance se thode zyada barabar. DS13 quarterly chi2 105 vs 99 (z 3.2).

## 6. Shuffle / generator signatures
| Test | FB | GB | GL | DS | DS13 |
|---|---|---|---|---|---|
| repeat within W=5 obs/shuffle | 1.26 (p .005) | 1.10 | 1.09 | 1.37 (.005) | 1.27 (.005) |
| W=100 | 0.96 | 0.95 | 0.99 | 1.02 | 1.02 |
| fresh 100-deck blocks all-distinct | 0 | 0 | 0 | 0 | 0 |
| FFT periodicity p | 0.65 | 0.72 | 0.27 | 0.35 | 0.38 |
| birthday-spacing p | 0.43 | 0.37 | 0.25 | 0.09 | 0.64 |
| compression ratio (zlib) | .9994 | .9998 | .9991 | .9997 | .9989 |
| LCG best fit (random mean) | 77 (77.3) | 76 (77.6) | 83 (78.3) | 273 (282) | 74 (77.6) |
| lagged-Fibonacci BH rejects | 0 | 1 | 0 | 8 | 0 |
- Sampling-without-replacement / taash-shuffle ka nishan nahi; chhoti window (W=5-20) me repeat zyada, W=100 me kam. Seeded PRNG ka nishan nahi. DS ke 8 rejects DS ke bias/serial asar se, generator se nahi.

## Power (80% power, 5% alpha)
| Cheez | n=4908 | DS n=21,430 |
|---|---|---|
| ek number ki sambhavna 1% se | 1.40% | 1.20% |
| 100 me se koi ek (Bonferroni) | 1.66% | 1.29% |
| lag-1 correlation r | 0.040 | 0.019 |
"Random jaisa" ka matlab "bada asar nahi", "zero asar" nahi.

## Kya iska matlab (aasaan Hinglish)
FB, GB aur GL ke 2013 ke baad ke result sach me random jaise hain. Koi number zyada nahi aata, koi chhupa gap-pattern nahi, taash-shuffle ka nishan nahi, na computer-seed wale formula ka. Jo design ya copy chart me dikhti hai wo random me bhi utni hi baar banti hai; mahine-se-mahine copy to random se thodi kam hi hai. Do halki baatein mili: ek saal me kisi number ka bahut zyada baar aana random se thoda kam hota hai (spread 12-15% kam), aur games me same din same number 1.0% ki jagah 1.4% baar aata hai. Ye asar itne chhote hain ki inse koi number ya design pakad kar nafa banana mushkil hai.
DS (1966+) alag hai. Kuch numbers (jaise 41) hamesha thode zyada aur kuch (jaise 05) thode kam aate hain, 60 saal me ye nahi badla. 1990 ke baad har saal pehle ka data dekh kar 10 sabse zyada aane wale numbers chunne par hit-rate 11.1% mila (random 10%): chhota edge. Aaj ke FB/GB/GL par ye bias nahi chalta. DS me 2-3 din ke fark par repeat bhi 1.3-1.5 guna thoda zyada hai, par ye bhi 1% se 1.4% hi.
Pattern ke liye saaf baat: jahan random hai wahan koi pattern, link ya design aage ka result pakka nahi bata sakta. Agar koi pattern chalta dikhe to ya wo bahut saare tests me se ek chamak hai, ya DS ke bias jaisa chhota asli asar. DS ka bias paper-trading me payout ke hisaab se walk-forward parakhna chahiye (backtest agent ka kaam).

## Sudhar / aage ka kaam
- App ke link/copy hisse me within-year shuffle baseline + p-value dikhao (lab/scanner.py, lab/steps.py) taaki user dekhe copy random me kitna aata hai.
- DS bias map (41 hot, 05 cold, doubles kam) walk-forward me payout ke saath parakho.
- Cross-game same-din asar (+41%) Dec 2026 ke baad ke naye data par dobara confirm karo.
- Limitations: DS me mahine ka aakhri din chhuti, isliye lag row-wise hai; 200-shuffle tests me min p = 0.005.
