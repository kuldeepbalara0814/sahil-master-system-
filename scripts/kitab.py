#!/usr/bin/env python3
"""patterns/AUTO_INDEX.md code se apne aap banata hai (files, pattern, API, data, tools, tests). Hath se mat badlo.
  python scripts/kitab.py           # taaza karo
  python scripts/kitab.py --check   # purani ho to exit 1"""
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "patterns", "AUTO_INDEX.md")


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def first_line(*p):
    doc = ast.get_docstring(ast.parse(read(*p))) or "(likha nahi)"
    return doc.strip().split("\n")[0].replace("|", "/")


def build():
    out = ["# AUTO INDEX (scripts/kitab.py ne banaya; hath se mat badlo)", "", "## Pattern folders", ""]
    pdir = os.path.join(ROOT, "patterns")
    for d in sorted(x for x in os.listdir(pdir) if os.path.isfile(os.path.join(pdir, x, "README.md"))):
        out.append(f"- `{d}`: {read('patterns', d, 'README.md').splitlines()[0].lstrip('# ').strip()}")
    out += ["", "## Code (har file ka kaam)", "", "| File | Kaam |", "|---|---|", f"| lab_server.py | {first_line('lab_server.py')} |"]
    for folder in ("lab", "scripts"):
        for n in sorted(os.listdir(os.path.join(ROOT, folder))):
            if n.endswith(".py"):
                out.append(f"| {folder}/{n} | {first_line(folder, n)} |")
    out.append("| lab_static/ | " + ", ".join(sorted(n for n in os.listdir(os.path.join(ROOT, "lab_static")) if n.endswith(".js"))) + " |")
    server = read("lab_server.py")
    out += ["", "## API raaste", "", ", ".join(f"`{p}`" for p in sorted(set(re.findall(r'@app\.(?:get|post|route)\("([^"]+)"', server))))]
    gh = read("lab", "gh.py")
    files = re.findall(r'"([^"]+\.(?:json|csv))"', gh[gh.index("\nFILES = "):].split("\n")[1])
    out += ["", "## Data files (app GitHub se sync karti hai)", "", ", ".join(f"`{f}`" for f in files)]
    names = re.findall(r'Tool\("([a-z0-9_]+)"', server + read("lab", "mcp_tools.py"))
    out += ["", "## Connector tools", "", ", ".join(f"`{n}`" for n in sorted(set(names)))]
    out += ["", "## Tests", ""]
    for n in sorted(os.listdir(os.path.join(ROOT, "tests"))):
        if n.startswith("test_") and n.endswith(".py"):
            out.append(f"- `tests/{n}`: {len(re.findall(r'^    def test_', read('tests', n), re.M))} test")
    items = re.findall(r"^(\d+)\.\s+\*\*(.+?)\*\*", read("patterns", "HANDOFF.md"), re.M)
    out += ["", f"## HANDOFF ke aakhri faisle (kul {items[-1][0] if items else 0})", ""]
    out += [f"- {n}. {t[:150]}" for n, t in items[-12:]]
    return "\n".join(out) + "\n"


def main(argv):
    new = build()
    old = read("patterns", "AUTO_INDEX.md") if os.path.exists(OUT) else ""
    if "--check" in argv:
        print("AUTO_INDEX taaza hai" if new == old else "AUTO_INDEX purani hai: python scripts/kitab.py chalao")
        return 0 if new == old else 1
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(new)
    print("likha:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
