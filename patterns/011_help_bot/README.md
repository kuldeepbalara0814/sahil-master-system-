# 011 Sahil Lab Help (chat robot) - Phase 1: sirf sawaal-jawaab

Har tab par neeche-right robot button. Dabao -> "Sahil Lab Help" panel. Hinglish me app ke tab/pattern/niyam ke baare me poochho. **Sirf samjhata hai, kuch badalta nahi** (koi data, bet, setting ya code nahi).

## Chalane ke liye (Kuldeep ko Render me do cheez set karni hain; key kabhi chat/repo me nahi)
1. Render dashboard -> apni service **sahil-lab** -> left menu **Environment**.
2. **Add Environment Variable**: Key = `SARVAM_API_KEY`, Value = Sarvam dashboard se copy ki hui API key. (Sarvam key: dashboard.sarvam.ai -> API Keys.)
3. **Add Environment Variable**: Key = `HELP_PIN`, Value = chat ka password (jo tum chaho; na doge to `ADMIN_PIN` use hoga).
4. **Save Changes** (service apne aap dobara chalti hai, ~1-2 min).
5. App kholo -> robot button -> password dalo -> sawaal poochho.
- Key set nahi ho to chat saaf likhta hai: "API key set nahi hai - Render dashboard me SARVAM_API_KEY set karo."
- Key kabhi: chat me nahi, git me nahi, browser me nahi. Browser sirf apne server ko bolta hai; server Sarvam ko.
- Optional: `HELP_DAILY_MAX` (roz ke AI jawab ki seema, default 80), `SARVAM_MODEL` (default `sarvam-105b`), `SARVAM_URL`.

## Pehle asli jaanch (Termux me, key kahin likhi nahi jati)
`git clone https://github.com/kuldeepbalara0814/sahil-master-system-.git && cd sahil-master-system- && python3 scripts/help_selftest.py`
Script key chhupa kar poochhti hai (screen par nahi dikhti) ya `SARVAM_API_KEY` environment se leti hai. Sarvam ko ek chhota sawaal bhejti hai aur sirf status, token ginti aur jawab ke pehle 220 akshar dikhati hai. "SAB THEEK" aaye to Render me key set karo. FAIL aaye to kaaran likha aata hai: `403` = key galat/band, `400` = model ya setting galat, `429` = limit ya credit khatam, `0` = internet.
Chat me bhi galti par ab aisa hi code aur kaaran dikhta hai (kachcha Sarvam text ya key nahi).

## Surakshit kyun hai (paise Sarvam credits se katte hain)
- **Password server par jaanchta hai** (browser ki JS badalne se nahi bachega). PIN code/repo me kahin nahi likha. 4 ank ka PIN kamzor hota hai, isliye: galat PIN 5 baar lagatar -> sabke liye 15 minute band; roz ki seema; 2 second se kam gap me AI sawaal nahi; sawaal 400 akshar tak. **Salah: 6 ya zyada ank ka HELP_PIN rakho, aur aisa jo tumhare naam/GitHub username ke ank se na milta ho** (repo ka naam public hai, usme ank dikhte hain, to wo andaze me aasan hai).
- Sarvam ki galti par saaf message ("Sarvam se jawab nahi aaya, dobara try karo."), kachcha error ya key kabhi nahi dikhti. Jawab `textContent` se dikhta hai (HTML andar nahi ghus sakta).

## Token/kharcha kaise bachta hai
1. **FAQ (zero token):** 13 aam sawaal (copy, pattern number se kholna, scan time, 009, ladder, pocket, paper trading, galat result, break-even, andar/bahar, Excel, data purana, 008, PIN) ke taiyar jawab `lab/help_faq.py`. "aaj/abhi/kal" wale (live) sawaal isme nahi aate.
2. **Cache:** pichle jawab (usi live sthiti me) 3 din; milte-julte sawaal par wahi jawab. Jawab ke neeche "turant jawab (token nahi laga)" likha aata hai.
3. **Kam gyaan bhejna:** poori jaankari (`lab/help_kb.md`) nahi, sirf sawaal se mile hisse (~32% size). Kuch na mile to poora gyaan (andaza nahi).
4. **Reasoning band:** `reasoning_effort "none"` (tumhare apne test ke hisaab se sirf `/v2` par chalta hai; `-conversations`/GLM/Kimi/Gemma par nahi bhejte).
5. Roz ki seema + max_tokens 1500.

