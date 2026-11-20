"""Aap ki bhasha (Hinglish) me likha idea -> backtest wala spec.

Ye machine-learning nahi, seedhe shabdon ke niyam hain, isliye har baar ek hi jawab aata hai aur
'maine ye samjha' saaf dikhta hai. Galat samjha ho to Lab ka form theek karke dobara test kar sakte ho.
Naam: FB = FD (Faridabad), GB, GL (GA bhi), DS.
"""
import re

from . import backtest

GAME_WORDS = {
    "fb": "FD", "fd": "FD", "faridabad": "FD", "faridabaad": "FD", "frbd": "FD", "faribad": "FD",
    "gb": "GB", "ghaziabad": "GB", "gaziabad": "GB", "gzbd": "GB", "ghazibad": "GB",
    "gl": "GL", "ga": "GL", "gali": "GL", "gaali": "GL", "galli": "GL",
    "ds": "DS", "desawar": "DS", "disawar": "DS", "dsawar": "DS", "dswr": "DS", "deshawar": "DS", "dishawar": "DS"}
NAME = {"FD": "FB", "GB": "GB", "GL": "GL", "DS": "DS"}                 # screen par FB
LAG1 = {"kal", "kl", "yesterday", "pichle", "pichhle", "pichla", "pichhla"}
LAG2 = {"parso", "parson"}
LAG0 = {"aaj", "aj", "usi", "ussi", "same", "today"}
CONNECT = {"to", "toh", "tab", "phir", "fir", "uske", "iske", "tabhi"}
VERBS = {"lagao", "lagana", "lagayo", "lagaye", "lagaen", "lagega", "khelo", "khelna", "play", "bet", "lage", "lagaana"}
JOIN = {"aur", "ya", "dono", "teeno", "me", "mein", "par", "pe", "ka", "ki", "ke", "se", "wale"}
WEEK = {"somvar": 0, "monday": 0, "mon": 0, "mangal": 1, "mangalwar": 1, "tuesday": 1, "budh": 2, "budhwar": 2, "wednesday": 2,
        "guru": 3, "guruwar": 3, "brihaspati": 3, "thursday": 3, "shukra": 4, "shukrawar": 4, "friday": 4,
        "shani": 5, "shaniwar": 5, "saturday": 5, "ravi": 6, "ravivar": 6, "itwar": 6, "sunday": 6}
for _b, _i in (("som", 0), ("mangal", 1), ("budh", 2), ("guru", 3), ("shukra", 4), ("shani", 5), ("ravi", 6)):
    for _suf in ("var", "war", "vaar", "waar"):
        WEEK[_b + _suf] = _i
OPS = {"palat": "palat", "ulta": "palat", "palta": "palat", "reverse": "palat",
       "wahi": "same", "same": "same", "seedha": "same", "khud": "same",
       "family": "family", "rashi": "family", "parivar": "family"}
DOST = {"dost", "dosto", "friend", "friends", "saathi", "sathi", "dosti"}
HOT = {"hot", "garam", "frequent"}
COLD = {"cold", "thanda", "overdue"}
FILLER = set("""me mein par pe ka ki ke ko se jo aaya aaye aata aati nikla niklega nikle result number numbers lagao lagana lagayo
 aur ya to toh jab agar phir fir hai ho hoga hogi wale wala wali uska uski uske din dino mahine mahina baar top agle agla next uske iske
 ek do teen char paanch dono teeno sabhi sab games game khelo bet play lage lagega dost friends saathi tab tabhi kuch bhi
 hi bas sirf jaise matlab yani yaani mera idea ye wo us is isme usme unka inka""".split())
MAXTOP = 40


def _tokens(text):
    t = text.lower().replace("−", "-").replace("–", "-")
    t = re.sub(r"[,;:()\[\]'\"।]", " ", t)
    return re.findall(r"[+\-]\d+|\d+|[a-z]+", t)


def _is_num(tok):
    return tok.isdigit() and 0 <= int(tok) <= 99


