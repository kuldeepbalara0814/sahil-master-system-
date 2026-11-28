"""Claude connector ke aur tool (patterns/016_connector/README.md). SIRF PADHTE hain: koi file, bet, scan ya GitHub par likhna nahi.

Har jawab par DHYAN mohar: ye kagaz ka kalpnik puzzle khel (paper trading testing) hai, asli paisa / bhavishyavani nahi."""
import datetime as dt
import json
import os
import time
import urllib.request

from . import card, data, pockets, rank, reqbox, tick, window, yaad

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DHYAN = ("KAGAZ KA KALPNIK PUZZLE KHEL (paper trading testing). Asli paisa nahi, koi salah ya bhavishyavani nahi. "
         "Ab tak ki jaanch me in list ka natija random jaisa hi hai.")
GAMES = ("FB", "GB", "GL", "DS")      # andar ka naam; jawab me app jaisa "FD" (fd_naam)
KEYS = [k for k, _ in pockets.LISTS]
NAMES = dict(pockets.LISTS)
MAX_DOC = 24000
_gh = {"t": 0.0, "out": None}


def mohar(fn):
    """Har tool ke jawab ke sabse upar DHYAN."""
    def wrap(**kw):
        out = fn(**kw)
        return {"dhyan": DHYAN, **out} if isinstance(out, dict) else {"dhyan": DHYAN, "jawab": out}
    return wrap


def fd_naam(fn):
    """App me pehla game 'FD' dikhta hai (andar 'FB'): jawab ke key aur game-naam FD kar do."""
    def wrap(**kw):
        return json.loads(json.dumps(fn(**kw), ensure_ascii=False, default=str).replace('"FB"', '"FD"'))
    return wrap


def _s(nums):
    return [f"{int(n):02d}" for n in sorted(nums)]


