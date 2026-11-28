# AUTO INDEX (scripts/kitab.py ne banaya; hath se mat badlo)

## Pattern folders

- `001_copy_pattern`: Pattern 001: Copy Pattern (aap ne 2026-11-20 ko sikhaya)
- `002_mapping_pattern`: 002 Mapping pattern (naksha pattern)
- `003_family_pattern`: 003 Family pattern (rashi family ki chain)
- `004_baar_tokri`: 004 Baar tokri (weekday ke zyada aaye number)
- `005_dana_farak_box`: 005 Dana-Farak (4 Din Box)  [pushti baaki]
- `006_single_sheet_naksha`: 006 Single sheet Naksha (ek game ki apni sheet par mapping)  [SIKHANA JARI, kuch banaya nahi]
- `007_puzzle_steps`: 007 Puzzle-Steps (3 mahine ek sheet par step 1 / 2 / 3)  [APPROVED version, user ne kaha "push kar do live"]
- `008_ds_recency`: 008 DS Recency (DS ke pichle number dohrate hai) - paper R&D, FORWARD TEST chal raha hai
- `009_ank_chal`: 009 Ank-Chal  [naya, 24 Nov 2026 - pushti baaki, SIRF paper/research, software sirf dikhata hai, faisla insaan ka]
- `010_meri_window`: 010 Meri Window (sirf kagaz ka research)
- `011_help_bot`: 011 Sahil Lab Help (chat robot) - Phase 1: sirf sawaal-jawaab
- `012_paas_ank`: 012 Paas-Ank (user ka logic, 25 Nov 2026) - pushti baaki, app me NAHI joda
- `013_auto_fetch_alerts`: 013 Auto fetch (result aate hi) + banner khabar + 007 aage badhe  (24 Nov 2026, user ki maang)
- `014_safeguard`: 014 Pehredaar (safeguard) aur madad wale tools  (25 Nov 2026, user: "git par push ke time safe rakhe, galat chij ko roke")
- `015_auto_pockets`: 015 Auto paper pockets (user, 27 Nov 2026)  -- sirf KAGAZ, asli paisa nahi
- `016_connector`: 016 Claude connector (MCP)  -- KAGAZ KA KALPNIK PUZZLE KHEL
- `017_roz_ka_card`: 017 Roz ka card  -- KAGAZ KA KALPNIK PUZZLE (paper test)

## Code (har file ka kaam)

