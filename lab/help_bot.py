"""Sahil Lab Help (Phase 1): sirf sawaal-jawaab. Koi data, bet, setting ya code nahi badalta.

Surakshit tareeka (user ke paise Sarvam API se katte hain):
- API key SIRF environment variable SARVAM_API_KEY se (Render dashboard). Code/commit/browser me kabhi nahi. Browser Sarvam ko seedha call nahi karta, sirf apne server ko.
- Chat sirf password (HELP_PIN, na ho to ADMIN_PIN) se khulta hai. Jaanch SERVER par hoti hai (browser ki JS badalkar bachna mumkin nahi). PIN kabhi code me nahi likha.
- 4 ank ka PIN kamzor hota hai, isliye: galat PIN 5 baar lagatar -> sabke liye 15 minute band (IP badalkar bachna mumkin na ho, isliye global); 2 second se kam gap me AI sawaal nahi;
  roz ki seema HELP_DAILY_MAX (default 80 AI jawab); sawaal 400 akshar tak; jawab ke token ki hadd. Ye sab memory me hai (Render restart par ginti shuru se).
- Sarvam se kuch bhi galat/khaali aaye to saaf message; kachcha upstream error ya key kabhi user ko nahi dikhti.

Token bachane ke 3 tareeke (user ne kaha: baar-baar ek jaise sawaal ho to zyada token na lage):
1) FAQ: aam sawaalon ke taiyar jawab (lab/help_faq.py), zero token.  2) Cache: pichle jawab (usi live sthiti me) 3 din tak.  3) Retrieval: poora gyaan nahi, sirf sawaal se mile hue hisse bhejte hain.
Reasoning band ("none"), isliye soch ke token bhi nahi lagte. FAQ/cache se aaya jawab daily seema ya gap me nahi ginta.
"""
import datetime as dt
import hashlib
import hmac
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request

from . import help_faq

KB_PATH = os.path.join(os.path.dirname(__file__), "help_kb.md")
URL_V2 = "https://api.sarvam.ai/v2/chat/completions"           # user ke test: reasoning_effort "none" SIRF /v2 par chalta hai (v1 reject karta hai)
URL_V1 = "https://api.sarvam.ai/v1/chat/completions"           # '-conversations' model sirf /v1 par (usme reasoning hota hi nahi)
DEFAULT_MODEL = "sarvam-105b"
MAX_TOKENS = 1500
MAX_Q = 400
MAX_HISTORY = 4                                                 # pichle 2 sawaal-jawab (context ke liye), kharcha kam
MAX_HIST_CHARS = 600
MAX_FAILS = 5
LOCK_SECONDS = 15 * 60
MIN_GAP = 2.0
CACHE_TTL = 3 * 86400
CACHE_MAX = 200
CACHE_SIM = 0.8                                                 # milte-julte sawaal (shabd-set ka mel) par wahi jawab
TOP_CHUNKS = 5
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
NO_KEY_MSG = "API key set nahi hai — Render dashboard me SARVAM_API_KEY set karo."
NO_PIN_MSG = "Help ka password set nahi hai — Render dashboard me HELP_PIN set karo."
UPSTREAM_MSG = "Sarvam se jawab nahi aaya, dobara try karo."

STOP = set("""kya hai hain ka ki ke me mein se ko to aur ya hota hoti hote hoga kar karo karna karu karun kare batao bata bataiye mujhe mera meri mere ye yeh wo woh ho tha the thi ek
 kaise kyun kyu kahan kab kaun kaunsa koi kuch bhi hi na nahi par pe liye wala wali wale jaise jaisa isme usme iska uska isse usse hum aap tum main mai bhai please plz ji""".split())
LIVE = {"aaj", "abhi", "kal", "parso", "today", "latest", "taza", "taaza", "current", "ab", "filhal"}     # aaj ki sthiti wale sawaal: FAQ nahi, live data ke saath AI

_lock = threading.Lock()
_state = {"fails": 0, "locked_until": 0.0, "day": "", "count": 0, "last": 0.0}
_cache = {}                                                     # key -> {"a": jawab, "t": samay, "tok": set, "live": hash}
_chunks_cache = {}


def reset_for_tests():
    with _lock:
        _state.update({"fails": 0, "locked_until": 0.0, "day": "", "count": 0, "last": 0.0})
        _cache.clear()


def _key():
    return os.environ.get("SARVAM_API_KEY", "").strip()


def _pin():
    return (os.environ.get("HELP_PIN") or os.environ.get("ADMIN_PIN") or "").strip()