class Reader:
    """lab_server se: state() -> (rows, friends), jload(naam, default), manual+partial wale result."""

    def __init__(self, state, jload, known):
        self.state, self.jload, self.known = state, jload, known

    def scan(self):
        rows, fr = self.state()
        rep = self.jload("patterns_today.json", None) or {}
        return rows, fr, rep

    def today_lists(self):
        """-> (play date, {key: numbers}, lock hui thi?)"""
        rows, _, rep = self.scan()
        play = data.play_date(rows).isoformat()
        day = (self.jload("pockets.json", None) or {}).get("days", {}).get(play)
        if day:
            return play, pockets.lists_of(day), True
        if not rep:
            return play, {}, False
        return play, pockets.baskets(rep, rows), False

    def pick(self, key, lists):
        if key not in KEYS:
            raise ValueError("list ka naam inme se: " + ", ".join(KEYS))
        return set(lists.get(key) or [])

    # ---- aaj ki jodiyan ----
    def aaj_ki_tokri(self, list=""):
        play, lists, locked = self.today_lists()
        keys = [list] if list else KEYS
        for k in keys:
            self.pick(k, lists)
        return {"tarikh": play, "lock": locked, "note": "Subah ke scan par lock hoti hai." if locked else "Abhi lock nahi: taaza ginti.",
                "list": {k: {"naam": NAMES[k], "ginti": len(lists.get(k) or []), "jodi": _s(lists.get(k) or [])} for k in keys}}

    def tulna(self, pehli="top30", doosri="dost"):
        play, lists, locked = self.today_lists()
        a, b = self.pick(pehli, lists), self.pick(doosri, lists)
        both = a & b
        return {"tarikh": play, "lock": locked, "pehli": {"key": pehli, "naam": NAMES[pehli], "ginti": len(a)},
                "doosri": {"key": doosri, "naam": NAMES[doosri], "ginti": len(b)},
                "dono_me": {"ginti": len(both), "jodi": _s(both)}, "sirf_pehli_me": _s(a - b), "sirf_doosri_me": _s(b - a),
                "random_me_aam_taur_par_common": round(len(a) * len(b) / 100, 1)}

    def jodi_khojo(self, jodi=0):
        rows, fr, rep = self.scan()
        play, lists, _ = self.today_lists()
        out = {"jodi": f"{jodi:02d}", "tarikh": play, "kin_list_me": [NAMES[k] for k in KEYS if jodi in (lists.get(k) or [])]}
        if rep:
            allr = next(g for g in rank.build(rep, rows, fr)["groups"] if g["key"] == "all")["lists"]["ALL"]
            for i, r in enumerate(allr):
                if r["n"] == jodi:
                    out["number_rank"] = {"kram": i + 1, "kul": len(allr), "score": r["score"], "baar_tokri": bool(r["baar"]), "kisne_diya": r["maps"][:40]}
        out["naksha_aaj"] = [{"game": e["game"], "naksha": e["name"], "title": e["title"]} for e in yaad.view(rows)["aaj"]["items"] if jodi in e["numbers"]]
        hits = [{"tarikh": d.isoformat(), "game": g} for d, v, *_ in rows for g, n in zip(GAMES, v) if n == jodi]
        out["pichli_baar_aayi"] = hits[-8:][::-1]
        out["kul_baar"] = len(hits)
        return out

    def naksha_aaj(self):
        rows, _, _ = self.scan()
        v = yaad.view(rows)["aaj"]
        play, lists, _ = self.today_lists()
        top = set(lists.get("top30") or [])
        return {"tarikh": v["date"], "kul_alag_jodi": len(v["all"]), "jodi": _s(v["all"]),
                "game_wise": {g: _s(n) for g, n in v["games"].items()},
                "30_jodi_me_bhi": _s(set(v["all"]) & top),
                "map": [{"naksha": e["name"], "game": e["game"], "jodi": _s(e["numbers"]), "title": e["title"], "kitne_din_se": e["pehle"]} for e in v["items"]],
                "note": "Naksha 1 ke naye aur pehle bane '?' box. 900 din ki jaanch: random jaisa."}

    def card_007(self):
        rows, _, rep = self.scan()
        if not rep:
            return {"note": "Abhi koi scan nahi."}
        s = window.steps007(rep)
        return {"tarikh": s["date"], "aaj_ki_jodi": _s(s["all"]), "aage_ke_box": _s(s["aage_all"]),
                "pattern": [{"naam": it["name"], "title": it["title"], "aaj": it["aaj"], "aage": it["aage"]} for it in s["items"] if it["aaj"] or it["aage"]],
                "note": "Card 007 ka niyam user ke mutabik abhi poora sahi nahi; sudhaar baaki."}

    def roz_ka_card(self):
        rows, _, rep = self.scan()
        v = card.view(self.jload("cards.json", None) or card.new_state(), rows, rep, self.jload("pockets.json", None))
        cur = v["card"]
        return {"tarikh": v["play_date"], "bana": v["bana"], "kyun": v["kyun"], "solid": _s(cur["solid"]) if cur else [], "spot": _s(cur["spot"]) if cur else [],
                "pichle": [{"date": x["date"], "solid": _s(x["solid"]), "spot": _s(x["spot"])} for x in v["pichle"][:7]],
                "matlab": "30 jodi + Naksha + Dost teeno me jo jodi; Baar me bhi = solid, baaki spot."}

    def requests_dekho(self):
        items = (self.jload(reqbox.FILE, None) or reqbox.new_box()).get("items", [])
        return {"kul": len(items), "naya": sum(1 for x in items if x["haal"] == "naya"), "list": items[-15:][::-1]}

    # ---- natija / paisa (kagaz) ----
    def din_ka_natija(self, tarikh=""):
        rows, _, _ = self.scan()
        by = {d.isoformat(): v for d, v, *_ in rows}
        date = tarikh or rows[-1][0].isoformat()
        res = window._results(by, self.known(rows), date)
        day = (self.jload("pockets.json", None) or {}).get("days", {}).get(date)
        lists = pockets.lists_of(day) if day else {}
        w = (self.jload("window_log.json", None) or {}).get("days", {}).get(date)
        if "top30" not in lists and w:
            lists["top30"] = [x["n"] for x in w["top30"]]
        out = {k: {"naam": NAMES.get(k, k), "ginti": len(n), "hit": [{"game": g, "jodi": f"{res[g]:02d}"} for g in GAMES if g in res and res[g] in n]}
               for k, n in lists.items()}
        return {"tarikh": date, "result": {g: f"{n:02d}" for g, n in res.items()},
                "list_ka_hit": out or "Us din ki koi lock tokri nahi mili (tokri 24 Nov se Window me, 28 Nov se baaki list)."}

    def pocket_report(self, list=""):
        rows, _, _ = self.scan()
        st = self.jload("pockets.json", None) or pockets.new_state()
        known = self.known(rows)
        if list:
            if list not in KEYS:
                raise ValueError("list ka naam inme se: " + ", ".join(KEYS))
            s = pockets.statement(st, rows, known, list)
            s["lines"] = [{k: v for k, v in x.items() if k != "numbers"} for x in s["lines"][-31:]]
            return {"shuru": pockets.START.isoformat(), "pocket": s}
        brief = []
        for k in KEYS:
            s = pockets.statement(st, rows, known, k)
            brief.append({"key": k, "naam": s["naam"], "balance": s["balance"], "fayda_nuksan": s["balance"] - pockets.CAPITAL, **{x: s["totals"][x] for x in ("days", "hit_days", "expected_hit_days")}})
        return {"shuru": pockets.START.isoformat(), "capital": pockets.CAPITAL, "pocket": brief,
                "samjho": "hit_days ko expected_hit_days (random ummeed) se milao; usse zyada na ho to koi fayda saabit nahi."}

    # ---- sehat / bug ----
    def error_jaanch(self, github=""):
        rows, _, rep = self.scan()
        now = dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30)))
        cp = self.jload("partial_results.json", None) or {}
        dikkat = [f"data: {p}" for p in data.validate(rows)[:10]]
        dikkat += [f"scan {e.get('pattern')}: {e.get('error')}" for e in rep.get("errors") or []]
        if rep and rep.get("asof") != rows[-1][0].isoformat():
            dikkat.append(f"aakhri scan {rep.get('asof')} ka hai, data {rows[-1][0].isoformat()} tak")
        part = cp if cp.get("results") else None
        late = tick.overdue(now, rows, part)
        if late:
            dikkat.append("ye result 2 ghante se zyada atke: " + ", ".join(late))
        out = {"abhi": now.strftime("%Y-%m-%d %H:%M IST"), "theek": not dikkat, "dikkat": dikkat or ["koi nahi mili"],
               "aakhri_data": rows[-1][0].isoformat(), "baaki_result": tick.due(now, rows, part), "aadhi_line": part,
               "auto_fetch_record": (self.jload("tick_log.json", []) or [])[-5:], "fetch_record": (self.jload("fetch_log.json", []) or [])[-5:],
               "khabar": [{"time": a["time"], "label": a["label"]} for a in (self.jload("alerts.json", None) or {}).get("items", [])[:5]],
               "pata_ho": "Result site Render ko 403 deti hai: app GitHub Action chalati hai (aam baat)."}
        if github == "haan":
            out["github_runs"] = github_runs()
        return out

    def guide(self, vishay="app"):
        return guide(vishay)


