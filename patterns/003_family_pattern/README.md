# 003 Family pattern (rashi family ki chain)

Aap ne (2026-11-22) Telegram se save ki hui pic se sikhaya. Pic: `ref_screenshot.jpg`. Ye **main ne jaisa samjha waisa** likha hai, aap ke jawab ke baad (6 sawal). Aap ki **pushti baaki** hai. Software me **abhi nahi** daala (Pattern Scan me 003 nahi hai). Is pattern ka Excel nahi banaya (aap ne mana kiya).

## Pic me kya hai (data se milaya, examples.csv me har cell)
- Ek hi mahina: **Nov 2026**. Pic ki row = Nov ki tarikh + 32 (row 35 = 3 Nov, row 50 = 18 Nov). Pic 18 Nov ko li gayi: sirf FB 44 aaya tha, baaki GB/GL/DS narangi khaali.
- Rang number ke nahi, **rashi (family)** ke hain:
  - Peela, chain 1 (02 rashi): 4 Nov GL 02, 6 Nov FB 75, 7 Nov GL 57. **Ulta** padha gaya.
  - Narangi, chain 1 (24 rashi): 7 Nov GB 24, 8 Nov DS 24, 10 Nov GL 29.
  - Peela, chain 2 (03 rashi): 14 Nov DS 85, 15 Nov GB 85, 17 Nov DS 80.
  - Narangi, chain 2 (02 rashi): 15 Nov DS 57, 16 Nov GB 25, aur 18 Nov GB/GL/DS khaali narangi = 3rd step ka andaza.

## Shabd (aap ke)
- **Rashi:** number ke har ank me 5 jodne se bani family. 8 number ki (jaise 02: 02 07 20 25 52 57 70 75) aur jodi rashi, 4 number ki (11: 11 16 61 66). Saari list `GLOSSARY.md` me.
- **Standing:** ek hi game column me agle din (GB se GB, DS se DS...). Kal DS 76, aaj DS 67 = family ka standing repeat. Wahi number dobara = standing repeat.
- **Cross:** agle din doosre column me (kal DS, aaj GL). Wahi number doosre column me = cross repeat.
- **Cross sirf aankh ka naam hai.** Machine ke liye ye "agle din, koi bhi column" hai. Cross zaroori nahi, standing bhi chalta hai.
- **Step 1, 2, 3:** sirf **ek hi (current) mahine** ke steps. Do alag mahine me same design ko step nahi bolte, wo mapping/naksha (002) hai.
- **Seedha** = date 1 se 30 ki taraf niche chalta design. **Ulta** = date 30 se 1 ki taraf upar chalta design.

## Design (jab pattern bana kehte ho)
Ek rashi ke 3 cell, teen row me: pehla, uske agle din (ya pichle din, ulta me) doosra, phir ek din chhodkar teesra.
- Seedha: din 0, +1, +3. Ulta (upar se neeche waqt me): din d, d+2, d+3 (copy pattern ke ulta shape jaisa).
- Chaaron chain isi design ki hain, bas rashi alag (24, 02, 03, 02). Mahine ki 4 saaf copy par har chain ko alag dekho to naksha same dikhega: same duri, same design, apni apni rashi.
- **Agar step 1 aur step 2 kisi design me bane hain to step 3 usi design me aayega.**
- Teeno cell wali chain sirf **pehchan** hai. 3rd step aa gaya to wo "haath se nikal gaya". Khelna 3rd step **se pehle**, sirf 2 step dekh kar hota hai.

## Khelna (3rd step ke din)
1. **Poori family**: 02 ki chain me 02 07 20 25 52 57 70 75 (8 jodi).
2. **Zyada paise sirf do location par**: 2 step ke **neeche ka standing column**. Narangi 02 chain (DS 57, GB 25): GB aur DS me zyada, FB aur GL me halka. Halka isliye ki banane wala kabhi pehle ya baad me de jata hai (same location par bahut log pakad le to us game par load zyada hota hai).
3. Chaaron khano (FB GB GL DS) me khelna hota hai. Ye ek hi company ke 4 window hain.

## Pass / fail
- 3rd step ke **din** family ka **koi bhi number kisi bhi game me** aaya = PASS. Us din nahi aaya = FAIL.
- Design wale location par aaya = **with location**. Doosre location par aaya = **out of location (variation)**. Dono PASS.
- Jodi rashi (4 number) bhi is pattern me ginte hain, par unka hissa kam hai: 8-number wali rashi ~90%, jodi rashi ~10% (mahine me ek-do baar), baaki family wahi rehti hai.
- "2 pass, 3 fail, phir fail" aap ka ek **idea** tha, niyam nahi. Ise niyam nahi maana.

