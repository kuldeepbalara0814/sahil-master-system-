# 010 Meri Window (sirf kagaz ka research)

**Kya hai:** app me "Aur" > **Meri Window** tab. Isme sirf meri chuni hui do tokri dikhti hain; baaki sab app me pehle jaisa chalta rehta hai. Software dikhata hai, faisla insaan ka. Sab paper, asli paisa nahi.

## Do tokri (jodi)
1. **Naksha ki jodi:** aaj ke NAYE Naksha pattern jinke andaze (targets) hain. Source: `patterns_today` ke key `naksha` ke items jinme `new` aur `targets` dono hon (lab/window.py `baskets`). Har pattern ka alag Copy, aur "Sab jodi copy" (unique, sorted).
2. **Top 30 jodi:** Number Rank ka ALL list, upar ke 30 (lab/rank.py). Score = kitne alag pattern ne wo jodi di + dost ke point (har dost-list hazri 1) + 2 agar aaj ke din (baar) ki tokri me (24 Nov 2026 se; pehle +1 tha, dost nahi the).

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


## Pattern number se kholo (25 Nov 2026 jodha)
- Meri Window me "Pattern number se kholo" card: kind chuno (Naksha, Naksha-Rashi, Puzzle-Steps, Family, Copy, Dana-Farak), number likho (jaise 03) ya list se "Kholo" dabao. Wahi rang wala chart khulta hai jo Pattern Scan me "Kholo (rang me dekho)" se khulta hai, aur "Excel me dekho (download)" button.
- **Number** = wahi jo Pattern Scan aur Number Rank me "Pattern 03 (Family)" likha dikhta hai (us kind ki list me position). Naksha ka label bina bracket ka ("Pattern 04").
- List sirf **aaj ke scan** ki hoti hai (aaj ki date). Filter: "Aaj ke andaze wale" (status aaj, jinka result abhi aana hai), "Sirf naye (aaj bane)", "Sab". Jo pattern chal raha hai wo har roz ke scan me tab tak aata rehta hai jab tak uska aakhri result nahi aa jata; uske baad apne aap hat jata hai (koi alag memory/store nahi, scan roz naya banta hai).
- Top 30 ke har number ke neeche "kaun se pattern se aayi": label (jaise "Pattern 01 (Naksha-Rashi)") par dabao to wo pattern khul jata hai. (`/api/window` ke top30 me `maps`.)
- Naye Naksha pattern ke card me bhi "Kholo (No. NN)" button.
- Code: `lab_static/tabs_window.js` (`openCard`, `openItem`, `parseLabel`), `lab_server.py api_window` (maps). Chart/Excel ka purana code reuse (`window.SCANX.chart/famMonth`, `/api/scanner/view`, `/api/scanner/month_view`, `/api/scanner/xlsx`).
- **Aaj ke sab Naksha + Steps number (24 Nov 2026):** Window me ek card: Naksha 1 ke saare aaj-wale items (purane aur naye) aur Puzzle-Steps ke number, vote ke hisab se; hara = Top 30 me bhi, peela = 2+ vote. **Naksha-Rashi (2b) isme nahi** (user ne kaha). **Sirf dikhane ke liye, paper basket nahi.** Naksha pocket ab bhi sirf naye Naksha 1 ki jodi leti hai.
- **Kyun chhoota (24 Nov, FD 53 / GB 93):** GB 39/93 **Puzzle-Steps (007) No. 1** ("Pattern 01") me tha, Naksha me nahi; Steps Window me kabhi tha hi nahi (Window = naye Naksha 1 + Top 30; Top 30 me 93 ko sirf 5 vote, rank 70wa, 30wi ka score 14). FD 53 sirf kamzor Naksha-Rashi items me aur Mangalwar ki 12 jodi me tha. Naye niyam (baar 2 + dost) se bhi rank ~54wa/60wa; isliye ab Window me Steps alag card me dikhta hai.