def github_runs(repo="kuldeepbalara0814/sahil-master-system-"):
    """GitHub Action ki pichli run (public jankari, 10 minute cache)."""
    if _gh["out"] is None or time.time() - _gh["t"] > 600:
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/runs?per_page=8", headers={"User-Agent": "sahil-lab"})
            with urllib.request.urlopen(req, timeout=8) as r:
                _gh["out"] = [{"kya": x["name"], "kab": x["created_at"], "natija": x["conclusion"] or x["status"]} for x in json.load(r)["workflow_runs"]]
            _gh["t"] = time.time()
        except Exception as e:
            return f"GitHub se jankari nahi mili: {type(e).__name__}"
    return _gh["out"]


def _read(*parts):
    try:
        with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def guide(vishay="app"):
    """app = app kya hai; patterns = list; 001..016 = us pattern ka README; handoff = aakhri faisle; shabd = glossary."""
    folder = os.path.join(ROOT, "patterns")
    dirs = sorted(d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d)))
    v = (vishay or "app").strip().lower()
    if v == "app":
        text = _read("lab", "help_kb.md")
    elif v == "patterns":
        text = _read("patterns", "README.md")
    elif v == "shabd":
        text = _read("patterns", "GLOSSARY.md")
    elif v == "handoff":
        text = (_read("patterns", "HANDOFF.md") or "")[-MAX_DOC:]
    else:
        match = [d for d in dirs if d.startswith(v)] if v.isdigit() and len(v) == 3 else []
        text = _read("patterns", match[0], "README.md") if match else None
    if text is None:
        raise ValueError("vishay: app, patterns, shabd, handoff, ya pattern number " + ", ".join(d[:3] for d in dirs))
    return {"vishay": v, "pattern_list": [d for d in dirs], "likha_hai": text[:MAX_DOC]}


