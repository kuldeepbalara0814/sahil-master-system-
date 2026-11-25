#!/usr/bin/env python3
"""PEHREDAAR: galat cheez GitHub tak na pahuche (patterns/014_safeguard/README.md). Sirf padhta hai, kuch badalta nahi.

  python scripts/safeguard.py --base <purana> [--head <naya>] [--tests]   # do commit ke beech ka badlav
  python scripts/safeguard.py --base HEAD --head WORKTREE --records-only  # roz ki Action: record to nahi badla?
Exit 1 = ROKO. Jaanbujh kar record sudharna ho: ALLOW_DATA_EDIT=1."""
import argparse
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDS = ("data/results.csv", "data/ds_1966_2012.csv", "sahil_system/lifetime_record.txt")      # purani line kabhi na badle / hate
PROTECTED_DIRS = ("data/", "sahil_system/")
MAX_BYTES = 2_000_000
BAD_NAMES = re.compile(r"(^|/)(\.env(\..*)?|id_rsa.*|id_ed25519.*|.*\.pem|.*\.key|.*\.p12|credentials[^/]*\.json|selfcheck_report\.json)$")
SECRETS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\b(ghp|gho|ghs|ghu)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
    ("API key (sk_)", re.compile(r"\bsk[_-][A-Za-z0-9_-]{20,}\b")),
    ("AWS key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("PIN/key/password seedha likha", re.compile(r"\b(SARVAM_API_KEY|HELP_PIN|ADMIN_PIN|GITHUB_TOKEN)\b\s*[=:]\s*[\"']?(?!\$|\{|<|os\.|sync|secrets)[A-Za-z0-9_\-]{4,}[\"']?\s*($|#)")),
]
bad, warn = [], []


def git(*args, binary=False):
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True)
    return (r.returncode, r.stdout if binary else r.stdout.decode("utf-8", "replace"))


def read(rev, path):
    if rev == "WORKTREE":
        try:
            with open(os.path.join(ROOT, path), "rb") as f:
                return f.read()
        except OSError:
            return None
    code, out = git("show", f"{rev}:{path}", binary=True)
    return out if code == 0 else None


def changed(base, head):
    """[(status, path)] - A/M/D."""
    args = ["diff", "--name-status", "--no-renames", base] + ([] if head == "WORKTREE" else [head])
    code, out = git(*args)
    if code:
        bad.append(f"git diff nahi chala ({base}..{head}): pehle 'git pull' karo")
        return []
    return [tuple(x.split("\t", 1)) for x in out.splitlines() if "\t" in x]


def lines(blob):
    return [x.strip() for x in (blob or b"").decode("utf-8", "replace").splitlines() if x.strip() and not x.startswith("#")]


def check_records(base, head):
    for path in RECORDS:
        old, new = read(base, path), read(head, path)
        if old is None:
            continue
        if new is None:
            bad.append(f"RECORD mit raha hai: {path}")
            continue
        have = set(lines(new))
        gone = [x for x in lines(old) if x not in have]
        if gone:
            msg = f"RECORD ki {len(gone)} purani line badli/hati: {path} (jaise: {gone[0][:60]})"
            (warn if os.environ.get("ALLOW_DATA_EDIT") == "1" else bad).append(msg)


def check_files(base, head, files):
    for status, path in files:
        if status == "D":
            if path.startswith(PROTECTED_DIRS) and os.environ.get("ALLOW_DATA_EDIT") != "1":
                bad.append(f"data file delete ho rahi hai: {path}")
            continue
        if BAD_NAMES.search(path):
            bad.append(f"ye file repo me nahi jani chahiye: {path}")
        blob = read(head, path)
        if blob is None:
            continue
        if len(blob) > MAX_BYTES:
            bad.append(f"bahut badi file ({len(blob) // 1024} KB): {path}")
        old = set((read(base, path) or b"").decode("utf-8", "replace").splitlines())
        added = [x for x in blob.decode("utf-8", "replace").splitlines() if x not in old]
        for name, rx in SECRETS:
            if not path.startswith("tests/") and any(rx.search(x) for x in added):
                bad.append(f"chhupi cheez lag rahi hai ({name}): {path}")          # asli value print nahi karte
        if path.startswith("lab_static/") and any(re.search(r"\bsatta\b(?!-king)", x, re.I) for x in added):
            warn.append(f"app me 'satta' shabd: {path}")


def check_code(head, files):
    todo = [p for s, p in files if s != "D"]
    with tempfile.TemporaryDirectory() as tmp:
        for path in todo:
            blob = read(head, path)
            if blob is None or not path.endswith((".py", ".js", ".json", ".yml", ".yaml")):
                continue
            p = os.path.join(tmp, "f" + os.path.splitext(path)[1])
            with open(p, "wb") as f:
                f.write(blob)
            try:
                if path.endswith(".py"):
                    py_compile.compile(p, doraise=True, cfile=p + "c")
                elif path.endswith(".json"):
                    json.loads(blob.decode("utf-8"))
                elif path.endswith(".js") and shutil.which("node") and path.startswith("lab_static/"):
                    r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
                    if r.returncode:
                        bad.append(f"JavaScript tuta: {path}: {r.stderr.strip().splitlines()[-1][:120]}")
                elif path.endswith((".yml", ".yaml")):
                    try:
                        import yaml
                        yaml.safe_load(blob.decode("utf-8"))
                    except ImportError:
                        pass
            except Exception as e:
                bad.append(f"file tuti hai: {path}: {type(e).__name__}: {str(e)[:120]}")
    ruff = shutil.which("ruff") or os.path.join(os.path.dirname(sys.executable), "ruff")
    if os.path.exists(ruff):
        r = subprocess.run([ruff, "check", "--no-cache", "--output-format", "concise", "."], cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            bad.append("ruff (asli bug): " + " | ".join(r.stdout.strip().splitlines()[:3]))
    else:
        warn.append("ruff nahi mila (pip install ruff)")


def run_script(label, *args):
    r = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        out = [x for x in (r.stderr + r.stdout).splitlines() if x.startswith(("FAIL:", "ERROR:", "  [error]"))]
        bad.append(f"{label} fail: " + " | ".join(out[:5] or (r.stderr or r.stdout).strip().splitlines()[-2:]))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sahil Lab pehredaar")
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--tests", action="store_true")
    ap.add_argument("--records-only", action="store_true")
    a = ap.parse_args(argv)
    bad.clear()
    warn.clear()
    check_records(a.base, a.head)
    if not a.records_only:
        files = changed(a.base, a.head)
        check_files(a.base, a.head, files)
        check_code(a.head, files)
        run_script("data jaanch", os.path.join("scripts", "selfcheck.py"), "--data", "--no-file")
        if a.tests and any(not p.startswith(("data/", "patterns/", "research/")) and not p.endswith(".md") for _, p in files):
            run_script("tests", "-m", "unittest", "tests.test_lab", "tests.test_core", "tests.test_fetcher", "tests.test_paper", "tests.test_server")
    for w in warn:
        print("  dhyan:", w)
    for b in bad:
        print("  ROKA:", b)
    print("PEHREDAAR:", "ROKA (push mat karo)" if bad else "THEEK")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