def daily_max():
    try:
        return max(1, int(os.environ.get("HELP_DAILY_MAX", "80")))
    except ValueError:
        return 80


def config():
    """Kya set hai (value nahi): UI isse saaf message dikhata hai."""
    return {"key_set": bool(_key()), "pin_set": bool(_pin())}


def check_pin(pin, now=None):
    """-> (ok, message, http_status). Galat PIN ginta hai, 5 lagatar par 15 minute band."""
    now = time.time() if now is None else now
    real = _pin()
    if not real:
        return False, NO_PIN_MSG, 503
    with _lock:
        if now < _state["locked_until"]:
            wait = int(_state["locked_until"] - now) // 60 + 1
            return False, f"Bahut galat PIN lage. {wait} minute baad try karo.", 429
        if hmac.compare_digest(str(pin or "").encode(), real.encode()):
            _state["fails"] = 0
            return True, "", 200
        _state["fails"] += 1
        if _state["fails"] >= MAX_FAILS:
            _state["locked_until"] = now + LOCK_SECONDS
            _state["fails"] = 0
            return False, f"Bahut galat PIN lage. {LOCK_SECONDS // 60} minute baad try karo.", 429
        return False, "PIN galat hai.", 403


# ---------------- sawaal ko shabdon me todna ----------------
def tokens(text):
    """Chhote shabd (a-z, 0-9), stop-shabd hata kar. 009/008/fb jaise chhote bhi rakhte hain."""
    return {w for w in re.findall(r"[a-z0-9]+", str(text).lower()) if w not in STOP and (len(w) >= 3 or w.isdigit() or w in ("fb", "gb", "gl", "ds", "fd"))}


def _all_words(text):
    return set(re.findall(r"[a-z0-9]+", str(text).lower()))


def _has_live_intent(q):
    return bool(_all_words(q) & LIVE)


def faq_answer(q):
    """Taiyar jawab (zero token) ya None. Sirf non-live sawaal; ek group ke SAARE shabd hone chahiye."""
    if _has_live_intent(q):
        return None
    words = _all_words(q)
    for item in help_faq.FAQ:
        for grp in item["groups"]:
            if all(any(w == g or (len(g) >= 4 and w.startswith(g)) for w in words) for g in grp):
                return item["answer"]
    return None


# ---------------- gyaan (KB) ka retrieval ----------------
def _knowledge():
    try:
        with open(KB_PATH, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return "(app ki jaankari file nahi mili)"


def _chunks():
    """KB ko (section, line) ke tukdon me. 'Bot ke niyam' aur 'App kya hai' hamesha jate hain, baaki sawaal se mel khane par."""
    kb = _knowledge()
    h = hashlib.sha1(kb.encode()).hexdigest()
    if _chunks_cache.get("h") == h:
        return _chunks_cache["v"]
    always, items, sec = [], [], ""
    for line in kb.splitlines():
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            sec = line[3:].strip()
            continue
        if not line.strip():
            continue
        row = (sec, line.strip())
        if sec.startswith("Bot ke niyam") or sec.startswith("App kya hai"):
            always.append(row)
        else:
            items.append((sec, line.strip(), tokens(sec + " " + line)))
    _chunks_cache.update({"h": h, "v": (always, items)})
    return always, items


def knowledge_for(question):
    """Sawaal se mile hue hisse (kam token). Kuch na mile to poora gyaan (kabhi andaze se jawab na ho)."""
    always, items = _chunks()
    q = tokens(question)
    scored = []
    for i, (sec, line, tk) in enumerate(items):
        sc = sum((2 if w.isdigit() else 1) for w in q if w in tk or any(len(w) >= 4 and (t.startswith(w) or w.startswith(t)) for t in tk if len(t) >= 4))
        if sc:
            scored.append((-sc, i))
    if not scored:
        return _knowledge()
    pick = sorted(i for _, i in sorted(scored)[:TOP_CHUNKS])
    out, last = [], None
    for sec, line in always:
        if sec != last:
            out.append(f"\n## {sec}")
            last = sec
        out.append(line)
    for i in pick:
        sec, line, _ = items[i]
        if sec != last:
            out.append(f"\n## {sec}")
            last = sec
        out.append(line)
    return "\n".join(out)


def system_prompt(live="", question=""):
    s = ("Tum 'Sahil Lab Help' ho: Sahil Lab app ka madadgaar. Neeche app ki jaankari ka sawaal se juda hissa hai. Usi se, chhote saaf Hinglish me jawab do. "
         "Jawab me jo cheez neeche nahi hai, wo mat banao.\n" + knowledge_for(question))
    if live:
        s += "\n\n## Abhi ki sthiti (live, sahi maano)\n" + live
    return s


def clean_history(history):
    out = []
    for m in (history or [])[-MAX_HISTORY:]:
        if isinstance(m, dict) and m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str) and m["content"].strip():
            out.append({"role": m["role"], "content": m["content"].strip()[:MAX_HIST_CHARS]})
    return out