def parse(text):
    """-> {ok, spec, explain, ignored, warnings, error}"""
    tk = _tokens(text)
    if not tk:
        return {"ok": False, "error": "Kuch likha nahi. Upar se koi example dabao ya apna idea likho."}
    used = [False] * len(tk)

    def mark(*idx):
        for i in idx:
            if 0 <= i < len(tk):
                used[i] = True

    # ---- game mentions aur unka lag ----
    ments = []
    for p, w in enumerate(tk):
        if w in GAME_WORDS:
            lag, lp = None, None
            j = p - 1
            while j >= 0 and p - j <= 4 and tk[j] not in GAME_WORDS:
                if tk[j] in LAG1:
                    lag, lp = 1, j
                    break
                if tk[j] in LAG2:
                    lag, lp = 2, j
                    break
                if tk[j] in LAG0:
                    lag, lp = 0, j
                    break
                if tk[j] == "pehle" and j >= 2 and tk[j - 1] == "din" and _is_num(tk[j - 2]) and int(tk[j - 2]) <= backtest.MAX_LAG:
                    lag, lp = int(tk[j - 2]), j
                    break
                j -= 1
            ments.append({"p": p, "game": GAME_WORDS[w], "lag": lag, "lp": lp})
            mark(p)
            if lp is not None:
                mark(lp)
    # "N din pehle" ke baad ke game ke liye: 'N din pehle GB'
    for p in range(len(tk) - 2):
        if _is_num(tk[p]) and tk[p + 1] == "din" and tk[p + 2] in ("pehle", "purane", "peeche", "piche"):
            mark(p, p + 1, p + 2)
    for m in ments:                              # 'GB 2 din pehle' jaisa order
        k = m["p"] + 1
        if m["lag"] is None and k + 2 < len(tk) and _is_num(tk[k]) and tk[k + 1] == "din" and tk[k + 2] in ("pehle", "purane"):
            if int(tk[k]) <= backtest.MAX_LAG:
                m["lag"] = int(tk[k])

    allg = False
    if (any(w in tk for w in ("sabhi", "sab")) and "games" in tk) or "chaaron" in tk:
        allg = True
    triple = "teeno" in tk and not ments

    # ---- source / target baantna ----
    cpos = next((i for i, w in enumerate(tk) if w in CONNECT), None)
    verbpos = max((i for i, w in enumerate(tk) if w in VERBS), default=None)
    if cpos is not None and ments and any(m["p"] < cpos for m in ments) and any(m["p"] > cpos for m in ments):
        srcs = [m for m in ments if m["p"] < cpos]
        tgts = [m for m in ments if m["p"] > cpos]
        split = cpos
        mark(cpos)
    elif ments:
        tg = [ments[-1]]
        k = len(ments) - 2
        while k >= 0:
            between = tk[ments[k]["p"] + 1: tg[0]["p"]]
            if all(b in JOIN for b in between) and ments[k]["lag"] in (None, 0):
                tg.insert(0, ments[k])
                k -= 1
            else:
                break
        tgts = tg
        srcs = [m for m in ments if m not in tgts]
        split = srcs[-1]["p"] + 1 if srcs else 0
        if len(ments) == 1:
            srcs, tgts, split = [], [ments[0]], 0
    else:
        srcs, tgts, split = [], [], 0

    on = [m["game"] for m in tgts]
    if allg:
        on = ["FD", "GB", "GL", "DS"]
    elif triple:
        on = ["FD", "GB", "GL"]
    if not on:
        return {"ok": False, "error": "Kis game me lagana hai ye samajh nahi aaya. Jaise: 'FB me lagao' ya 'GB aur GL me'."}

    # ---- mode ----
    mode = "rule"
    if any(w in HOT for w in tk) or ("zyada" in tk and any(w in tk for w in ("aaye", "aaya", "aata", "baar", "nikle"))):
        mode = "hot"
    elif any(w in COLD for w in tk) or "der" in tk or ("nahi" in tk and any(w in tk for w in ("aaya", "aaye", "aata"))):
        mode = "cold"
    for w in HOT | COLD | {"zyada", "der", "nahi", "sabse"}:
        for i, x in enumerate(tk):
            if x == w:
                mark(i)

    # ---- ops, days, numbers ----
    ops, dost_n, days = [], None, []
    nums_left, nums_right = [], []
    window = topk = None
    for i, w in enumerate(tk):
        nxt = tk[i + 1] if i + 1 < len(tk) else ""
        prv = tk[i - 1] if i > 0 else ""
        if w in OPS:
            ops.append(OPS[w]); mark(i)
        elif w in DOST:
            mark(i)
            if "dost" not in ops:
                ops.append("dost")
            for c, ci in ((nxt, i + 1), (prv, i - 1)):
                if _is_num(c) and dost_n is None:
                    dost_n = int(c); mark(ci)
            if prv == "top" and i >= 2 and _is_num(tk[i - 2]):
                dost_n = int(tk[i - 2]); mark(i - 2)
        elif re.fullmatch(r"[+\-]\d+", w):
            k = int(w)
            if abs(k) == 1:
                ops.append("plus1" if k > 0 else "minus1"); mark(i)
        elif w in ("plus", "minus") and _is_num(nxt) and int(nxt) == 1:
            ops.append("plus1" if w == "plus" else "minus1"); mark(i, i + 1)
        elif w == "upar" and prv == "ek":
            ops.append("plus1"); mark(i, i - 1)
        elif w == "neeche" and prv == "ek":
            ops.append("minus1"); mark(i, i - 1)
        elif w in WEEK:
            days.append(WEEK[w]); mark(i)
        elif w in ("top",) and _is_num(nxt):
            topk = int(nxt); mark(i, i + 1)
        elif _is_num(w):
            if nxt in ("din", "dino"):
                window = int(w); mark(i, i + 1)
            elif nxt in ("mahine", "mahina", "month"):
                window = int(w) * 30; mark(i, i + 1)
            elif nxt in ("number", "numbers") and mode in ("hot", "cold"):
                topk = int(w); mark(i, i + 1)
            elif not used[i]:
                (nums_left if i < split else nums_right).append(int(w)); mark(i)
    # 'ek upar' / 'ek neeche' me 'ek' filler; baaki shabd
    ops = list(dict.fromkeys(ops))
    if "dost" in ops:
        ops[ops.index("dost")] = f"dost{min(dost_n or 3, 10)}"

    spec = {"mode": mode, "on": list(dict.fromkeys(on)), "days": sorted(set(days)) if days else None}
    warn = []
    if mode in ("hot", "cold"):
        spec.update(window=min(max(window or 30, 5), 365), topk=min(max(topk or 10, 1), MAXTOP))
        if mode == "cold":
            spec.pop("window", None)
    else:
        spec["ops"] = ops or ["same"]
        if srcs:
            order = backtest.GAMES
            same_day = (any(m["lag"] == 0 for m in tgts) and not any(w in tk for w in ("agle", "agla", "next", "kal"))
                        and all(order.index(a["game"]) < order.index(b["game"]) for a in srcs for b in tgts))
            spec["sources"] = [{"game": m["game"], "lag": (m["lag"] if m["lag"] is not None else (0 if same_day else 1))} for m in srcs]
            spec["base"] = "source"
            if nums_left:
                spec["value"] = nums_left[0]
                if len(nums_left) > 1:
                    warn.append("Sirf pehla number (%02d) trigger me liya." % nums_left[0])
            if nums_right:
                spec["base"], spec["fixed"] = "fixed", nums_right
        else:
            fixed = nums_right or nums_left
            if not fixed:
                return {"ok": False, "error": "Number kahan se lena hai ye samajh nahi aaya. Jaise: 'kal GB me jo aaya wahi aaj FB me', "
                        "ya 'FB me 30 ke dost lagao', ya 'pichle 30 din me sabse zyada aaye wo 10 number'."}
            spec["base"], spec["fixed"] = "fixed", fixed
    try:
        spec = clean(spec)
    except ValueError as e:
        return {"ok": False, "error": str(e), "spec": spec}
    ignored = [w for i, w in enumerate(tk) if not used[i] and w not in FILLER and w not in LAG1 and not w.isdigit()]
    return {"ok": True, "spec": spec, "explain": explain(spec), "ignored": ignored[:8], "warnings": warn}


