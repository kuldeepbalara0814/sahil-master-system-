"""DS (Desawar) ka purana record 1966-2012 satta-xpress.com se uthao -> data/ds_1966_2012.csv  (ek baar chalane ka kaam).

Site par tarikh = Desawar khulne ki tarikh. Hamare record me DS 'pichli tarikh ki line' me likha jata hai (line = khula - 1 din).
CSV: line_date, ds, khula_date. XX / CL (result nahi) chhod diye jate hain.
"""
import csv
import datetime as dt
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "data", "ds_1966_2012.csv")
UA = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36"


def page_url(y):
    return f"https://satta-xpress.com/desawar-satta-chart-record-{y}.php" if y <= 2019 else f"https://satta-xpress.com/desawar-chart-{y}.php"


def parse(html, year):
    html = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    out = {}
    for tr in re.findall(r"<tr.*?</tr>", html, flags=re.S):
        cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.S)]
        if len(cells) >= 13 and cells[0].isdigit():
            for m in range(12):
                v = cells[1 + m]
                if re.fullmatch(r"\d{1,2}", v):
                    try:
                        out[dt.date(year, m + 1, int(cells[0]))] = int(v)
                    except ValueError:
                        pass
    return out


def fetch(y, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(page_url(y), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(3)


def main(y0=1966, y1=2012):
    rows = {}
    for y in range(y0, y1 + 1):
        got = parse(fetch(y), y)
        for d, v in got.items():
            rows[d] = v
        print(y, len(got), flush=True)
        time.sleep(1.2)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["line_date", "ds", "khula_date"])
        for d in sorted(rows):
            w.writerow([(d - dt.timedelta(days=1)).isoformat(), f"{rows[d]:02d}", d.isoformat()])
    print("kul", len(rows), "->", OUT)


if __name__ == "__main__":
    main(*(int(x) for x in sys.argv[1:3]))
