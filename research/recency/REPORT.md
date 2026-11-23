# Recency-repeat R&D (paper only): kam exact number, DS 1966-2026 + FB/GB/GL 2013-26
(Agent rnd-recency; report lead ne likhi. Lead ne dusre site (satta-xpress ke jagah "doosri site") ke alag DS data par bhi rule dubara chalaya: 2022-26 par 1.41% (96/6793), hamare data par 1.47% (100/6807): data-artifact nahi lagta.)

## Saar (10 line)
1. **DS ka apna pichla number dohrata hai (paper par durable edge):** rule = DS ke **2, 3, 4, 5 result pehle wale 4 exact number** (lag 1 chhodo). Hit **1.37% per number** (break-even 95x par 1.05%, 90x par 1.11%).
2. 1980-2026 me dashak-wise stable: 1.45, 1.41, 1.48, 1.42, 1.37%; 1966-79 me 1.66%. Dheema girna ~0.02%/dashak, collapse nahi.
3. 2022-26: 100 hit / 6,807 stake = 1.47%, ROI **+40% (95x), +32% (90x)**; mahine-block 95% CI +18% se +62%.
4. Controls: within-year shuffle 0.996% (200 shuffle ka max 1.20%, asli 1.37%); uniform-random walk-forward ROI -5%. Yaani bias nahi, **asli serial structure**.
5. Pure walk-forward (sirf pichle saalon se slot chuno, agle saal bet, 2018-26, 4 game x 4 number): 49,352 stake, 641 hit, 1.30%/number, ROI +23% (CI +14% se +32%). DS +29%, GL +29%, FB +23%, GB +12%.
6. Same-din FB/GB/GL -> DS asli par ghat raha (DS ROI 2022-26 ~ +9%, CI -13% se +34%). "Pichli line ke FB+GB+GL" tikta hai (+47%, CI +14% se +80%) par slot kuch data dekhne ke baad chuna gaya.
7. **Hint din kaam nahi karte:** weekday, tarikh, mahina, abhi-hit, clumpiness koi filter multiple-testing ke baad nahi bacha (best p_adj 0.61 / 0.88). Rule roz chalana hai.
8. "Agreement" rule (number 2+ source me) random se kharab (lift 0.4-1.1). Palat dilutes: exact number behtar.
9. Bharosa: DS lag 2-5 repeat chance se upar hona **ucch** (z~5, har dashak me); +30% edge tikna **madhyam**; kisi ek saal ke liye **kam** (saal -39% se +57%).
10. Ye "chhota recycling pool" lagta hai: abhi nikla number dabta hai (lag1 0.94%), 2-6 result me wapas aata hai (1.4%), baar-baar dikhna aur nahi badhata.

## 1. Rules (83, pehle se tay) - DS, 2013-26, ROI @95x, stake 1/number, ~350 din/saal
| Rule | Number | Rate % | ROI 13-26 | ROI 22-26 | 22-26 CI | Slope lift/saal |
|---|---|---|---|---|---|---|
| own lag 2+3 | 2 | 1.40 | +33% | +35% | +2% se +69% | -0.006 |
| own lag 2-5 | 4 | 1.37 | +30% | +40% | +18% se +62% | ~0 |
| pichli line FB+GB+GL | 3 | 1.52 | +45% | +47% | +14% se +80% | +0.016 |
| same din FB+GB+GL | 3 | 1.37 | +30% | +9% | -13% se +34% | -0.034 |
| same din trio + palat | <=6 | 1.23 | +17% | +12% | -4% se +29% | -0.006 |
| agreement | 1-4 | ~1.0 | ~0 | -6% se -26% | negative | - |
| lag 1 akela | 1 | 0.90 | -15% | -34% | | |
Period-wise same-din trio ROI: DS +43% / +35% / +7% (2013-17 / 18-22 / 23-26); GL +60 / +38 / +32; GB +51 / +24 / +17. Sirf DS ka own-lag rule aur pichli-line trio ghat nahi rahe.

