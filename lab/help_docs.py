"""Sahil Lab Help: docs (README / HANDOFF / GLOSSARY / pattern README) me se jawab dhundhna - bina AI ke (hybrid ka 'docs' hissa).

Chhote tukde (chunk) banakar sawaal se milaate hain (IDF wala shabd-mel). Do kaam:
- best(): jawab docs me bahut saaf likha ho (kai shabd mile, ek tukda saaf jeeta) to wahi tukda seedha (zero token).
- context(): warna Sarvam ko sirf mile hue 4-5 tukde dete hain (poora gyaan nahi), taaki jawab docs par tike aur token kam lagein.
Live sthiti (aaj ke number) docs me nahi hoti, isliye wo sawaal yahan se nahi, AI + live data se jate hain (help_bot).
"""
import glob
import hashlib
import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_CHUNK = 900            # ek tukde ke akshar
SHOW_MAX = 700             # seedha dikhane par kitne akshar
MIN_MATCHED = 2            # kam se kam itne alag shabd mile
MIN_COVER = 0.85           # sawaal ke (docs me maujood) shabdon me se itne ka mel
MIN_COVER_CURATED = 0.65   # help_kb ke saaf tukde ke liye thoda kam (agar 3+ shabd mile)
MIN_LEAD = 1.15            # tie ke baahar ke sabse achhe tukde se itna aage
TIE = 0.97                 # itne ke andar ke number 'barabar' maane jate hain (ek hi baat KB, README aur HANDOFF teeno me hoti hai)
STOP = set("""kya hai hain ka ki ke me mein se ko to aur ya hota hoti hote hoga kar karo karna karu karun kare batao bata bataiye mujhe mera meri mere ye yeh wo woh ho tha the thi ek
 kaise kyun kyu kahan kab kaun kaunsa koi kuch bhi hi na nahi par pe liye wala wali wale jaise jaisa isme usme iska uska isse usse hum aap tum main mai bhai please plz ji
 fark matlab mtlb samjhao samjha samjhana kitna kitne kitni banta banti bana baare baat sab saari saare aati aata aate jata jati jate dikhta dikhti dikhte""".split())
_cache = {}


def tokens(text):
    """Chhote shabd (a-z, 0-9), stop-shabd hata kar. 009/008/fb jaise chhote bhi rakhte hain."""
    return {w for w in re.findall(r"[a-z0-9]+", str(text).lower()) if w not in STOP and (len(w) >= 3 or w.isdigit() or w in ("fb", "gb", "gl", "ds", "fd"))}


def clean(text):
    t = re.sub(r"\*\*|`", "", text)
    t = re.sub(r"^\s*[-*]\s+", "", t, flags=re.M)
    return re.sub(r"[ \t]+", " ", t).strip()


def trim(text, n=SHOW_MAX):
    t = clean(text)
    if len(t) <= n:
        return t
    cut = t[:n]
    k = max(cut.rfind(". "), cut.rfind("\n"))
    return (cut[:k + 1] if k > n * 0.5 else cut.rsplit(" ", 1)[0]) + " ..."


def _split_long(label, text):
    out, buf = [], ""
    for para in re.split(r"\n\s*\n|\n(?=\s*[-*] )", text):
        if buf and len(buf) + len(para) > MAX_CHUNK:
            out.append(buf)
            buf = ""
        buf += ("\n" if buf else "") + para
    if buf.strip():
        out.append(buf)
    return [(label, p.strip()) for p in out if p.strip()]


def _chunks_for(path):
    rel = os.path.relpath(path, ROOT)
    base = rel.replace("patterns/", "").replace("/README.md", " README").replace(".md", "")
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return []
    out = []
    if rel.endswith("HANDOFF.md"):                               # "20. **...**" se shuru hone wala har item ek tukda
        cur, num = [], None
        for ln in lines + ["0. END"]:
            m = re.match(r"^(\d+)\. ", ln)
            if m:
                if cur and num:
                    out.append((f"HANDOFF item {num}", "\n".join(cur)))
                num, cur = m.group(1), [ln[len(m.group(0)):]]
            elif num is not None and not ln.startswith("## "):
                cur.append(ln)
        return out
    if rel.endswith("help_kb.md"):                               # har bullet ek tukda; 'Bot ke niyam' sirf AI ke liye (jawab nahi)
        sec = ""
        for ln in lines:
            if ln.startswith("## "):
                sec = ln[3:].strip()
            elif ln.strip() and not ln.startswith("#") and not sec.startswith("Bot ke niyam"):
                out.append((f"App jaankari - {sec}", ln.strip()))
        return out
    sec, buf = "shuruaat", []
    for ln in lines + ["## END"]:
        if ln.startswith("## ") or ln.startswith("# "):
            if buf and "\n".join(buf).strip():
                out += _split_long(f"{base} - {sec}", "\n".join(buf))
            sec, buf = ln.lstrip("# ").strip(), []
        else:
            buf.append(ln)
    return out


