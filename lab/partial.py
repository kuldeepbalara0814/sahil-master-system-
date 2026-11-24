"""Aadhi line (partial result): aaj ke jo game aa chuke (FB shaam ~6:30, GB raat ~10:30, GL raat ~12:15) -- DS agli subah ~5:30.
Line tab hi results.csv me judti hai jab chaaron aa jayen; tab tak aadhe result 'partial_results.json' me rakhte hain (sirf dikhane/pattern ke liye, record nahi).
{"asof": ISO, "date": "YYYY-MM-DD", "results": {"FB": 53, "GB": 93}}"""
import datetime as dt

GAMES = ("FB", "GB", "GL", "DS")


def clean(obj, last=None):
    """Sahi shape ka partial ya None. last = results.csv ki aakhri line ki tarikh: wo ya usse purani tarikh ka partial bekaar (line poori ho chuki)."""
    try:
        d = dt.date.fromisoformat(obj["date"])
        res = {g: int(n) for g, n in obj["results"].items() if g in GAMES[:3] and n is not None and 0 <= int(n) <= 99}
    except (TypeError, KeyError, ValueError, AttributeError):
        return None
    if not res or (last is not None and d <= last):
        return None
    return {"asof": obj.get("asof"), "date": d.isoformat(), "results": res}


def as_row(p):
    """steps ke liye: (date, [fb, gb, gl, None], 'partial'); None = abhi aaya nahi."""
    d = dt.date.fromisoformat(p["date"])
    r = p["results"]
    return d, [r.get("FB"), r.get("GB"), r.get("GL"), None], "partial"


def new_games(prev, cur):
    """cur me aise game jo prev me us tarikh par nahi the (naya result aaya). -> [(game, number)]."""
    if not cur:
        return []
    old = (prev or {}).get("results", {}) if prev and prev.get("date") == cur["date"] else {}
    return [(g, n) for g, n in cur["results"].items() if g not in old]


def merged_results(manual, partial):
    """{date: {game: number}}: hath se dale (manual) auto-partial par bhaari."""
    out = {}
    if partial:
        out[partial["date"]] = dict(partial["results"])
    for d, v in (manual or {}).items():
        out.setdefault(d, {}).update(v)
    return out
