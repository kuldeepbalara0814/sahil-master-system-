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
**Active tab -> "DS rule (paper, 90 din)"**: roz ke 4 number, hit/miss apne aap, hit-dar vs 1% (random), kagaz ka ROI (95x), abhi ki bina-hit streak. Rule **frozen** hai (badla nahi jayega). Shuru: 24 Nov 2026. Code: lab/ds_rule.py, route /api/dsrule.
90 din baad (ya jaldi, agar asar gayab ho): hit-dar 1.05% (break-even) se neeche ya random ke paas aaye to rule band.

## Aage ka R&D (sirf DS, 1966-2026)
Rule ka sudhar (lag subset, set size, recycling-pool probability), 41/05/doubles ke jhukav ka asar, edge gayab hone par jaldi pakadna (CUSUM/SPRT), bankroll aur gaddha (drawdown), dusre website par dohrana. Nateeje research/recency/.
