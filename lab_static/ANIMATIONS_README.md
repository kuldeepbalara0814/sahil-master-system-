# Sahil Lab — Animations (25 Nov 2026)

Teeno animation, halki aur professional. Sirf animation hai — koi rang, layout,
data, ya logic nahi badalti. Rang theme.css ke variables se (magenta `--mg`,
peacock-blue `--cy`), NEON theme se mel khata hai.

## Kya hai

1. **Thinking dots** — teen dot (magenta, peacock-blue, safed), baari-baari
   uchhalte hue. Dikhta hai jab app soch raha ho:
   - Active tab: "Hit map dekh raha hoon..." wali load line
   - "Abhi scan karo" button dabane par: "Scan chal raha hai..." ke saath
2. **Excited (PASS)** — jab koi pattern PASS ho, uska card halka pop karta hai
   + halki magenta glow, aur PASS badge halka bounce karta hai. Ek baar,
   ~0.5 sec, phir normal. Card dobara render hone par phir chalega.
3. **Zigzag line** — Active tab ke "AAJ KA SAAR" hero ke neeche zigzag line:
   pehle left se right draw hokar aati hai, phir dashes zigzag par behti
   rehti hain. Logo wali zigzag (M3 17l6-6 4 4 8-8) se mel khata motif hai.

## Files

- `lab_static/animations.css` (NAYI) — teeno animation + keyframes.
  Alag file hai, taaki hatana aasan ho.
- `lab_static/index.html` (1 line) — `animations.css` ka `<link>` theme.css
  ke baad.
- `lab_static/tabs_active.js` (2 lines) — do jagah `.spin` ki jagah
  `.think` (3 x `<i>` ke saath): hit-load line aur scan button ka busy state.
  Baaki `.spin` jagah (dusri "Load..." line) jaise the waise hi hain.

## Wapas kaise hataye

- Aasan: `index.html` se `animations.css` wali line hata do — purana look
  wapas, `.think` wali jagah par dot dikhenge nahi (class bina CSS ke khaali
  span hai), `.spin` wapas lane ke liye `tabs_active.js` ki 2 line wapas
  badlo.
- Poora: `git revert <is commit ka hash>`.

## Test

- 13 tab kholo — 0 JS error.
- Active tab: hero ke neeche zigzag draw hokar behti dikhni chahiye.
- "Abhi scan karo" dabao — button me teen dot uchhalte dikhne chahiye.
- PASS card aane par ek halka pop + glow dikhna chahiye.
- `prefers-reduced-motion` wale user ke liye animation band rehti hai,
  zigzag line phir bhi dikhti hai.