def clean(spec):
    """Form se ya parser se aaye spec ko saaf karo; galat ho to Hinglish me ValueError."""
    s = {"mode": spec.get("mode", "rule")}
    if s["mode"] not in ("rule", "hot", "cold"):
        raise ValueError("mode galat")
    on = []
    for g in spec.get("on") or []:
        g = GAME_WORDS.get(str(g).lower(), None)
        if g and g not in on:
            on.append(g)
    if not on:
        raise ValueError("Kam se kam ek game chuno jisme lagana hai.")
    s["on"] = on
    days = spec.get("days")
    s["days"] = sorted({int(d) for d in days if 0 <= int(d) <= 6}) if days else None
    if s["mode"] in ("hot", "cold"):
        s["topk"] = min(max(int(spec.get("topk", 10)), 1), MAXTOP)
        if s["mode"] == "hot":
            s["window"] = min(max(int(spec.get("window", 30)), 5), 365)
        return s
    ops = [o for o in (spec.get("ops") or ["same"]) if re.fullmatch(r"same|palat|plus1|minus1|family|dost([1-9]|10)", str(o))]
    s["ops"] = list(dict.fromkeys(ops)) or ["same"]
    if spec.get("base") == "fixed":
        fixed = []
        for v in spec.get("fixed") or []:
            if not 0 <= int(v) <= 99:
                raise ValueError("Number 0 se 99 ke beech hona chahiye.")
            if int(v) not in fixed:
                fixed.append(int(v))
        if not fixed:
            raise ValueError("Koi number nahi diya.")
        s["base"], s["fixed"] = "fixed", fixed[:20]
        if spec.get("sources"):
            s["sources"] = _srcs(spec["sources"], on)
            if spec.get("value") not in (None, ""):
                s["value"] = int(spec["value"])
        return s
    s["base"] = "source"
    s["sources"] = _srcs(spec.get("sources"), on)
    if not s["sources"]:
        raise ValueError("Source game chuno (jaise 'kal GB').")
    if spec.get("value") not in (None, ""):
        v = int(spec["value"])
        if not 0 <= v <= 99:
            raise ValueError("Number 0 se 99 ke beech hona chahiye.")
        s["value"] = v
    return s