## Konsa model? (tumhare Zynta test + Sarvam docs ke hisaab se)
- **Help Q&A ke liye: `sarvam-105b` (/v2, reasoning "none")** - tumhare test me PASS (Test 1: 407 token, 3.5 sec; Test 2: 526 token, 1.2 sec). Bhav Sarvam ke pricing page ke mutabik: Rs 10 input / Rs 0.25 cached input / Rs 25 output per 10 lakh token (2026 ke ant tak intro bhav). Ek jawab ~4 paise, FAQ/cache me 0. Roz ke 80 jawab ki seema = zyada se zyada ~Rs 3/din.
- **DeepSeek:** tumhari Sarvam key par hi chalta hai (`deepseekv4.1-flash-1017`, tumhare mapping me "ffmpeg / code" ke liye), alag DeepSeek account/key nahi chahiye. Uska bhav mujhe pakka nahi mila (sirf DeepSeek V4 Pro Rs 115/350 dikha). Help Q&A me bachat itni kam hai ki badalne ka fayda nahi; **code/bug-fix wale kaam (Phase 2) ke liye ye achha dawedaar hai.** Badalna ho to Render me `SARVAM_MODEL=deepseekv4.1-flash-1017` (koi code badlav nahi).
- `sarvam-105b-conversations` bhi chalega (roz ki chat ke liye); uske liye `SARVAM_MODEL=sarvam-105b-conversations` (code apne aap /v1 aur bina reasoning bhejta hai).

## Phase 2 (BADLAV KARNE WALA BOT) - sirf DESIGN, kuch banaya nahi. Tumhari "haan" ke bina code nahi.
Tumne kaha bot tumhare kehne par bug fix/badlav kar sake. Sidha live app ko badalne dena **khatarnak** hai (galat edit ya prompt-injection se app toot sakti hai, aur live app public repo se judi hai). Do surakshit darje:
- **2a (zero khatra, meri salah pehle ye):** chat me "Badlav request" button: tum simple Hinglish me likho ("ye button theek karo"); bot **EXACT badlav likhta hai** (kaun si file, kya purana -> kya naya, kyun) aur request ek queue me save hoti hai (PIN se). Phir wo mujhe (QC head) milti hai: mai jaanchta hu, test chalata hu, ek alag commit me lagata hu, push + live check. Bot khud kuch nahi badalta.
- **2b (zyada khatarnak, baad me, sirf tumhari alag "haan" par):** tumhari PIN-haan ke baad server GitHub par **branch + pull request** banaye (kabhi seedha main nahi), GitHub Action poore test chalaye, tum merge dabao, phir Render deploy. Niyam: sirf allowlist ki files (lab_static/*, patterns/*.md, lab/help_kb.md...); `lab_server.py` ka auth, `lab/gh.py`, `data/`, `.github/`, `render.yaml`, secrets kabhi nahi; chhota diff; har badlav ek commit (revert aasan); kill-switch env `HELP_WRITE=0`; GitHub token alag (sirf PR), key env me. Koi delete nahi. PIN wale kaam (fetch, paper bet) PIN se hi rahenge.
- Dono me bot ko **code-sakshm model** chahiye (DeepSeek Flash/Pro ya Claude); Q&A wala chhota model kaafi nahi.

## Code
`lab/help_bot.py` (PIN, lockout, cap, cache, retrieval, Sarvam call), `lab/help_faq.py`, `lab/help_kb.md` (bot ka gyaan: isse README/HANDOFF ke saath mel me rakho), `lab_static/help.js` (robot button + panel), `lab_server.py` (`/api/help/status`, `/api/help/unlock`, `/api/help`), tests `HelpBotTests`, `HelpBotSavingTests`.
Wapas: `git revert <hash>` (ya Render se `SARVAM_API_KEY` hata do: chat band ho jata hai).
