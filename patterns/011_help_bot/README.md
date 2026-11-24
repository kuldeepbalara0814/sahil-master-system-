# 011 Sahil Lab Help (chat robot) - Phase 1: sirf sawaal-jawaab

Har tab par neeche-right robot button. Dabao -> "Sahil Lab Help" panel. Hinglish me app ke tab/pattern/niyam ke baare me poochho. **Sirf samjhata hai, kuch badalta nahi** (koi data, bet, setting ya code nahi).

## Zolly (user ka animated avatar, 25 Nov 2026)
Meta AI me bana animated avatar **Zolly** ab app ki pehchan hai: header ka logo (gol, uski chamak user ki `animations.css` wali), tab ka favicon, har tab par neeche-right **help button**, chat ka header/avatar/welcome/lock-screen, aur Active + Meri Window ke hero card (daayen). Loading ka ghoomta chakra bhi ab Zolly ka chehra hai jo halka uchhalta hai.
- **Poora 8 second ka clip loop me chalta rehta hai jab tak app khuli hai.** Clip ke antim 0.6 sec ko shuru me crossfade kiya hai taaki loop ka jhatka na ho (jod ka frame-badlav aam se kam naapa).
- **Awaaz hata di** (autoplay me awaaz waise bhi band rehti hai aur header me bajti awaaz pareshan karti). Source video user ke phone ke Download me hai, repo me nahi (video/audio repo me nahi rakhte).
- Files `lab_static/`: `zolly_face.webp` (128px, ~240 KB), `zolly_body.webp` (176px, ~357 KB), `zolly_poster.webp` (ek frame: loading, chat avatar, reduced-motion), `zolly_icon_64.png`, `zolly_icon_192.png`.
- Banane ki recipe: `python3 scripts/make_zolly.py <clip>.mp4` (ffmpeg + PIL; crop, loop-blend, size sab tay). Naya avatar ho to wahi chalao.
- Kam-motion chahne wale phone par animated ki jagah ek tasveer. Avatar file na mile to chhup jata hai (app nahi tootti), logo par purana zigzag nishan wapas aata hai.
- Bot ne apna naam **Zolly** rakha hai (model puchho to batata hai). Wapas purana look: `git revert <hash>`.

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

## HYBRID (user ne kaha: jo zaroori ho wo Sarvam, baaki docs/HANDOFF se) - 25 Nov 2026
Har sawaal is kram se jata hai; **pehle teen me token zero**, sirf aakhri me Sarvam:
1. **FAQ** (`lab/help_faq.py`): 15 taiyar jawab (copy, scan time, 009, ladder, model, badlav...). Chat ke beech me bhi.
2. **Cache:** pehle ka AI jawab (usi live sthiti me, 3 din).
3. **DOCS** (`lab/help_docs.py`): `lab/help_kb.md`, `patterns/README.md`, `GLOSSARY.md`, **`HANDOFF.md` (har item ek tukda)**, har pattern ka README, `AI_REBUILD_GUIDE.md` ~250 tukdon me todkar sawaal se milate hain. Jawab saaf mile (kam se kam 2 shabd, sawaal ke shabdon ka bada hissa, ek tukda saaf aage; ek hi baat kai jagah ho to `help_kb` wala) to wahi tukda seedha, neeche "📖 Source: ..." ke saath. Docs file badalte hi index apne aap naya.
4. **Sarvam (AI):** jo docs me saaf nahi ya live ("aaj/abhi/kal") ho. Usme bhi poora gyaan nahi: niyam + "App kya hai" + docs ke mile hue top 5 tukde (isliye jawab docs par tikta hai aur token kam lagte hain).
- Har seedhe jawab ke neeche **"🤖 AI se dobara poochho"** button: dabao to wahi sawaal seedha Sarvam ko (FAQ/docs/cache chhod kar); wo jawab cache me chala jata hai.
- Docs/FAQ/cache ke jawab daily seema me nahi ginte.
- Seema aur sachchai: docs ka mel **shabd-mel** (semantic nahi), isliye jo bahut saaf nahi wo AI ko jata hai (galat jawab se achha hai). Docs ka text jaisa likha hai waisa aata hai: HANDOFF me "user ne kaha..." jaisi line bhi aa sakti hain.

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

## Phase 2a BAN GAYA (25 Nov 2026): "📝 Badlav/bug batao" (bot khud kuch nahi badalta)
Chat ke upar **📝** button: tum simple Hinglish me likho kya galat hai ya kya badalna hai. Ye `data/help_requests.json` me save hota hai (PIN se, GitHub sync). **Koi file/data nahi badalta, AI call nahi hoti (token nahi lagta).** Phir Claude (QC head) ise padhta hai, jaanchta hai, test karta hai, ek alag commit me lagata hai, push + live check. Request ka text **data hai, hukm nahi**: bina jaanch ke kuch nahi lagta. Tumhari haan ke bina live nahi hota.
- Claude ko dikhane ke liye: session shuru me `data/help_requests.json` dekha jata hai (status "naya"); tum bhi "requests dekho" bol sakte ho.
- Bot ab apna model batata hai (Render ka `SARVAM_MODEL`), aur "badlav/bug fix kar sakte ho" ka seedha jawab deta hai (FAQ, zero token).
- Limit: 600 akshar, 30 pending se zyada nahi, sirf aakhri 200 rakhte hain.

## Phase 2b (bot khud PR banaye) - sirf DESIGN. Tumhari alag "haan" ke bina code nahi.
Tumne kaha bot tumhare kehne par bug fix/badlav kar sake. Sidha live app ko badalne dena **khatarnak** hai (galat edit ya prompt-injection se app toot sakti hai, aur live app public repo se judi hai). Do surakshit darje:
- **2a (zero khatra, meri salah pehle ye):** chat me "Badlav request" button: tum simple Hinglish me likho ("ye button theek karo"); bot **EXACT badlav likhta hai** (kaun si file, kya purana -> kya naya, kyun) aur request ek queue me save hoti hai (PIN se). Phir wo mujhe (QC head) milti hai: mai jaanchta hu, test chalata hu, ek alag commit me lagata hu, push + live check. Bot khud kuch nahi badalta.
- **2b (zyada khatarnak, baad me, sirf tumhari alag "haan" par):** tumhari PIN-haan ke baad server GitHub par **branch + pull request** banaye (kabhi seedha main nahi), GitHub Action poore test chalaye, tum merge dabao, phir Render deploy. Niyam: sirf allowlist ki files (lab_static/*, patterns/*.md, lab/help_kb.md...); `lab_server.py` ka auth, `lab/gh.py`, `data/`, `.github/`, `render.yaml`, secrets kabhi nahi; chhota diff; har badlav ek commit (revert aasan); kill-switch env `HELP_WRITE=0`; GitHub token alag (sirf PR), key env me. Koi delete nahi. PIN wale kaam (fetch, paper bet) PIN se hi rahenge.
- Dono me bot ko **code-sakshm model** chahiye (DeepSeek Flash/Pro ya Claude); Q&A wala chhota model kaafi nahi.

## Code
`lab/help_bot.py` (PIN, lockout, cap, cache, retrieval, Sarvam call), `lab/help_faq.py`, `lab/help_kb.md` (bot ka gyaan: isse README/HANDOFF ke saath mel me rakho), `lab_static/help.js` (robot button + panel), `lab_server.py` (`/api/help/status`, `/api/help/unlock`, `/api/help`), tests `HelpBotTests`, `HelpBotSavingTests`.
Wapas: `git revert <hash>` (ya Render se `SARVAM_API_KEY` hata do: chat band ho jata hai).