def _srcs(src, on):
    out = []
    for x in src or []:
        g = GAME_WORDS.get(str(x.get("game", "")).lower())
        lag = int(x.get("lag", 1))
        if not g or not 0 <= lag <= backtest.MAX_LAG:
            raise ValueError("Source game ya din galat hai.")
        for t in on:
            if not backtest.known(g, lag, t):
                why = "ek hi game ka aaj ka result us game me lagane ke liye pehle nahi aata" if g == t else f"aaj ka {NAME[g]} {NAME[t]} ke baad aata hai"
                raise ValueError(f"Ye nahi ho sakta: {why}. 'Kal' (ya pehle ka din) ka result lo, ya aisa game chuno jo target se pehle khulta ho.")
        if {"game": g, "lag": lag} not in out:
            out.append({"game": g, "lag": lag})
    return out


def _lag_txt(lag):
    return {0: "aaj ke", 1: "kal ke", 2: "parso ke"}.get(lag, f"{lag} din pehle ke")


def explain(spec):
    """Simple Hinglish me 'maine ye samjha'."""
    on = " + ".join(NAME[g] for g in spec["on"])
    day = ""
    if spec.get("days"):
        nm = ["Somvar", "Mangalvar", "Budhvar", "Guruvar", "Shukravar", "Shanivar", "Ravivar"]
        day = " (sirf " + ", ".join(nm[d] for d in spec["days"]) + " ko)"
    if spec["mode"] == "hot":
        return f"Pichle {spec['window']} din me jo {spec['topk']} number sabse zyada aaye, wahi {on} me lagao{day}."
    if spec["mode"] == "cold":
        return f"Jo {spec['topk']} number {on} me sabse der se nahi aaye, wahi lagao{day}."
    fixed = spec.get("base") == "fixed"
    subj = ", ".join("%02d" % n for n in spec["fixed"]) if fixed else None
    if fixed:
        opn = {"same": subj, "palat": f"{subj} ka palat", "plus1": f"{subj} +1", "minus1": f"{subj} -1", "family": f"{subj} ki family"}
    else:
        opn = {"same": "wahi number", "palat": "uska palat", "plus1": "usse ek zyada (+1)", "minus1": "usse ek kam (-1)", "family": "uski family (rashi + palat)"}
    parts = []
    for o in spec["ops"]:
        parts.append((f"{subj} ke top {o[4:]} dost" if fixed else f"uske top {o[4:]} dost") if o.startswith("dost") else opn[o])
    what = " + ".join(parts)
    if fixed:
        cond = ""
        if spec.get("sources"):
            sr = " ya ".join(f"{_lag_txt(s['lag'])} {NAME[s['game']]}" for s in spec["sources"])
            cond = f"Jab {sr} me " + ("%02d aaye" % spec["value"] if spec.get("value") is not None else "kuch bhi aaye") + ", tab "
        return f"{cond}{what} {on} me lagao{day}."
    sr = " ya ".join(f"{_lag_txt(s['lag'])} {NAME[s['game']]}" for s in spec["sources"])
    cond = f" (sirf jab wo number %02d ho)" % spec["value"] if spec.get("value") is not None else ""
    return f"{sr} number{cond} lo, aur {what} {on} me lagao{day}."