# ---------------- model / URL ----------------
def model_name():
    return os.environ.get("SARVAM_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def supports_none(model):
    """User ke test: reasoning_effort "none" 105b / DeepSeek Flash / Pro / Qwen par chalta hai; GLM / Kimi / 105b-conversations / Gemma4 par NAHI bhejna."""
    m = model.lower()
    return (m.startswith("sarvam-105b") and not m.endswith("-conversations")) or m.startswith("deepseek") or m.startswith("qwen")


def endpoint(model):
    return os.environ.get("SARVAM_URL", "").strip() or (URL_V1 if model.lower().endswith("-conversations") else URL_V2)


def _http_post(url, headers, payload, timeout=45):
    """Sarvam ko call. (status, dict ya None). Test me isi ko badalte hain."""
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return e.code, None
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return 0, None


def _extract(resp):
    try:
        text = resp["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None
    if not isinstance(text, str):
        return None
    if "</think>" in text:                                     # kuch model soch (think) bhi bhejte hain: sirf asli jawab
        text = text.split("</think>")[-1]
    text = text.strip()
    return text or None


# ---------------- cache ----------------
def _cache_lookup(tok, livehash, now):
    if not tok:
        return None
    best = None
    for k, v in list(_cache.items()):
        if now - v["t"] > CACHE_TTL:
            del _cache[k]
            continue
        if v["live"] != livehash:
            continue
        sim = len(tok & v["tok"]) / max(1, len(tok | v["tok"]))
        if sim >= CACHE_SIM and (best is None or sim > best[0]):
            best = (sim, v["a"])
    return best[1] if best else None


def _cache_put(tok, livehash, answer, now):
    if not tok:
        return
    key = livehash + "|" + " ".join(sorted(tok))
    _cache[key] = {"a": answer, "t": now, "tok": set(tok), "live": livehash}
    if len(_cache) > CACHE_MAX:
        for k in sorted(_cache, key=lambda x: _cache[x]["t"])[: len(_cache) - CACHE_MAX]:
            del _cache[k]


def ask(question, history=None, live="", now=None):
    """-> (answer ya None, error message ya None, http_status, via). via: faq | cache | ai. PIN pehle check ho chuka hona chahiye."""
    now = time.time() if now is None else now
    q = str(question or "").strip()
    if not q:
        return None, "Sawaal likho.", 400, None
    if len(q) > MAX_Q:
        return None, f"Sawaal chhota rakho ({MAX_Q} akshar tak).", 400, None
    key = _key()
    if not key:
        return None, NO_KEY_MSG, 503, None
    hist = clean_history(history)
    if not hist:                                               # follow-up sawaal (pichli baat par nirbhar) me FAQ/cache nahi
        a = faq_answer(q)
        if a:
            return a, None, 200, "faq"
    livehash = hashlib.sha1(live.encode()).hexdigest()[:12]
    tok = tokens(q)
    if not hist:
        with _lock:
            cached = _cache_lookup(tok, livehash, now)
        if cached:
            return cached, None, 200, "cache"
    day = dt.datetime.fromtimestamp(now, IST).date().isoformat()
    with _lock:
        if _state["day"] != day:
            _state["day"], _state["count"] = day, 0
        if _state["count"] >= daily_max():
            return None, "Aaj ki seema poori ho gayi (kharcha bachane ke liye). Kal dobara poochho.", 429, None
        if now - _state["last"] < MIN_GAP:
            return None, "Thoda ruko, phir poochho.", 429, None
        _state["last"] = now
    model = model_name()
    payload = {"model": model, "temperature": 0.2, "max_tokens": MAX_TOKENS,
               "messages": [{"role": "system", "content": system_prompt(live, q)}] + hist + [{"role": "user", "content": q}]}
    if supports_none(model):
        payload["reasoning_effort"] = "none"
    status, resp = _http_post(endpoint(model), {"Content-Type": "application/json", "api-subscription-key": key}, payload)
    ans = _extract(resp) if status == 200 and resp else None
    if not ans:
        return None, UPSTREAM_MSG, 502, None
    with _lock:
        _state["count"] += 1                                  # sirf safal AI jawab ginta hai
        if not hist:
            _cache_put(tok, livehash, ans, now)
    return ans, None, 200, "ai"
