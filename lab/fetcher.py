"""satta-king-fast.com ke mahine ke chart se nayi lines laana.

Site ka niyam: DSWR column me DS us tarikh par dikhta hai jis tarikh subah khula (agli subah 5:30).
Isliye  line(d) = FD,GB,GL (site ki tarikh d)  +  DS (site ki tarikh d+1).
Mahine ka aakhri din chhuti: us din FD/GB/GL = XX, par DS dikhta hai (pichle din ki line ka).
"""
import datetime as dt
import html as _html
import re
import time
import urllib.request

from . import data

URL = "https://satta-king-fast.com/chart.php?ResultFor={name}-{year}&month={month:02d}&year={year}"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


class FetchError(Exception):
    pass


def month_url(y, m):
    return URL.format(name=MONTHS[m - 1], year=y, month=m)


def fetch_month(y, m, timeout=40, retries=2):
    last = None
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(month_url(y, m), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:            # network ya site ki galti
            last = e
            time.sleep(2 * (i + 1))
    raise FetchError(f"{y}-{m:02d} ka page nahi aaya: {last}")


def _num(s):
    s = s.strip()
    if not re.fullmatch(r"\d{1,3}", s):
        return None                       # XX ya khaali
    v = int(s)
    return 0 if v == 100 else (v if 0 <= v <= 99 else None)


def parse_month(page, y, m):
    """{date: dict(ds,fd,gb,gl)}  (None = abhi result nahi / chhuti)."""
    tables = re.findall(r"<table.*?</table>", page, re.S)
    tb = next((t for t in tables if "DSWR" in t), None)
    if tb is None:
        raise FetchError(f"{y}-{m:02d}: chart table nahi mili (site badal gayi ya rok lagi?)")
    out = {}
    for tr in re.findall(r"<tr.*?</tr>", tb, re.S):
        cells = [re.sub(r"\s+", " ", _html.unescape(re.sub(r"<.*?>", "", c))).strip() for c in re.findall(r"<t[hd].*?</t[hd]>", tr, re.S)]
        if len(cells) == 5 and re.fullmatch(r"\d{1,2}", cells[0]):
            try:
                d = dt.date(y, m, int(cells[0]))
            except ValueError:
                continue
            out[d] = dict(ds=_num(cells[1]), fd=_num(cells[2]), gb=_num(cells[3]), gl=_num(cells[4]))
    if not out:
        raise FetchError(f"{y}-{m:02d}: chart khaali")
    return out


def build_lines(site):
    """site = {date: {...}} -> [(date, [fd,gb,gl,ds], 'site')] sirf poori lines."""
    lines = []
    for d in sorted(site):
        s = site[d]
        if None in (s["fd"], s["gb"], s["gl"]):
            continue                      # chhuti ya aaj ka result abhi nahi
        nx = site.get(d + dt.timedelta(days=1))
        if not nx or nx["ds"] is None:
            continue                      # DS agli subah aata hai
        lines.append((d, [s["fd"], s["gb"], s["gl"], nx["ds"]], "site"))
    return lines


def months_between(a, b):
    y, m = a.year, a.month
    out = []
    while (y, m) <= (b.year, b.month):
        out.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def new_lines(rows, today=None, fetch=fetch_month, pause=1.5):
    """Aakhri line ke baad ki nayi lines (site se). Return (lines, info)."""
    today = today or dt.date.today()
    last = rows[-1][0]
    site, info = {}, {"months": [], "errors": []}
    for (y, m) in months_between(last, max(today, last)):
        try:
            site.update(parse_month(fetch(y, m), y, m))
            info["months"].append(f"{y}-{m:02d}")
        except FetchError as e:
            info["errors"].append(str(e))
        if pause:
            time.sleep(pause)
    return [ln for ln in build_lines(site) if ln[0] > last], info