| File | Kaam |
|---|---|
| lab_server.py | Sahil Lab web server (Flask). |
| lab/__init__.py | Sahil Lab: result data, dost (friend) lists, aaj ki list, paper trading, monitor, auto-fetch. |
| lab/active.py | Active registry: jo pattern ek baar bana wo kabhi gayab nahi hota. |
| lab/alerts.py | Banner khabar: result aane ke baad kaun se current pattern NAYE active hue (patterns/013_auto_fetch_alerts/README.md). |
| lab/ank_chal.py | 009 Ank-Chal (naya pattern, 24 Nov 2026) - patterns/009_ank_chal/README.md |
| lab/baar.py | Baar (weekday) ki tokri: us weekday par jo 6 number sabse zyada aaye + unke palat. Aaj ki jodi par highlight (hint) ke liye. |
| lab/backtest.py | Idea ka backtest: aaj tak ke result par dekho ki idea chalta ya nahi. |
| lab/band.py | Band rashi / band number: kitne din se (kisi bhi game me) nahi aaye. |
| lab/card.py | Roz ka card (patterns/017_roz_ka_card/README.md). SIRF KAGAZ ka puzzle: asli paisa, salah ya bhavishyavani nahi. |
| lab/dana_farak.py | 005 Dana-Farak (4 Din Box): patterns/005_dana_farak_box/README.md. |
| lab/data.py | Result data: load / validate / merge (kabhi duplicate nahi). |
| lab/ds_rule.py | 008 DS Recency: DS ke pichle number dohrate hai (paper forward test + apne aap chalne wala kagaz ka khata). |
| lab/export_all.py | Ek pattern ke saare items ek saath download: PDF / JPG / Excel (har pattern 'Pattern 01', 'Pattern 02'...) |
| lab/export_xlsx.py | Record ka Excel: aap ki 'ANNUAL RESULT CHART' wali sheet jaisa (har saal ka block, mahine side-by-side, FB GB GL DS). |
| lab/fetcher.py | Result site (pehli) ke mahine ke chart se nayi lines laana. |
| lab/friends.py | Dost (saathi) numbers. |
| lab/gamefiles.py | Har game ka alag record: FB, GB, GL (2013 se) aur DS (1966 se). Sab 'sab ek me' results.csv se bante hain, isliye wo update hota hai to ye bhi apne aap. |
| lab/gapchain.py | Gap filter: ek hi gap se bane 'step' pakadta hai. |
| lab/gh.py | GitHub se data files padhna/likhna (Render ka disk restart par mit jaata hai). |
| lab/health.py | healthchecks.io jaisi 'zinda ho?' ghanti: HEALTHCHECK_URL (Render env / GitHub secret) ho to har update ke baad ping. |
| lab/help_bot.py | Sahil Lab Help (Phase 1): sirf sawaal-jawaab. Koi data, bet, setting ya code nahi badalta. |
| lab/help_docs.py | Sahil Lab Help: docs (README / HANDOFF / GLOSSARY / pattern README) me se jawab dhundhna - bina AI ke (hybrid ka 'docs' hissa). |
| lab/help_faq.py | Sahil Lab Help: aam sawaalon ke TAIYAR jawab (bina AI ke, zero token). README/HANDOFF/Guide se, sahi aur chhote. |
| lab/hits.py | Hit hue map (short list): jis map (pattern ke andaze) ka number aaya wo 3 din Active window me alag se. |
| lab/idea.py | Aap ki bhasha (Hinglish) me likha idea -> backtest wala spec. |
| lab/mcp_endpoint.py | Sahil Lab ka MCP endpoint (Claude ke custom connector ke liye). |
| lab/mcp_tools.py | Claude connector ke aur tool (patterns/016_connector/README.md). SIRF PADHTE hain: koi file, bet, scan ya GitHub par likhna nahi. |
| lab/monitor.py | Monitor: har strategy ka rolling hit % vs break-even. Asar ghat jaye to chetavani. |
| lab/paper.py | Paper trading (kalpnik paisa). Koi asli paisa nahi. |
| lab/partial.py | Aadhi line (partial result): aaj ke jo game aa chuke (FB shaam ~6:30, GB raat ~10:30, GL raat ~12:15) -- DS agli subah ~5:30. |
| lab/picks.py | Aaj ki list: single jodi aur har game ki 10 number ki list. |
| lab/pockets.py | Auto paper pockets (patterns/015_auto_pockets/README.md). Sirf KAGAZ ka hisaab, asli paisa nahi. |
| lab/rank.py | Number Rank: aaj ke saare pattern (map) number ke liye vote dete hain. Ek map = ek vote (ek number par). |
| lab/reqbox.py | Duet (Claude connector) ka request box: bug / idea / badlav / sawal likhna. SIRF LIKHA jata hai - koi code, bet ya record nahi badalta. |
| lab/scan_view.py | Pattern Scan: ek pattern ka saaf rang wala chart (app me dikhane ke liye) aur wahi Excel me. |
| lab/scanner.py | Pattern Scan: sikhaye hue har pattern ko roz apne aap chalata hai aur batata hai ki aaj kya ban raha hai. |
| lab/steps.py | 007 Puzzle-Steps: 3 mahine ek lambi sheet par step 1 / step 2 / step 3 ka design (patterns/007_puzzle_steps/README.md). |
| lab/tick.py | App ki apni ghadi: kaun sa result ab tak aa jana chahiye tha par nahi aaya (patterns/013_auto_fetch_alerts/README.md). |
| lab/update.py | Roz ka kaam (ek command):  python -m lab.update |
| lab/window.py | Meri Window (24 Nov 2026): app ke andar ek alag, 'apni chuni hui' screen. |
| lab/yaad.py | Naksha ki yaad (patterns/010_meri_window/README.md): naksha ka chart aage ke 8 din tak '?' box dikhata hai, par card sirf agle din ka |
| scripts/backup.py | 3-2-1 backup: ek zip jisme poori git history (sab branch), data, AI ke notes aur wapas laane ke kadam. |
| scripts/copy_pattern_demo.py | Copy pattern (patterns/001) ko kisi bhi range par dhoondh kar Excel me rang se dikhao. |
| scripts/fetch_ds_history.py | DS (Desawar) ka purana record 1966-2012 doosri site se uthao -> data/ds_1966_2012.csv  (ek baar chalane ka kaam). |
| scripts/help_selftest.py | Sahil Lab Help ka ASLI jaanch (Termux me chalao). Sarvam ko ek chhota sawaal bhejta hai aur dikhata hai ki jawab aaya ya nahi. |
| scripts/kitab.py | patterns/AUTO_INDEX.md code se apne aap banata hai (files, pattern, API, data, tools, tests). Hath se mat badlo. |
| scripts/make_zolly.py | Zolly (animated avatar) ke app-assets banata hai: ek video (mp4) se. |
| scripts/pattern_excel.py | Pattern ki Excel copy: record chart + aap ke nishaan rang me (blue = pichla mahina, yellow = is mahine) + 'Padho' sheet. |
| scripts/photo.py | README ki photo asli data se banata hai: docs/photo/ me naksha chart, card 007 chart aur roz ka card. |
| scripts/puzzle_pattern.py | Puzzle-Steps: EK FILE ki script (copy-paste karke kisi bhi jagah chala sakte ho, Termux me bhi). |
| scripts/safeguard.py | PEHREDAAR: galat cheez GitHub tak na pahuche (patterns/014_safeguard/README.md). Sirf padhta hai, kuch badalta nahi. |
| scripts/selfcheck.py | Sahil Lab khud-jaanch. JSON report banata hai; padho, theek karo, --clean se report mita do. Kuch badalta nahi, sirf padhta hai. |
| lab_static/ | alerts.js, app.js, help.js, tabs_active.js, tabs_baar.js, tabs_core.js, tabs_guide.js, tabs_lab.js, tabs_pattern.js, tabs_pockets.js, tabs_rank.js, tabs_scan.js, tabs_window.js |

