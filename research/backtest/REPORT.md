# Backtest R&D: app ke pattern 13 saal (2014-26) walk-forward, asli vs random
(Agent rnd-backtest-4 ka kaam; report lead ne likhi. Asli aankde: `out/` (tables_light.md, variants_*.csv, max_test_*.csv); koi ank alag ho to **out/ sahi**. Heavy sample = 237 din (~5%), 1 asli + 3 shuffle run.)

## Saar (10 line)
1. **Dana-farak** (2 number + palat) ka lift 1.139 (n=15045, CI 1.095-1.182, z 6.3): poori table me akela bada ank.
2. Is lift ka lagbhag **70% "haal me aaye number ka dohrana"** hai: control (2 haal ke box number + palat) ka lift 1.099 (z 8).
3. Control ke upar farak ka bachha fayda sirf **1.036** (z 2.5, 100-record block bootstrap). Within-year shuffle me lift sirf 1.005-1.024 (z<=1.4).
4. Wo bachha hissa **2014-17 me hi** (farak/control 1.089, z 3.4); **2018-26 me 1.012 (z 0.7)**. Saal-wise lift 2015 ke 1.30 se 2025-26 me 1.06; 2022 random se neeche.
5. Lift GL aur DS ke cell me (1.23-1.25), FB/GB me kam (1.07-1.09). "Series spot" wale number random se kam (0.96, z -2.0): series variants se kuch nahi milta.
6. Multiple testing: farak z 6.3 har shuffle null se upar (row/col max-z 3.64, year-shuffle 2.93), par null run kam hone se sabse chhota p sirf 0.077/0.2 mil sakta tha. **Copy aur family null ko paar nahi karte. Tokri random se KAM (0.913, z -4.4).**
7. Heavy sample (237 din): naksha 1.158 (CI 0.91-1.41, z 1.24), naksha-rashi 1.017, steps 0.949: sab shor ke andar. 3 heavy shuffle me naksha 0.86-0.95.
8. 100 heavy variants me 2 ke z>2, koi < -2. Sabse achha (naksha2 L=15 top6, location-exact, z 2.75) shuffle ki range me (null max 2.04, p 0.25).
9. "Hit hue map" persistence: jo map hit hota hai wo live list se nikal jata hai (dobara hit nahi). Jo live map kal hit nahi hue unki hit-dar 1.045x, naye map ki 1.043x: barabar. Daily-excess lag-1 autocorrelation ~0.
10. Number Rank me zyada vote = zyada hit-dar, **haal ke number dohrane ke asar se zyada nahi**. **Koi code badlav nahi banta.**

## 1. Dana-farak vs recency (n=15045, core set)
| Naap | Hit-dar | Lift (uniform 0.2225) |
|---|---|---|
| Farak, asli | 0.2533 | 1.139 |
| Recency control (2 haal ke number + palat) | 0.2446 | 1.099 |
| DS-bias se expected | 0.2233 | 1.004 |
| Within-year shuffle | - | 1.005-1.024 |
- DS ka bias sirf +0.0008 jodta hai, lift ki wajah nahi.
- Game-wise cell lift: FB 1.086 (z 1.7), GB 1.066 (1.3), GL 1.226 (4.8), DS 1.248 (5.1). Din-offset: usi din 1.21, +1 din 1.17, +2 1.15, +3-5 1.10.
| Daur | farak | control | uniform | farak/control | z |
|---|---|---|---|---|---|
| 2014-17 (n=4534) | 0.2759 | 0.2533 | 0.2223 | 1.089 | 3.4 |
| 2018-26 (n=10511) | 0.2436 | 0.2408 | 0.2226 | 1.012 | 0.7 |
Saal-wise farak/control: 2014 1.13, 2015 1.11, 2016 1.05, 2017 1.08, 2018 0.96, 2019 1.02, 2020 1.00, 2021 1.09, 2022 0.91, 2023 1.02, 2024 1.05, 2025 1.05, 2026 1.02.

## 2. Pattern table (light, walk-forward) - poori: `out/tables_light.md`
| Pattern (default) | n | set | hit | random | lift (CI) | z |
|---|---|---|---|---|---|---|
| copy | 2225 | 3.9 | 0.165 | 0.148 | 1.116 (1.00-1.23) | 1.95 |
| family | 8291 | 7.5 | 0.285 | 0.268 | 1.064 (1.026-1.103) | 3.3 |
| dana (sab) | 34797 | 3.35 | 0.201 | 0.192 | 1.047 (1.021-1.073) | 3.5 |
| tokri (365d top6) | 4368 | 11.2 | 0.346 | 0.378 | 0.913 (0.875-0.952) | -4.4 |
Kam set par lift (bucket) aur saal-wise lift: `out/tables_light.md` ke section 3-4. Copy/GB chhote sample (n=587) me 1.28 dikhta hai (z 2.4) par multiple testing ke baad pakka nahi.


