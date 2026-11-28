"""Roz ka card (patterns/017_roz_ka_card/README.md). SIRF KAGAZ ka puzzle: asli paisa, salah ya bhavishyavani nahi.

User ka niyam (28 Nov 2026), us din ki subah wali LOCK tokri (data/pockets.json) se:
  1) "30 jodi (sab pattern)"            -> top30
  2) Naksha: aaj ke naye + pehle bane naksha jinme aaj ki tarikh ka box  -> naksha | naksha_sab
  3) Dost 30                             -> dost
  4) Ek baar ki window (us weekday ki Baar tokri) -> baar
Jo jodi 1, 2 aur 3 teeno me = card ki jodi. Inme jo 4 (baar) me bhi = SOLID (upar hara), baaki = SPOT (neeche).

Kab banta hai: tarikh D ka card tabhi, jab line D-1 POORI ho (DS = D ki subah ~5:30, isi se line poori hoti hai), us line par
subah ka naya scan chal chuka ho (scan asof = aakhri line, play_date = D) aur D ki tokri lock ho chuki ho. Ek baar bana to
LOCK (data/cards.json): dobara kabhi nahi badalta. Purani tarikh (aaj se pehle) ka card kabhi nahi banta, aur kal ke data par
aaj ka card nahi banta (scan purana ho to ruk jata hai, agli run phir dekhti hai).
"""
import datetime as dt
import io
import os

from PIL import Image, ImageDraw, ImageFont

from . import data

NEEDED = ("top30", "naksha", "naksha_sab", "dost", "baar")
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
FOOT_GAMES = "FD   GB   GL   DS"
FOOT_NOTE = "Sahil Lab  |  paper test"

# Rang aur naap: 28 Nov 2026 ke haath se bane card jaise (1080 chauda)
W, M, COLS, COL_W = 1080, 60, 4, 240
BG, WHITE = (18, 22, 31), (255, 255, 255)
GREEN, GREEN_LBL = (23, 163, 74), (220, 252, 231)
BORDER, SPOT_LBL, SPOT_NUM = (90, 101, 121), (209, 213, 219), (241, 245, 249)
WEEKDAY, YELLOW, NOTE = (180, 188, 204), (250, 204, 21), (122, 128, 140)
_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu", "/usr/share/fonts/TTF", "/Library/Fonts", "C:/Windows/Fonts"]
_FONTS = {}


def numbers(lists):
    """Lock tokri -> {"solid": [...], "spot": [...], "teeno": [...]} (sab sorted)."""
    lists = lists or {}
    s = lambda k: {int(n) for n in lists.get(k) or []}
    teeno = s("top30") & (s("naksha") | s("naksha_sab")) & s("dost")
    solid = teeno & s("baar")
    return {"solid": sorted(solid), "spot": sorted(teeno - solid), "teeno": sorted(teeno)}


def today_ist():
    return dt.datetime.now(IST).date()


def ready(rows, rep, pstate, today=None):
    """-> (theek?, play date iso, kyun). Card banane ki saari shartein ek jagah."""
    play = data.play_date(rows)
    key = play.isoformat()
    last = rows[-1][0].isoformat()
    today = today or today_ist()
    if play < today:
        return False, key, f"aakhri poori line {last} ki hai: aaj ({today.isoformat()}) ka DS wala data abhi nahi aaya"
    if not rep:
        return False, key, "abhi koi scan nahi"
    if rep.get("asof") != last or rep.get("play_date") != key:
        return False, key, f"scan purana hai (scan {rep.get('asof')} ka, data {last} tak)"
    if rep.get("errors"):
        return False, key, "scan me galti thi"
    day = (pstate or {}).get("days", {}).get(key)
    if not day:
        return False, key, f"{key} ki tokri abhi lock nahi hui"
    if day.get("late"):
        return False, key, f"{key} ki tokri result aane ke baad bani (late): card nahi"
    missing = [k for k in NEEDED if k not in (day.get("lists") or {})]
    if missing:
        return False, key, "tokri me ye list nahi: " + ", ".join(missing)
    return True, key, "theek"


def new_state():
    return {"days": {}}


def make(cstate, rows, rep, pstate, today=None, now=None):
    """Shartein poori hon aur is tarikh ka card na bana ho to LOCK karo. -> (nayi bani?, play iso, kyun)."""
    ok, key, why = ready(rows, rep, pstate, today)
    days = cstate.setdefault("days", {})
    if key in days:
        return False, key, "is tarikh ka card pehle hi bana (lock)"
    if not ok:
        return False, key, why
    nums = numbers(pstate["days"][key]["lists"])
    days[key] = {"solid": nums["solid"], "spot": nums["spot"], "asof": rep.get("asof"), "scan_time": rep.get("time"),
                 "made": (now or dt.datetime.now(IST)).isoformat(timespec="seconds")}
    return True, key, "bana"


