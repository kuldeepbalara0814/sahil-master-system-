# 014 Pehredaar (safeguard) aur madad wale tools  (25 Nov 2026, user: "git par push ke time safe rakhe, galat chij ko roke")

## Kya rokta hai (`scripts/safeguard.py`)
- **Record:** results.csv, ds_1966_2012.csv, lifetime_record.txt ki koi purani line badle ya hate; data file delete ho.
- **Chhupi cheez:** key, token, private key, PIN seedha likha; `.env`, `*.pem`, ssh key jaisi file. (Value kabhi print nahi hoti.)
- **Tuta code:** Python compile, JavaScript, JSON/YAML, ruff (sirf asli bug wale niyam), data jaanch, saare tests.
- 2 MB se badi file. App me mana kiya hua shabd aaye to chetavni.
- **Force push** aur main branch delete (`.githooks/pre-push`).

## Kahan chalta hai (3 parat)
1. **Push se pehle** (jis clone se push hota hai): `git config core.hooksPath .githooks` (clone ke baad ek baar).
2. **GitHub** (`code-tests`): pehredaar, Gitleaks (poori history), tests, Playwright (asli browser, phone jaisi screen).
3. **Render:** `render.yaml` `autoDeployTrigger: checksPass` -> tests fail hon to naya code live nahi jata. (Dashboard me bhi: Settings -> Auto-Deploy -> "After CI Checks Pass".)
Roz wali data Action me record-pehredaar: fetcher ki galti se purana record badla to commit nahi hota.

**Dhyan:** parat 2 tak galat commit GitHub par pahunch sakta hai agar kisi ne hook ke bina push kiya; tab Render use deploy nahi karta aur email aati hai.

Jaanbujh kar record sudharna ho: `ALLOW_DATA_EDIT=1 git push ...`. Tests chhodne (aapat me): `SKIP_TESTS=1`.

## Aur tools
- **Ruff** (`ruff.toml`), **Gitleaks** (CI me, checksum ke saath), **Playwright** (`tests/ui_smoke.py`), **Dependabot** (`.github/dependabot.yml`).
- **healthchecks.io** (`lab/health.py`): account par check banao (Period 12 ghante, Grace 3 ghante), ping URL ko Render env `HEALTHCHECK_URL` aur GitHub secret `HEALTHCHECK_URL` me daalo. URL repo/chat me nahi.