def _paths():
    ps = [os.path.join(ROOT, "lab", "help_kb.md"), os.path.join(ROOT, "patterns", "README.md"), os.path.join(ROOT, "patterns", "GLOSSARY.md"),
          os.path.join(ROOT, "patterns", "HANDOFF.md"), os.path.join(ROOT, "patterns", "AI_REBUILD_GUIDE.md")]
    ps += sorted(glob.glob(os.path.join(ROOT, "patterns", "*", "README.md")))
    return [p for p in ps if os.path.exists(p)]


def index():
    """Tukde + idf (file badlne par apne aap dobara). -> {'chunks': [...], 'idf': {shabd: wazan}, 'vocab': set}"""
    sig = hashlib.sha1("|".join(f"{p}:{os.path.getmtime(p):.0f}:{os.path.getsize(p)}" for p in _paths()).encode()).hexdigest()
    if _cache.get("sig") == sig:
        return _cache["idx"]
    chunks = []
    for p in _paths():
        for label, text in _chunks_for(p):
            tk = tokens(label + " " + text)
            if len(clean(text)) >= 25 and tk:
                chunks.append({"label": label, "text": text, "tok": tk, "long": {t for t in tk if len(t) >= 4}})
    df = {}
    for c in chunks:
        for t in c["tok"]:
            df[t] = df.get(t, 0) + 1
    n = len(chunks)
    idx = {"chunks": chunks, "df": df, "n": n}
    _cache.update({"sig": sig, "idx": idx})
    return idx


def _match(w, c):
    if w in c["tok"]:
        return True
    if len(w) >= 4:
        return any(t.startswith(w) or w.startswith(t) for t in c["long"])
    return False


def _rank(question):
    """-> (scores [(score, chunk, matched_set)] bade se chhota, known_idf_total, known_tokens). Docs me na milne wale shabd (typo) ginti me nahi."""
    idx = index()
    n = max(1, idx["n"])
    q = tokens(question)
    idf, known = {}, set()
    for w in q:
        dfw = sum(1 for c in idx["chunks"] if _match(w, c))
        if dfw:
            idf[w] = math.log(1 + n / dfw)
            known.add(w)
    out = []
    for c in idx["chunks"]:
        m = {w for w in known if _match(w, c)}
        if m:
            out.append((sum(idf[w] for w in m), c, m))
    out.sort(key=lambda x: -x[0])
    return out, sum(idf.values()), known


def best(question):
    """Seedha docs jawab: {'text', 'label'} ya None (agar saaf na ho to AI ko)."""
    ranked, total, known = _rank(question)
    if len(known) < MIN_MATCHED or not ranked or total <= 0:
        return None
    top_s = ranked[0][0]
    ties = [x for x in ranked if x[0] >= TIE * top_s]
    curated = [x for x in ties if x[1]["label"].startswith("App jaankari")]
    if curated:
        pick = curated[0]                                        # ek hi baat kai jagah ho to help_kb wala (saaf, chhota) tukda
    elif len(ties) == 1:
        pick = ties[0]
    else:
        return None                                              # kai alag tukde barabar: AI mila-kar samjhaye
    score, chunk, matched = pick
    cov = score / total
    ok = len(matched) >= MIN_MATCHED and (cov >= MIN_COVER or (bool(curated) and cov >= MIN_COVER_CURATED and len(matched) >= 3))
    rest = [x[0] for x in ranked if x not in ties]
    if not ok or (rest and score < MIN_LEAD * rest[0]):
        return None
    return {"text": trim(chunk["text"]), "label": chunk["label"]}


def context(question, k=5, each=600):
    """AI ke liye: sawaal se mile hue top-k tukde ('[label] text') ek string me. Kuch na mile to ''."""
    ranked, _, _ = _rank(question)
    return "\n".join(f"[{c['label']}] {trim(c['text'], each)}" for _, c, _ in ranked[:k])
