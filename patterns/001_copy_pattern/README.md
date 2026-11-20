# Pattern 001: Copy Pattern (aap ne 2026-11-20 ko sikhaya)
Chalti hai sirf 3-6 mahine, phir badal jaati hai. Isliye sirf pichle 3-6 mahine me parkho, 13 saal par nahi.

## Meri samajh
1. Ek hi game me do number aaye jinme 1 ya 10 ka farak ho (seedha ya palat karke): 38/84 (palat 83, 84 usse 1 door), 73/47, 16/51, 80/70, 97/98.
2. Un do se 4 jodi ka set: dono number + dono ke palat (80,70 -> 80,70,07,08). Palat wale halka play.
3. Seedha shape: din1, din2, [ek din gap], din4. Ulta shape: din1, [gap], din3, din4 (97,98,97).
4. Din4 par set ka koi number kisi bhi game me aaye = PASS, warna FAIL.

## Aap ke examples (examples.csv, blue = Oct, yellow = Nov)
Oct 6-9 GB 38,84 -> GL 83 | Oct 13-16 DS 97,98 -> 97 | Oct 18-21 GL 73,47 -> DS 47 | Nov 9-12 DS 16,51 -> GL 15 | Nov 17-18 DS 80,70 -> 20 Nov baaki (07,08,70,80).

## 3 mahine ka hisaab (1 Sep - 19 Nov)
Seedha: 23 bane, 22 pure, 6 PASS, 16 FAIL. Ulta: 18 bane, 2 PASS, 16 FAIL. Random se bhi ~15% baar pass hota hai. Ye pattern isi dauran dekha gaya, isliye pakka parakh nahi.

## Jo pakka nahi (aap se puchna hai)
"10 dane" ka matlab; teesra number x se ya y se; pass kis game me; "halka play" kitna.
