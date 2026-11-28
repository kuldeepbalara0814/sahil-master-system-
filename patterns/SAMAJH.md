# Sahil Lab ki kitab: app aur pattern kaise bante hain

> Kagaz ka kalpnik puzzle khel (paper test). Ye kitab "kaise aur kyu" samjhati hai; sach ka aakhri roop code hai.
> Code ki taaza suchi: `AUTO_INDEX.md`. Faisle aur unki wajah: `HANDOFF.md`.

## 1. Data
- `data/results.csv`: har din ki ek line `date,fd,gb,gl,ds` (2013 se). Number 00-99. Andar code me FD ko `FB` bhi kehte hain.
- DS usi tarikh ki line me likha jata hai jo agli subah ~5:30 khulta hai. Isliye line DS aane par hi "poori" hoti hai.
- Mahine ke aakhri din chhutti: us tarikh ki line nahi. (`lab/data.is_last_day`)
- DS ka purana hissa 1966-2012: `data/ds_1966_2012.csv`.
- Naya data: `lab/fetcher.py` site se lata hai; purani line kabhi nahi badalta; beech ka din na bhara ho to aage nahi jodta.

## 2. Roz ka chakkar
1. DS aata hai -> nayi poori line -> **naya scan** (`lab/scanner.py` sab pattern) -> 30 jodi tokri, pocket, card **lock**.
2. FD/GB/GL aate hain -> sirf aadhi line (`data/partial_results.json`), hit jaanch, banner. **Maps nahi badalte.**
3. Kaun lata hai: GitHub Action (`.github/workflows/daily.yml`) aur app ki apni ghadi (`lab/tick.py`, `/api/tick`, cron-job.org ping). Result site Render ko 403 deti hai, isliye app Action chalati hai.
4. Kuch na bane to app ke upar **bada laal box** (`tick.khatra`).

## 3. Naksha (002): "purane saal me wahi rang ka design"
Code: `scanner.scan_naksha`, `match_info`. Sirf data aur ginti, koi AI nahi.
1. Naye data ki aakhri **L line** lo (L = 10, 12, 15, 18).
2. Har cell ka **class**: number aur uska palat ek (28 = 82). (Naksha-Rashi 002b: class = rashi/family.)
3. Naye tukde ke andar jin do cell ka class same, wo **link**.
4. 2013 se ab tak har purane L-line tukde me dekho: wahi link **usi jagah (game) aur usi duri** par kitne bane. Zyada = achha milan; score `z` (ausat se kitna upar).
5. Har lambai ke 12 sabse achhe milan (ek dusre se 20 line door). Barabar score me purani jagah pehle (`best_order`, har machine par ek jaisa).
6. **Rang:** jude hue link ka ek group = ek rang. "Hara se hara" = purane aur naye me wahi group, wahi jagah. Rang ka apna koi matlab nahi, sirf pehchan.
7. **Andaza:** purane tukde ke aage wali line me jo cell kisi group ke purane class ka hai, naye me wahi jagah us group ka naya class (number + palat) '?' box.
8. `mazboot/theek/kamzor`: z ko random jagah ke best se tolte hain (`BASE`). 900 din ki jaanch: hit random jitna.
9. **Naam** (`name_for`): pattern ki pehchan se bana label (jaise Naksha-Hans-97); naam ka koi matlab nahi. Purana tukda roz ek line khisakta hai to naam bhi badalta hai.
10. **Yaad** (`lab/yaad.py`): aaj ki tarikh par pichle 8 din ke scan ke '?' box bhi.
Sikhaai abhi adhuri hai (step 1/2/3 khelna): `002_mapping_pattern/README.md`.