def font(size, bold=True):
    key = (size, bold)
    if key not in _FONTS:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        f = None
        for d in _DIRS:
            try:
                f = ImageFont.truetype(os.path.join(d, name), size)
                break
            except OSError:
                continue
        _FONTS[key] = f or ImageFont.load_default(size=size)
    return _FONTS[key]


def _grid(draw, nums, top, size, color, step):
    """4 column ki grid, har row ke number beech me (kam number ho to row beech me aati hai)."""
    for r in range(0, len(nums), COLS):
        row = nums[r:r + COLS]
        x0 = M + (COLS - len(row)) * COL_W // 2
        y = top + (r // COLS) * step
        for i, n in enumerate(row):
            draw.text((x0 + i * COL_W + COL_W // 2, y), f"{n:02d}", font=font(size), fill=color, anchor="mm")


def _rows(n):
    return max(1, (n + COLS - 1) // COLS)


def render(date_iso, solid, spot, quality=92):
    """Card ki JPG (bytes). 4 solid + 8 spot = 1080x1350, bilkul 28 Nov wala naksha; zyada number ho to card lamba."""
    d = dt.date.fromisoformat(date_iso)
    g_h = 205 + (_rows(len(solid)) - 1) * 150 + 155
    s_h = 175 + (_rows(len(spot)) - 1) * 135 + 100
    g_top = 240
    s_top = g_top + g_h + 50
    s_bot = s_top + s_h
    H = s_bot + 290
    im = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(im)
    dr.text((W // 2, 101), d.strftime("%d-%m-%Y"), font=font(72), fill=WHITE, anchor="mm")
    dr.text((W // 2, 171), d.strftime("%A").upper(), font=font(34, bold=False), fill=WEEKDAY, anchor="mm")
    dr.rounded_rectangle((M, g_top, W - M, g_top + g_h), radius=40, fill=GREEN)
    dr.text((W // 2, g_top + 57), "SOLID", font=font(44), fill=GREEN_LBL, anchor="mm")
    if solid:
        _grid(dr, solid, g_top + 205, 124, WHITE, 150)
    else:
        dr.text((W // 2, g_top + 205), "aaj koi nahi", font=font(56), fill=GREEN_LBL, anchor="mm")
    dr.rounded_rectangle((M, s_top, W - M, s_bot), radius=40, outline=BORDER, width=3)
    dr.text((W // 2, s_top + 56), "SPOT", font=font(44), fill=SPOT_LBL, anchor="mm")
    if spot:
        _grid(dr, spot, s_top + 175, 100, SPOT_NUM, 135)
    else:
        dr.text((W // 2, s_top + 175), "aaj koi nahi", font=font(56), fill=SPOT_LBL, anchor="mm")
    dr.text((W // 2, s_bot + 98), FOOT_GAMES, font=font(62), fill=YELLOW, anchor="mm")
    dr.text((W // 2, s_bot + 208), FOOT_NOTE, font=font(28, bold=False), fill=NOTE, anchor="mm")
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def save_jpg(cstate, date_iso, folder):
    """Locked card ki JPG data/cards/<tarikh>.jpg me (pehle se ho to chhod do). -> path ya None."""
    day = cstate.get("days", {}).get(date_iso)
    if not day:
        return None
    os.makedirs(folder, exist_ok=True)
    p = os.path.join(folder, f"{date_iso}.jpg")
    if not os.path.exists(p):
        tmp = p + ".tmp"
        with open(tmp, "wb") as f:
            f.write(render(date_iso, day["solid"], day["spot"]))
        os.replace(tmp, p)
    return p


def view(cstate, rows, rep, pstate, today=None):
    """App ke liye: aaj ka haal + pichle card."""
    ok, key, why = ready(rows, rep, pstate, today)
    days = cstate.get("days", {})
    cur = days.get(key)
    return {"play_date": key, "bana": bool(cur), "card": cur, "taiyar": ok, "kyun": "card bana (lock)" if cur else why,
            "pichle": [{"date": d, **days[d]} for d in sorted(days, reverse=True)[:30]],
            "dhyan": "Kagaz ka kalpnik puzzle (paper test). Asli paisa nahi, koi salah ya bhavishyavani nahi; ab tak natija random jaisa."}
