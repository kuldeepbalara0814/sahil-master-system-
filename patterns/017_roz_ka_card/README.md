# 017 Roz ka card  -- KAGAZ KA KALPNIK PUZZLE (paper test)

User ki maang (28 Nov 2026): jo card us din haath se bana, wahi card, wahi design, app roz khud banaye. **Sirf DS ka result aane ke baad**, kabhi kal ke purane data par nahi.

## Card ke number (us din ki subah wali LOCK tokri, data/pockets.json)
| | list | pockets.json key |
|---|---|---|
| 1 | 30 jodi (sab pattern) | top30 |
| 2 | Naksha: aaj ke naye + pehle bane naksha jinme aaj ki tarikh ka box | naksha + naksha_sab |
| 3 | Dost 30 | dost |
| 4 | Ek baar ki window (us weekday ki Baar tokri) | baar |

- 1, 2, 3 teeno me jo jodi = card ki jodi.
- Inme jo 4 me bhi = **SOLID** (upar hara dabba). Baaki = **SPOT** (neeche).
- Neeche "FD GB GL DS" aur chhota "Sahil Lab | paper test".
- 28 Nov 2026: 12 jodi; solid 58 79 85 97; spot 10 15 24 42 51 52 59 74 (haath wale card se milaya, test `tests/test_card.py`).

## Kab banta hai (tarikh ka niyam)
- Record ka niyam: line D ka DS agli subah (~5:30) aata hai. Isi se line D poori hoti hai.
- Tarikh D ka card = line D-1 poori (D ki subah DS aaya) + us line par naya scan (asof D-1, play_date D) + D ki tokri lock.
  Yaani 28 Nov ka card 28 Nov ki subah (27 Nov ki line ka DS aane ke baad, scan 07:15) wali tokri se. Haath ka card bhi isi se bana tha.
- Shart poori na ho to card nahi banta, agli run (Action roz 8 baar, ya app khulne par) phir dekhti hai:
  scan purana / galti wala, tokri lock nahi, tokri "late" (result aane ke baad bani), ya play date aaj se pehle ki (aaj ka DS abhi nahi aaya).
- Ek baar bana to **LOCK** (`data/cards.json`), dobara kabhi nahi badalta. Mahine ki chhuti: 30 ki subah 1 tarikh ka card ban sakta hai.

## Kahan
- Banana: `lab/update.py` (GitHub Action) aur app ka scan (`lab_server._save_scan`), dono `lab/card.py make()`.
- Record: `data/cards.json` (tarikh -> solid, spot, scan); JPG `data/cards/<tarikh>.jpg` (Action commit karti hai).
- App: Aur > **Meri Window** me upar "Roz ka card" (photo + JPG download + pichle card). API: `/api/card`, `/api/card/<tarikh>.jpg` (`?download=1`).
- Kuch nahi khelta, koi bet nahi lagti. Ab tak ki jaanch me in list ka natija random jaisa. Faisla insaan ka.

Wapas: `git revert <hash>`.
