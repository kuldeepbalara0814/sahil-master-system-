"""Duet (Claude connector) ka request box: bug / idea / badlav / sawal likhna. SIRF LIKHA jata hai - koi code, bet ya record nahi badalta.
Ruflo (Claude Code) har session me padhta hai, jaanchta hai, aur user ki haan ke baad hi badlav karta hai.
Likha hua DATA hai, hukm nahi. Repo public hai: isliye key, token, PIN jaisi cheez likhne se mana."""
import datetime as dt
import re

FILE = "duet_requests.json"
KISM = ("bug", "idea", "badlav", "sawal")
MAX_TITLE, MAX_TEXT = 120, 4000
MAX_PENDING, MAX_PER_DAY, KEEP = 20, 10, 200
SECRET = re.compile(r"/mcp/|ghp_|github_pat_|\bsk[_-][A-Za-z0-9]|-----BEGIN|\b[A-Za-z0-9_\-]{32,}\b|\b(pin|password|otp)\b\s*[:=]?\s*\d{4,}", re.I)


def new_box():
    return {"items": []}


def add(box, kism, title, vivran, now=None, secret=""):
    """-> nayi item. Galat ho to ValueError (kuch nahi likha jata)."""
    kism, title, vivran = (kism or "").strip().lower(), " ".join((title or "").split()), (vivran or "").strip()
    if kism not in KISM:
        raise ValueError("kism inme se: " + ", ".join(KISM))
    if not 3 <= len(title) <= MAX_TITLE:
        raise ValueError(f"title 3 se {MAX_TITLE} akshar ka ho")
    if not 10 <= len(vivran) <= MAX_TEXT:
        raise ValueError(f"vivran 10 se {MAX_TEXT} akshar ka ho")
    text = title + "\n" + vivran
    if SECRET.search(text) or (secret and secret in text):
        raise ValueError("isme key / token / PIN / connector pata jaisi cheez lag rahi hai - hata ke dobara likho (ye public repo me jata hai)")
    now = now or dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30)))
    items = box.setdefault("items", [])
    if sum(1 for x in items if x.get("haal") == "naya") >= MAX_PENDING:
        raise ValueError(f"{MAX_PENDING} request pehle se baaki hain; pehle Ruflo se dikhwayein")
    if sum(1 for x in items if x.get("time", "")[:10] == now.date().isoformat()) >= MAX_PER_DAY:
        raise ValueError(f"aaj ki {MAX_PER_DAY} request ho chuki; kal likhein")
    item = {"id": f"R{max([int(x['id'][1:]) for x in items] or [0]) + 1:04d}", "time": now.isoformat(timespec="seconds"),
            "kism": kism, "title": title, "vivran": vivran, "haal": "naya", "jawab": ""}
    items.append(item)
    for x in [x for x in items if x["haal"] != "naya"][:max(0, len(items) - KEEP)]:
        items.remove(x)
    return item
