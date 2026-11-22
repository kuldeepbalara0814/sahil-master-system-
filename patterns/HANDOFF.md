# HANDOFF: pattern sikhane ke niyam aur facts (jo bhi naya aaye, yahin jodna)

Ye file naye session/engineer ke liye hai taaki aap ko baar-baar samjhana na pade.

## Kaam ka tareeka
1. Aap ek-ek pattern sikhate ho. **Aap poora bata do tab tak main sawal nahi poochta / kuch test nahi karta.** Phir main apne shabdon me README likhta hoon aur ek-ek sawal poochta hoon. Aap ki pushti ke baad hi pattern pakka.
2. Pattern ke folder (`patterns/NNN_naam/`) me: README.md, examples.csv (har nishaan data se jaancha hua), reference pic, (zarurat par) spec.json aur Excel.
3. **Sirf wahi pattern software me jayega jo parakh me fayda dikhaye** (kachra jama nahi karna).
4. Pattern sirf **3-6 mahine** valid hai. Parakh sirf pichle 3-6 mahine par, 13 saal par nahi (jab tak aap na kaho).
5. Typing ki chhoti galtiyan (jaise "jun 2017" = Jan 2017) sandarbh se khud sudhaar lo.
6. Data aur copy Google Drive ke folder "Pattern Learning" me bhi rakhi jati hai; 5 pattern ho jayein to software me push aur Drive STATUS me "PUSH HUA".

## Game / data ke facts
- Game: FB (code me FD), GB, GL, DS. Number 00-99.
- FB GB GL tarikh wale din 12 baje se pehle; DS agli subah 5-6 baje. **DS pichli tarikh ki line me likhte hain.** Galat likhne par har pattern bigad jata hai.
- Mahine ke aakhri din ki chhuti. Isse game ek din aage-peeche (vibration). Mahine ke aas-paas +-1 din ka farak pass maana jata hai.
- Gap Excel jaise ginte hain: row ki duri. Chhuti ki row nahi hoti.
- Excel me rang sirf aankhon ke liye; ek jaisa rang = ek dusre se jodidaar. Kaala rang nahi (ank chhup jata hai).

## Shabd
Rashi, cross, jodi, half jodi, gap: `GLOSSARY.md`. Mapping/naksha pattern: `002_mapping_pattern/README.md`.

## Software me pattern (Pattern Scan tab)
- `lab/scanner.py`: har sikhaya hua pattern ek `scan_xxx(rows, asof)` hai aur `PATTERNS` list me ek entry. **Naya pattern sikhaya to yahin jodo** (scan function + PATTERNS + SCANNERS), phir wo apne aap roz chalega.
- Roz subah data aate hi `lab/update.py` (GitHub Action) scan chalata hai aur `data/patterns_today.json` banata hai. App me tab **Pattern Scan** hai: aaj kya ban raha hai, saaf rang wala chart, Excel download, aur **manual "Script abhi chalao"** button (galti aaye to wahi dikhti hai).
- Har pattern ko apna naam milta hai (Naksha-Hathi-44, Copy-Sher-50) taaki mix na ho. `lab/scan_view.py` chart aur Excel banata hai.
- 001 Jodi-Copy aur 002 Naksha scan chalte hain. 002 abhi 'Naksha' ke naam se same/palat links ka milan dekhta hai (aap ke pic ke design ko poora nahi pakadta, sudhar baaki).
