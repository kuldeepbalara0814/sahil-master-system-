# 008 DS Recency (DS ke pichle number dohrate hai) - paper R&D, FORWARD TEST chal raha hai

Ye **puzzle-logic R&D** ka hissa hai. **Sirf paper trading.** Asli paisa lagane ki salah nahi: commission, bhugtan ki der, limit aur lambi haar asli faayda kha sakte hai.

## Kya mila (R&D, 23 Nov 2026; research/recency/REPORT.md)
- **DS me jo number abhi 2 se 5 result pehle aaye wo thoda zyada wapas aate hai.** 100 me 1 baar (1.0%) ki jagah lagbhag **1.4%** (1.37%; 2022-26 me 1.47%).
- Ye **60 saal (1966-2026) me har dashak me** dikha aur **dusre website ke alag data me bhi** (2022-26: 1.41%). Yani data ki galti nahi lagti.
- **Rule (jo forward-test ho raha hai):** DS ke **2, 3, 4, 5 result pehle wale 4 exact number** (1 result pehle wala chhodo; palat nahi). Roz, **har din** (hint din ka koi filter kaam nahi karta).
- Break-even: rate 95 guna ho (40 se kam number par) to 1.05% per number, 90 guna ho to 1.11%. Isliye 1.4% = kagaz par lagbhag **+30 se +40%** har lagaye rupaye par.
- Ye **saal ka %** nahi hai (share market ke "15-20% saal" se mat milao). Ye har ₹1 par kagaz ka munafa hai, jisme hit bahut kam aata hai.

## Imandari se (kya NAHI pakka)
- **Hit ~har 17 din me ek.** Sabse lambi bina-hit streak **111 din**. Itihaas ka sabse bada gaddha 873 unit (kharch 4/din); 2022-26 me 280.
- Ek saal ka natija -39% se +57% tak gaya. Isliye "pakka pattern" nahi, **"mazboot dikhta hua asar"**.
- 83 tarike parakhe gaye, isliye shak hamesha rehta hai. Walk-forward (2018-26) me +23% (CI +14% se +32%).
- Same-din FB/GB/GL se DS ka asar ghat raha hai. FB/GB/GL ke apne pichle number me asar nahi.
- **Hint din nahi chalte** (weekday, tarikh, mahina, "abhi hit hua", agreement: kuch bhi multiple-testing ke baad nahi bacha). Palat se asar patla ho jata hai.
- Lag 1 (abhi nikla number) 0.94% (dabta hai); 2 se 6 result me wapas (1.4%); baar-baar dikhne par asar nahi badhta (chhota recycling pool).

## App me (forward test, 90 din)
**Active tab -> "DS rule (paper, forward test)"**: roz ke 4 number, hit/miss apne aap, hit-dar vs 1% (random), kagaz ka ROI (95x), abhi ki bina-hit streak. Rule **frozen** hai (badla nahi jayega). Shuru: 24 Nov 2026. Code: lab/ds_rule.py, route /api/dsrule.
**Zaroori (R&D se):** 90 din (~360 stake, ~5 hit) me **faisla nahi ho sakta** (power sirf ~10%); asli rate (1.37%) aur break-even (1.05%) me farak dikhne me **~5-6 saal** lagte hai. Isliye scoreboard ko lambe samay ka hisaab maano; rule frozen rakho; chhoti jeet-haar se faisla mat karo.

## Kagaz ka khata (apne aap, 23 Nov 2026, user ka kehna: "roz 30 Rs", auto bet/munafa/loss)
Active tab ke "DS rule" card me: **Roz 1 number** (DS ka 2 result pehle wala) ya **Roz 4 number** (2,3,4,5 result pehle), **Rs 30 har number par roz**, jeet par Rs 2,850 (95 guna), shuruaati kagaz ki raqam Rs 10,000. Har din ka bet, HIT/miss, net aur chalti raqam apne aap judti hai (shuru 24 Nov 2026); aaj ka bet, "agar pichla ~350 din ye rule chalta" ka hisaab, aur hindi me niyam card me likhe hai. Code: lab/ds_rule.py (rows se hi nikalta hai, kuch save nahi). Dhyan: 1-number rule me pichle saal sabse neeche raqam Rs 3,430 tak gayi (219 din bina hit); 4-number rule me Rs 120/din kharch.

## Aage ka R&D (sirf DS, 1966-2026)
Rule ka sudhar (lag subset, set size, recycling-pool probability), 41/05/doubles ke jhukav ka asar, edge gayab hone par jaldi pakadna (CUSUM/SPRT), bankroll aur gaddha (drawdown), dusre website par dohrana. Nateeje research/recency/.

## DS-only deep R&D (23 Nov 2026, research/recency/out/)
- Rule ka sudhar nahi mila: **lag 2-5 sabse achha** (chunav 1966-2012, test 2013-26): train 1.52%, test 1.37% (ROI +30% @95x, +23% @90x, z 5.1). Lag 2-6 1.26%, 2-7 1.23%: bada set patla; chhota set (lag 2-3: 1.40%, lag 2: 1.47%) ka rate similar par 1-2 number.
- Rolling yearly walk-forward: 1.368% (264 hit / 19,293 stake). Pool model (lag-profile se top-4) 1.35%: simple lag set se behtar nahi.
- 41/05/doubles ka jhukav **extra fayda nahi** deta (+-0.01 ROI, shor). Weekday/din/mahina filter kuch nahi (24 shart, best p_adj 0.89).
- **Dusre website** (2013-26): wahi rule 1.36% (261/19,199): data pakka.
- **Gaddha:** 1000 din me ~400 se 760 stake-unit (agar asli rate 1.37% ho; kam ho to zyada). Bankroll: Kelly ka 1/4-1/2 (~bank ka 0.2-0.4% roz); flat 1% roz par 19% chance bank 25% se neeche.
