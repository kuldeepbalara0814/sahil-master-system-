#!/usr/bin/env python3
"""README ki photo asli data se banata hai: docs/photo/ me naksha chart, card 007 chart aur roz ka card.
  python scripts/photo.py        (code ya dikhawat badle to dobara chalao)"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from lab import card, data, export_all, scanner  # noqa: E402

OUT = os.path.join(ROOT, "docs", "photo")


def main(out=OUT):
    os.makedirs(out, exist_ok=True)
    rows = data.load()
    rep = scanner.run(rows)
    done = []
    for key, name in (("naksha", "naksha.png"), ("steps", "puzzle_steps.png")):
        items = next((p["items"] for p in rep["patterns"] if p["key"] == key), [])
        it = next((i for i in items if i.get("status") == "aaj" and i.get("targets")), items[0] if items else None)
        if it:
            export_all.draw_pattern(1, it, export_all.safe_view(rows, it)).save(os.path.join(out, name), optimize=True)
            done.append(name)
    try:
        with open(os.path.join(ROOT, "data", "cards.json"), encoding="utf-8") as f:
            days = json.load(f)["days"]
        last = max(days)
        with open(os.path.join(out, "roz_ka_card.jpg"), "wb") as f:
            f.write(card.render(last, days[last]["solid"], days[last]["spot"], quality=85))
        done.append("roz_ka_card.jpg")
    except (OSError, ValueError, KeyError):
        print("card abhi nahi bana: card ki photo chhodi")
    print("photo:", ", ".join(done), "->", out)
    return done


if __name__ == "__main__":
    main()