def tools(reader, Tool, likho):
    lst = {"type": "string", "description": "list: " + ", ".join(f"{k} = {n}" for k, n in pockets.LISTS)}
    return [
        Tool("aaj_ki_tokri", "Aaj ki saari jodi list", "Aaj ki har list ki jodi (30 jodi, dost, baar, rashi, naksha, card 007, family, dana, copy, random). Kagaz ka puzzle khel.",
             mohar(fd_naam(reader.aaj_ki_tokri)), {"list": dict(lst, description=lst["description"] + ". Khali = sab.")}),
        Tool("tulna", "Do list ki tulna", "Aaj ki do list me common jodi aur alag jodi (jaise 30 jodi aur dost). Default top30 vs dost.",
             mohar(fd_naam(reader.tulna)), {"pehli": lst, "doosri": lst}),
        Tool("jodi_khojo", "Ek jodi kahan-kahan", "Ek jodi (0-99) kin list me, kis pattern ne di, kis naksha me, aur pehle kab aayi.",
             mohar(fd_naam(reader.jodi_khojo)), {"jodi": {"type": "integer", "minimum": 0, "maximum": 99, "description": "0-99 (07 ke liye 7)"}}),
        Tool("naksha_aaj", "Aaj ke naksha", "Aaj ki tarikh wale Naksha map: kitni jodi, kis game me, 30 jodi me kaunsi.", mohar(fd_naam(reader.naksha_aaj))),
        Tool("card_007", "Card 007 aaj", "Puzzle-Steps (007) ke aaj aur aage ke box ki jodi.", mohar(fd_naam(reader.card_007))),
        Tool("din_ka_natija", "Din ka natija", "Kisi din ka result aur us din ki lock list me kisne hit kiya.",
             mohar(fd_naam(reader.din_ka_natija)), {"tarikh": {"type": "string", "description": "YYYY-MM-DD; khali = aakhri din"}}),
        Tool("pocket_report", "Kagaz ke pocket", "Har list ke Rs 10,000 kagaz pocket ka hisaab; list doge to din-wise statement.",
             mohar(fd_naam(reader.pocket_report)), {"list": lst}),
        Tool("error_jaanch", "Site ki sehat aur bug", "Data, scan, auto-fetch, atke result, khabar; github='haan' do to GitHub ki pichli run bhi.",
             mohar(fd_naam(reader.error_jaanch)), {"github": {"type": "string", "description": "'haan' = GitHub run bhi"}}),
        Tool("roz_ka_card", "Roz ka card", "Aaj ke card ke solid aur spot number (kagaz ka puzzle), pichle card, aur na bana ho to kyun.", mohar(reader.roz_ka_card)),
        Tool("requests_dekho", "Request box dekho", "Duet ne jo bug/idea likhe aur unka haal (naya / ho gaya / mana).", mohar(reader.requests_dekho)),
        Tool("request_likho", "Request likho (Ruflo ke liye)",
             "Bug, idea, badlav ya sawal request box me likho; Ruflo (Claude Code) baad me jaanchega. User ki marzi se hi likho. Public repo me jata hai: key/PIN/pata kabhi nahi.",
             mohar(likho), {"kism": {"type": "string", "description": "bug, idea, badlav ya sawal"},
                            "title": {"type": "string", "description": "Ek line (3-120 akshar)"},
                            "vivran": {"type": "string", "description": "Poori baat: kya dekha, kya hona chahiye (10-4000 akshar)"}},
             ["kism", "title", "vivran"], write=True),
        Tool("guide", "Guide: app aur pattern ka matlab", "App ka tarika, pattern ke niyam, shabd, aur ab tak ke faisle. Samjhane ya idea sochne se pehle padho.",
             mohar(reader.guide), {"vishay": {"type": "string", "description": "app, patterns, shabd, handoff, ya 001..016"}}),
    ]