## Mera check (pichle 1 saal, 21 Nov 2025 se 21 Nov 2026), sirf "bante hain ya nahi" ke liye
Design: koi rashi din d aur d+1 (ya d+2) par aaye, phir din d+3 par wahi rashi aaye = PASS.
- Har mahine **45 se 63** design bante hain. 8-number rashi me 556 (88%), jodi rashi me 75 (12%), aap ke 90/10 se milta hai.
- 3rd step aaya: 8-number me 166/556 = **29.9%** (random 28.4%), jodi rashi me 13/75 = **17.3%** (random 15.1%). Random jaisa.
- **Location ka fayda nahi dikha:** step wale column me 8.4%, baaki columns me 9.5% (random 8%). Pass me se 88 location wale column me aaye, 78 sirf out of location.
- Pic ki chaar chain me 3rd step ka column step wale column me 3 baar mila (peela 03, peela 02, narangi 02 ka 18 Nov: GB 57, DS 70), ek baar nahi (narangi 24: GL 29).
- Pic ki narangi 02 chain ka 18 Nov wala 3rd step **PASS** hua (with location, GB aur DS).

## Kaun se design khelte ho (Sawal 7, aap ka jawab)
- Pic me sirf 4 chain rang ki gayi thi **aap ko dikhane aur sikhane ke liye**. Isi design ke jitne bhi bane wo sab khel sakte hain.
- **Paper trading me har pattern jo lage wahi khela jayega.** Machine ka kaam hai ye dekhna ki kaun sa pattern zyada pass ho raha hai aur kaun sa kam; tabhi graph banega. Software jitna zyada sikhaya jayega utna zyada pakadna seekhega.
- Isliye machine ka dimaag sirf unhi pattern tak nahi rahega jo ab tak sikhaye gaye, wo alag-alag tareeke se tezi se naye pattern bhi try karega (jab aap kahoge).

## Jab location saaf na ho (Sawal 8, aap ka jawab)
- Agar ek din me family ke kai cell aa jayen ya ek se zyada jagah same design ban raha ho, to **software location tay nahi karega.** Wo sirf pattern bata kar **mark laga dega** ki "ek se zyada jagah ban raha hai".
- Phir aap **khud aankh se manual dekh kar** tay karoge ki kahan khelna hai. Aap README me baad me notes jod/badal sakte ho; jaise-jaise baat dimaag me aaye, time aur halat ke saath saaf karte rahenge.

## Paper trading me paise (Sawal 9, aap ka jawab)
- **Location saaf nahi / bina location:** family ke har number par **10 Rs**, chaaron game me.
- **Location saaf ho:** location wale game me har number par **20 Rs (2 guna)**, baaki game me 10 Rs.
- Ye sirf **paper trading** hai taaki software majboot bane. Asli paise se khelna nahi.

## Software me kaise dikhana hai (aap ka kehna)
- **Index:** pattern ka naam (Family pattern) index me ho. Naam par click karo to jitne family pattern **abhi chal rahe hain** sab dikhen.
- **Ek hi mahine me family pattern kai ek saath bante hain.** Har ek ke liye us **mahine ki sheet ki alag copy**, har copy me ek pattern **alag rang** me. Saari copy ek image me jud sakti hain.
- **Rang koi bhi**, bas **niche ka ank saaf dikhe** (rang par kaala ank) aur pattern saaf dikhe. **Tarikh, mahina aur saal saaf likha ho.** Zarurat ho to remark.
- **Jitne bane ya shuru huye sab dikhao.** Jab ek se zyada jagah ban raha ho to location tay mat karo, sirf mark karo; aap khud dekh kar tay karoge.
- Aap koi pattern par click kar ke likh sakte ho ki kis location par kaun sa number khela.

## Family pattern ka poora mahina (aap ka kehna, 2026-11-22 raat)
- Card me "Kholo" dabane par **poora mahina** dikhta hai, **har rashi family alag rang** me (15 rang, legend ke saath). Is pattern ke cell moti safed border me, 3rd step gulabi "?".
- **"Ye kaise bana":** step 1, step 2, kaun sa design (din 0, +1, +3) aur is mahine wo rashi kin-kin dino me aayi (poori list), taaki pata chale ki ye design kaise banta hai.
- Kisi family ke rang par dabao to sirf wahi family dikhti hai. "Sirf is pattern ki family" bhi chun sakte ho. Excel download me bhi wahi poora mahina.
- Udaharan: Family-Titli-55 (24 rashi, 47 47 47): 19 Nov GB 47, DS 47; 20 Nov GL 47; 3rd step 22 Nov.

## Facts (HANDOFF.md me bhi)
- Ye design tabhi kaam kare jab DS ko pichle din ki line me likha ho (DS agli subah ka). Time: FB 6:15-6:30 pm, GB 10-10:15 pm, GL 12-12:15 am, DS 5:20-5:40 am.
- Mahine ke aakhri din chhuti se ek din aage-peeche (vibration). Mahine ke aas-paas +-1 din pass maana jata hai.

## Abhi baaki
Aap ne jo bataya wo sab likh diya. Parakh (3-6 mahine, aage ke din par) aur aap ki pushti baaki hai. Pushti ke baad hi software me aayega.