## API raaste

`/`, `/api/active`, `/api/active/scan`, `/api/alerts`, `/api/ank`, `/api/baar`, `/api/baar/all`, `/api/band`, `/api/card`, `/api/card/<date>.jpg`, `/api/diag/site`, `/api/download/results.csv`, `/api/drift`, `/api/dsrule`, `/api/export/record.xlsx`, `/api/fetch`, `/api/friends/<int:x>`, `/api/gaps`, `/api/health`, `/api/healthz`, `/api/help`, `/api/help/request`, `/api/help/requests`, `/api/help/status`, `/api/help/unlock`, `/api/hits`, `/api/lab/delete`, `/api/lab/ideas`, `/api/lab/parse`, `/api/lab/save`, `/api/lab/test`, `/api/monitor`, `/api/overview/<period>`, `/api/paper`, `/api/paper/place`, `/api/pattern/boards`, `/api/pattern/delete`, `/api/pattern/save`, `/api/pattern/sheet`, `/api/pattern/xlsx`, `/api/patterns/index`, `/api/pockets`, `/api/pockets.xlsx`, `/api/rank`, `/api/record`, `/api/record/game`, `/api/record/game.csv`, `/api/record/game.xlsx`, `/api/result/manual`, `/api/result/manual/delete`, `/api/review`, `/api/scanner`, `/api/scanner/bulk`, `/api/scanner/month_view`, `/api/scanner/months`, `/api/scanner/play`, `/api/scanner/plays`, `/api/scanner/run`, `/api/scanner/to_board`, `/api/scanner/view`, `/api/scanner/xlsx`, `/api/status`, `/api/tick`, `/api/today`, `/api/window`, `/api/window/pdf`, `/api/yaad`, `/mcp/<key>`

## Data files (app GitHub se sync karti hai)

`results.csv`, `paper_ledger.json`, `friends_snapshot.json`, `drift_log.json`, `monitor.json`, `fetch_log.json`, `ideas.json`, `boards.json`, `patterns_today.json`, `play_log.json`, `active_log.json`, `hit_log.json`, `review_log.json`, `manual_results.json`, `window_log.json`, `help_requests.json`, `partial_results.json`, `alerts.json`, `tick_log.json`, `pockets.json`, `cards.json`, `duet_requests.json`

## Connector tools

`aaj_ki_list`, `aaj_ki_tokri`, `aakhri_result`, `active_patterns`, `ank_009`, `card_007`, `din_ka_natija`, `ds_rule_008`, `error_jaanch`, `guide`, `jodi_khojo`, `monitor`, `naksha_aaj`, `paper_khata`, `pocket_report`, `request_likho`, `requests_dekho`, `roz_ka_card`, `sehat`, `tulna`

## Tests

- `tests/test_card.py`: 8 test
- `tests/test_core.py`: 6 test
- `tests/test_fetcher.py`: 5 test
- `tests/test_lab.py`: 167 test
- `tests/test_mcp.py`: 13 test
- `tests/test_paper.py`: 7 test
- `tests/test_server.py`: 8 test

## HANDOFF ke aakhri faisle (kul 83)

- 72. Mapping sirf DS ke baad (user, 26 Nov 2026):
- 73. Auto paper pockets (user, 27 Nov 2026):
- 74. 3 bug (bahari jaanch, 27 Nov, maine verify ki):
- 75. 28 Nov 2026:
- 76. 30 jodi ki parakh ka niyam tay (user ki haan, 28 Nov 2026):
- 77. Claude connector (MCP), 28 Nov 2026 (user ka patch, jaanch kar lagaya, user ki haan se push):
- 78. Connector ke 9 aur sirf-padhne wale tool (user, 28 Nov 2026):
- 79. Roz ka card (user, 28 Nov 2026: "same card same design roj app banaye, DS ka result aane ke baad, kal ke old par nahi"):
- 80. Roz ke card ka pocket + duet ka request box (user, 28 Nov 2026):
- 81. Bada laal box (user, 28 Nov 2026):
- 82. "Koi bhi AI bina bataye samajh sake" + 3-2-1 backup (user, 28 Nov 2026: "itni mehnat se app bani, kal kuch ho to sab suru se batana possible nahi"):
- 83. GitHub panna + branch ka tareeka (user, 28 Nov 2026: "open source, jaise git par diya hota hai, naksha ke photo; engineer ki tarah branch"):