## 2. Walk-forward + multiple-testing null (2018-26; har saal pichle saalon se chuna, ~66 candidates)
| Selection | Result | Null mean / 95th | p |
|---|---|---|---|
| Past ROI, 4 game | +10% (10,789 stake, 125 hit) | -5% / +9.9% | 0.05 |
| Past z, 4 game | +18.5% (35,441 stake, 442 hit) | - | 0.04 |
| Past ROI FB; GB, GL, DS | +30%; +12, +6, -6 | | 0.04; .23 .31 .53 |
| Past z GL / DS; FB / GB | +28% / +26%; +4% / +13% | | .02 / .04; .12 / .12 |
Null "no bet = -100%" maanta hai, isliye p halka flatter karta hai: indicative. Saal-wise z-chuna portfolio: +47, +31, +6, +31, +14, +8, +9, +1, +31 (har saal plus, baad ke saal modest).

## 3. FB/GB/GL alag (2013-26, ROI @95x)
GL <- FB same din 1.59% (+51%); GL <- GB same din 1.45% (+38%); GL <- FB+GB 1.52% (+44%, 22-26: +27%); GB <- FB same din 1.39% (+32%, 22-26: +15%); FB <- kal ka GB 1.51% (+43%); FB/GB/GL ke apne lag ~1.0-1.3% (~0). Cross-game asar ghat raha hai; sirf DS ka apna history tikta hai.

## 4. Hint din
37 shart x 4 game (weekday, din, mahina, game, pichla hit, clumpiness): null 95th max|z| 3.79, asli best 2.39 (January, p_adj 0.61): kuch nahi. DS 1966-99 train / 2000-26 test, 31 shart: best p_adj 0.88, test me sign ulat gaye. Agreement rule random se kharab. **Hint din nahi: rule roz chalana padega.**

## 5. Chhota recent pool: match vs doori (interleaved FB<GB<GL<DS, lag 1-40; out/dist_profile.csv)
DS apna lag, 1980-2026: lag1 0.94%, lag 2-5 1.43/1.35/1.45/1.45%, lag6 1.15%, lag 7-12 ~1.14%, lag 13-40 1.03% (baseline). Cross-game DS target (usi line / pichli line) 1.4-1.7%, 20-40 result par dheere 1.1-1.2%. 12-result window me ek baar dikha number DS par 1.37% (2018-26: 1.34%); 0 baar 0.96%; 2 baar 0.72%; 24-result window me 3+ baar ~0.5%. **Chhota recycling pool: abhi nikla number dabta hai, 2-6 result me lautta hai, baar-baar dikhna fayda nahi badhata.**

## 6. Risk: 4-number DS rule (lag 2-5, 95x, stake units; 4/din kharch, hit +91, miss -4)
| Sample | Din | Mean/din | Sabse lambi bina-hit streak | Itihaas ka max drawdown |
|---|---|---|---|---|
| 1980-2026 | 16,543 | +1.40 | 111 din | 873 |
| 2013-2026 | 4,908 | +1.18 | 111 din | 873 |
| 2022-2026 | 1,729 | +1.56 | 70 din | 280 |
(1000-din block resample ki baaki table agent ke message me kat gayi; dobara maangna ho to research/recency/out dekho.)

## Kya iska matlab (aasaan Hinglish)
DS me pichle 2 se 5 result ke number thode zyada wapas aate hai (100 me 1 ki jagah lagbhag 1.4). Ye 60 saal me har dashak me dikha aur dusre website ke data me bhi. Agar rate 95 guna ho to har ₹1 par kagaz ka munafa lagbhag 30 se 40%. Par hit kam aata hai (~har 17 din me ek), lambi haar aati hai (110 din tak bina hit), aur ek saal -39% se +57% ja sakta hai. Hint-din ka koi filter kaam nahi karta, isliye roz chalana padega. FB/GB/GL ke apne number me ye nahi. Abhi ise "pakka pattern" nahi, "mazboot dikhta hua asar" maano aur **90 din paper me bina niyam badle forward-test** karo. Asli paisa lagane ki salah nahi; commission, bhugtan ki der aur limit asli faayda kam kar sakte hai.