## 3. Sweeps (multiple testing)
Lift ke hisaab se top (n>=100): copy GB seedha 1.32 (n 288, z 2.0); copy GB all 1.28 (587, 2.4); farak saaf core 1.169 (4159, 6.3); farak all core 1.139 (15045, 6.3); family seedha confusion 1.12 (979, 2.3). Copy-GB ka CI chaura (n chhota).
Set size ke hisaab se (kam jodi par lift), bucket ka sabse achha: <=2.5: tokri top1 1.037 (z 0.7); 2.5-4.5: farak core 1.139 (6.3); 4.5-8: family all 1.064 (3.3), farak core+series 1.041 (4.0); >8: tokri 1 se neeche. **Kam jodi (<=2.5) par koi asli lift nahi.**
Family-wise (max-z) test:
| Pattern | K | Best variant | z | Bonferroni p | Row/col null max z (12 run), perm p | Year-shuffle null max z (4 run), perm p |
|---|---|---|---|---|---|---|
| copy | 15 | GB all | 2.43 | 0.11 | 2.93, 0.15 | 2.53, 0.40 |
| family | 9 | all | 3.27 | 0.005 | 1.88, 0.077 | 1.59, 0.20 |
| dana | 48 | farak all core | 6.29 | 8e-9 | 3.64, 0.077 | 2.93, 0.20 |
| tokri | 35 | 1095d top1 | 0.68 | 1.0 | 2.10, 0.77 | 2.35, 1.0 |
| ALL light | 107 | farak all core | 6.29 | 2e-8 | 3.64, 0.077 | 2.93, 0.20 |
| naksha | 25 | L=10 top12 | 2.29 | 0.28 | 1.08, 0.25 (3 run) | - |
| naksha2 | 40 | L=15 top6 loc-exact | 2.75 | 0.12 | 2.04, 0.25 (3 run) | - |
| steps | 35 | L=12 links=2 top24 | 0.78 | 1.0 | 0.88, 0.50 (3 run) | - |
Farak ka z 6.3 har shuffle null ke max z se bada, par null run kam hone se perm p ka chhota sambhav ank 1/13, 1/5, 1/4 hi hai.

## 4. Heavy sample (237 din ~5%; asli + 3 shuffle)
| Pattern | n | Hit | Random | Lift (CI) | z | Shuffle lift |
|---|---|---|---|---|---|---|
| naksha L=all top12 | 2478 | 0.0956 | 0.0826 | 1.158 (0.91-1.41) | 1.24 | 0.86, 0.95, 0.90 |
| naksha2 L=all top12 | 10352 | 0.5507 | 0.5416 | 1.017 (0.97-1.07) | 0.68 | 1.00-1.02 |
| steps L=all top8 | 1113 | 0.1554 | 0.1638 | 0.949 (0.80-1.10) | -0.66 | 0.85-1.07 |
100 eligible variants me 2 ke z>2, koi < -2. Sabse achha naksha2 L=15 top6 location-exact (lift 1.173, z 2.75) null range ke paas. 237 din se 15% se chhota lift pakadna mushkil: "asar nahi hai" nahi, "asar dikha nahi" likho.

## 5. Persistence aur vote calibration
- **Hit hue map (dana):** map hit hote hi live list se hat jata hai, isliye "kal hit hua" group bana nahi sakta. Jo live map kal hit nahi hua: n 13889, lift 1.045 (z 1.9); naye map: n 23542, lift 1.043 (z 2.2): barabar => persistence ka nishan nahi. Din-wise lag-1 autocorr: dana 0.018 (+-0.015), family -0.004, copy 0.07 (+-0.036), koi significant nahi.
- **Number Rank vote (237 din, sirf listed number):** vote 0: 0.91; 1: 0.85; 2: 0.86; 3: 0.91; 4-5: 1.04; 6-8: 1.00; 9-14: 1.07; >=15: 1.06. Tokri number 0.83 (z -2.3). Top-3 per din 1.37 (n 711, z 1.56); top-1 0.86 (z -0.45). Koi significant nahi.
- **Vote vs recency:** vote aur "pichle 12 din me aaya" ka correlation 0.30; pichle 12 din ki ginti 0/1/2+ par lift 0.95/1.07/1.19. Vote zyadatar recency hi napta hai, calibration ka saboot nahi.

## Kya iska matlab (user ke liye, aasaan Hinglish)
13 saal ki jaanch me koi bhi pattern (copy, family, naksha, naksha-rashi, steps, tokri) random se **saaf aur tikau** behtar nahi nikla. Sabse bada asar Dana-Farak ka dikha (1.14 guna), par uska zyada tar hissa isliye hai ki **jo number haal me aaya wo jaldi dobara aa jata hai** (yaani chhote-din ka dohrana), kisi design ki wajah se nahi. Wo bachha hua chhota hissa bhi sirf shuru ke saalon (2014-17) me tha, ab (2018-26) lagbhag khatam. Tokri to random se bhi kharab nikli. "Hit hue map" dobara hit hone ka bhi saboot nahi, aur zyada vote wale number bhi koi khaas behtar nahi. Isliye abhi kisi pattern ko "kaam karta hai" kehna theek nahi, aur app me koi badlav zaroori nahi. Paper trading me pass/fail naapte rehna sahi hai.

## Aage ka kaam
- Dana-farak par "haal ke number" control ko app me dikhana (har pattern ke saath: random me kitna hit aata hai).
- Heavy sample sirf 5%; poora walk-forward naksha/steps par baaki (har din ~1-2 s, ~2 ghante).
