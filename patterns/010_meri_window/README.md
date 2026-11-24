# 010 Meri Window (sirf kagaz ka research)

**Kya hai:** app me "Aur" > **Meri Window** tab. Isme sirf meri chuni hui do tokri dikhti hain; baaki sab app me pehle jaisa chalta rehta hai. Software dikhata hai, faisla insaan ka. Sab paper, asli paisa nahi.

## Do tokri (jodi)
1. **Naksha ki jodi:** aaj ke NAYE Naksha pattern jinke andaze (targets) hain. Source: `patterns_today` ke key `naksha` ke items jinme `new` aur `targets` dono hon (lab/window.py `baskets`). Har pattern ka alag Copy, aur "Sab jodi copy" (unique, sorted).
2. **Top 30 jodi:** Number Rank ka ALL list, upar ke 30 (lab/rank.py). Score = kitne alag pattern ne wo jodi di (+1 agar aaj ke din (baar) ki tokri me).

## Tokri lock ka niyam
Us din (play_date) ka **pehla scan** tokri bana kar lock kar deta hai. Baad ke scan (jab result aa jaye) tokri nahi badalte, taaki result dekh kar tokri na badle. Tokri `window_log.json` me jati hai (sirf yahi state).

## Ladder (har jodi par Rs)
FB par Rs 10; na aaye to GB par Rs 15; na aaye to GL par Rs 20; na aaye to DS par Rs 25. Jis game me hit aaya, us din wahin STOP. Hit par 95 guna per jodi (40 ya zyada jodi par 90 guna).
Udaharan: 20 jodi => FB Rs 200, GB Rs 300, GL Rs 400, DS Rs 500 (sabse zyada Rs 1,400).

## Do pocket
Har ek kagaz ke Rs 10,000: (1) Naksha ki jodi (2) Top 30 jodi. Tab me har pocket ka: ab ka paisa, net, ROI, din, hit wale din, sabse badi giraawat, balance ka SVG graph (seedhi dashed line = shuru ki raqam), kis game me hit, roz ka hisaab, aaj ki yojana (kharcha).

## START 25 Nov 2026
Pocket ki ginti 25 Nov 2026 se. Isse pehle ki (24 Nov) tokri result ke baad bani thi, isliye sirf dikhane ke liye (`plan.counted=false`).

## Hisaab
Stateless: roz ki tokri + site/hath ke result se hisaab har baar naya nikalta hai (lab/window.py, route `GET /api/window`). Tests: tests/test_lab.py `WindowTests`.

## Code
lab/window.py, lab_server.py (`/api/window`), lab_static/tabs_window.js, Active hero me "Meri Window kholo" button, theme.css (`wn-` class).

## Wapas jane ka tarika
Tab hatana ho: `git revert <hash>` (hash PROGRESS.md me). Backend commit 5d64b16, UI addadf3, 009 tarika card 6c787b9.

## Saaf sachchai
Ye paper research hai; 25 Nov se pehle ka koi record nahi, isliye abhi kuch sabit nahi. Natija ke liye mahino ka data chahiye.
