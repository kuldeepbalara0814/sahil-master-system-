# 012 Paas-Ank (user ka logic, 25 Nov 2026) - pushti baaki, app me NAHI joda

Kuldeep ne bataya: "kuch mahino se achha chalta hai". Maine apne shabdon me likha, aur 13 saal ke data par backtest kiya (research/paas_ank/).

## Logic (mere shabdon me)
1. **Trigger:** kisi bhi game (FB, GB, GL, DS) me aisa number aaye jiske dono ank **paas-paas** hon (aapas me 1 ka fark): 12, 21, 23, 32, 34, 43, 45, 54, 56, 65, 67, 76, 78, 87 (aur 01, 10, 89, 98).
2. **Tokri (36 jodi):** us number ke do ank {a, b}. **Andar** = wo sab number jinka pehla ank a ya b ho (20). **Bahar** = jinka doosra ank a ya b ho (20). Dono milakar 36 (kyunki 4 number dono me aate hain). Jaise 21 aaya to ank 2 aur 1 ("222 ya 111").
3. **Window:** trigger ke baad **agle 4 draw**, game ke kram me FB -> GB -> GL -> DS (agle din tak). Jaise GB me aaya to GL, DS, agle din FB, agle din GB.
4. **PASS:** in 4 draw me kisi me bhi number tokri (36 jodi) me aaye. Nahi aaya to FAIL.

## Backtest ka nateeja (13 saal, 3,314 trigger, random se tulna ke saath)
- **Pass 84.4%**, par **random me bhi 83.2%** pass hota hai (36 jodi, 4 draw: 1 - 0.64^4). Fark sirf +1.2 point (z +1.9, 95% range 83.2-85.6%): bahut halka.
- **Control** (aise trigger jinke ank paas-paas nahi, tokri phir bhi 36): 83.0% = random. Yaani "paas-ank" chunne se thoda hi fark aata hai.
- **Do hisse:** 2013-19: 85.4% (z +2.3); **2020-26: 83.5% (z +0.3), random jaisa.** Asar purane hisse me tha, ab nahi dikhta.
- **Shuffle test (300):** asli pass 10/300 se upar, ROI 3/300 se upar (p lagbhag 0.03 / 0.01), par ye ek hi test nahi tha (kai tarah se dekha), aur 2020 ke baad asar gaya.
- **Paise (Rs 1 har jodi, pehla hit par ruk jao, 95 guna):** ROI **-1.6%** (random me -5%). Matlab **fir bhi ghata**, bas random se kam. Ek trigger par ~Rs 81.5 lagta hai, net -Rs 1.33; saal me ~247 trigger => Rs 1/jodi par ~**-Rs 328/saal** (Rs 10/jodi par -Rs 3,278). 14 me se 5 saal ROI plus raha, 9 saal minus.
- Alag-alag A (andar) ya B (bahar) sirf: random (59%) ke paas (60.1% / 59.4%).
- Kis game me trigger aaya: FB 86.1%, GB 85.5%, GL 84.4%, DS 81.9% (DS me kam).

## Mera nateeja (QC)
"Pass bahut hota hai" ka asli kaaran ye hai ki **tokri bahut badi (36 jodi) aur window lamba (4 draw)** hai: random me bhi 83% pass. Paas-ank se sirf thoda faida dikha jo 2020 ke baad nahi dikha, aur paise me abhi bhi ghata. **Isse tradeable edge nahi kehna chahiye.** Paper me aage ka record dekh sakte hain (app me jodna tumhari "haan" par).

## Sawal jo baaki hai (ek)
Maine 01, 10, 89, 98 (0-1 aur 8-9 ke jode) trigger me ginte hain. Tumhari list me ye nahi the. Chahte ho ki ye bhi ginein ya sirf tumhari diye hue (12, 21, 23, 32, 34, 43, 45, 54, 56, 65, 67, 76, 78, 87)?

Code: `research/paas_ank/backtest.py` (chalao: `python3 research/paas_ank/backtest.py` repo ki jad se), poora output `research/paas_ank/out.txt`.