## 4. Baaki pattern (niyam ek line me; poora README aur code me)
| No | Naam | Niyam | Code |
|---|---|---|---|
| 001 | Jodi-Copy | ek game me do number jinme 1 ya 10 ka farak; din 1, din 2/3, din 4 par set ka number = PASS | scanner.copy_events |
| 003 | Family | ek rashi din d, d+1/d+2, phir d+3 par family khelna | scanner.family_events |
| 004 | Baar | us weekday par pichle 365 din ke 6 sabse zyada number + palat | baar.tokri |
| 005 | Dana-Farak | 4 din ke box me dana 10/01 farak wale do number | dana_farak.py |
| 006 | Single sheet | sikhana jari, bana nahi | - |
| 007 | Puzzle-Steps | 3 mahine ek sheet; Step 1 ka design Step 2, 3.. me usi duri (box) par. **User: abhi poora sahi nahi, dobara sikhayenge; bina sikhaye mat badlo** | steps.py |
| 008 | DS Recency | DS ke pichle number dohrate hain; paper forward test | ds_rule.py |
| 009 | Ank-Chal | 2 draw pehle ka ank usi jagah | ank_chal.py |
| 012 | Paas-Ank | paas ke ank; jaancha, random jaisa, app me nahi | research/paas_ank |

## 5. Rank, 30 jodi, dost, card, pocket
- **Dost** (`friends.py`): ek number ke aas-paas (usi din baad ke game + agle din) sabse zyada aane wale. Rank me: pichli line ke har number ke 12 dost (5 hara, 4 peela, 3 narangi) x 3 samay (poora, 3 mahine, is mahina).
- **Number Rank** (`rank.py`): score = kitne alag pattern ne jodi di + dost ke point + 2 agar Baar me.
- **30 jodi** = Rank ke upar ke 30 (Meri Window tokri).
- **Roz ka card** (`card.py`, user ka tarika): (30 jodi) aur (Naksha naye + pehle bane) aur (Dost 30), **teeno me** jo jodi. Unme se jo us din ki Baar me bhi = **SOLID** (upar hara), baaki **SPOT**. Neeche FD GB GL DS. DS aur lock ke bina nahi banta.
- **Pocket** (`pockets.py`): har list ka Rs 10,000 kagaz: har jodi par FD 10, GB 15, GL 20, DS 25; hit par us din ruk; 95 guna (40+ jodi par 90). Random 30 pocket tulna ke liye. 01 Dec 2026 se.
- Parakh ke pehle se tay niyam: `015_auto_pockets/README.md`.
- Ganit: is seedhi me har chaal ausat ghate ki hai (95/100). Koi list random se saaf aage ho tabhi baat.

## 6. App, connector, suraksha
- Flask `lab_server.py` + `lab_static/*.js`. Render free plan; `data/**` par deploy nahi; deploy sirf `code-tests` pass par.
- Connector (`/mcp/<MCP_KEY>`, `mcp_endpoint.py`, `mcp_tools.py`): sirf padhta hai; akela likhne wala `request_likho`.
- Help bot (Zolly): sawal-jawab aur request box; code kabhi nahi badalta.
- Pehredaar (`scripts/safeguard.py`, `.githooks/pre-push`, CI): record, secret, tuta code, bina note ka code, force push rokta hai.
- Khud-jaanch: `python scripts/selfcheck.py --live --tests`, theek karke `--clean`.

## 7. Gupt cheezein (sirf NAAM; value kahin nahi likhni - apni diary me rakho)
Render env: `ADMIN_PIN`, `HELP_PIN`, `SARVAM_API_KEY`, `GITHUB_TOKEN` (is repo par Contents + Actions read/write), `MCP_KEY`, `HEALTHCHECK_URL` (marzi). Phone: SSH key (GitHub push). Bahar: cron-job.org (`/api/tick`).

## 8. Sab kuch kho jaye to wapas kaise (3-2-1)
**3 copy, 2 alag jagah ke saadhan, 1 ghar se bahar:** GitHub (repo) + phone `Download/SahilBackup/*.zip` + Google Drive (wahi zip). Chaho to PC / pen drive par bhi.
`python scripts/backup.py` -> zip (poori git history sab branch, notes, RESTORE.md). Zip ke andar `RESTORE.md` ke kadam. Render par: naya web service, repo jodo (`render.yaml`), upar wale env dobara daalo.
