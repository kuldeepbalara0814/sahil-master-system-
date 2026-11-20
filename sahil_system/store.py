"""GitHub-backed storage.

Render free par disk restart par mit jaata hai, isliye asli data GitHub repo me
rehta hai (sahil_system/lifetime_record.txt aadi). Local files sirf cache hain.
GITHUB_TOKEN set nahi ho to local mode: files seedha disk par (dev/test ke liye).
"""
import base64
import json
import os
import threading
import time
import urllib.error
import urllib.request

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
FILES = ["lifetime_record.txt", "prediction_history.json", "pending_result.json"]
SUBDIR = "sahil_system"
REPO = os.environ.get("GITHUB_REPO", "kuldeepbalara0814/sahil-master-system-")
BRANCH = os.environ.get("GITHUB_BRANCH", "main")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = os.environ.get("GITHUB_API", "https://api.github.com").rstrip("/")
TTL = 45  # seconds: itne der baad GitHub se dobara pull

_sha = {}
_last_pull = 0.0
_lock = threading.RLock()


class StoreError(Exception):
    pass


def enabled():
    return bool(TOKEN)


def _local(name):
    return os.path.join(DATA_DIR, name)


def _request(method, name, body=None):
    url = f"{API}/repos/{REPO}/contents/{SUBDIR}/{name}"
    if method == "GET":
        url += f"?ref={BRANCH}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "sahil-system",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode())
        except Exception:
            payload = {}
        return e.code, payload
    except Exception as e:
        raise StoreError(f"GitHub se baat nahi ho payi: {e}")


def pull(force=False):
    """GitHub ki files local cache me utaro."""
    global _last_pull
    if not enabled():
        return
    with _lock:
        if not force and time.time() - _last_pull < TTL:
            return
        for name in FILES:
            code, payload = _request("GET", name)
            if code == 200:
                content = base64.b64decode(payload["content"])
                with open(_local(name), "wb") as f:
                    f.write(content)
                _sha[name] = payload["sha"]
            elif code == 404:
                _sha.pop(name, None)
                if os.path.exists(_local(name)):
                    os.remove(_local(name))
            else:
                raise StoreError(f"GitHub se {name} nahi mili (code {code}): {payload.get('message', '')}")
        _last_pull = time.time()


def _read(name):
    p = _local(name)
    if not os.path.exists(p):
        return None
    with open(p, "rb") as f:
        return f.read()


def snapshot():
    """Sab files ka abhi ka content (change pehchanne ke liye)."""
    return {n: _read(n) for n in FILES}


def push_changes(before, message):
    """Jo files before se alag hain unhe GitHub par commit karo."""
    if not enabled():
        return []
    pushed = []
    with _lock:
        for name in FILES:
            now = _read(name)
            if now is None or now == before.get(name):
                continue
            body = {
                "message": message,
                "content": base64.b64encode(now).decode(),
                "branch": BRANCH,
            }
            if name in _sha:
                body["sha"] = _sha[name]
            code, payload = _request("PUT", name, body)
            if code not in (200, 201):
                raise StoreError(f"{name} GitHub par save nahi hui (code {code}): {payload.get('message', '')}")
            _sha[name] = payload["content"]["sha"]
            pushed.append(name)
    return pushed


def restore(before):
    """Push fail ho to local cache purani halat par wapas."""
    for name, content in before.items():
        p = _local(name)
        if content is None:
            if os.path.exists(p):
                os.remove(p)
        else:
            with open(p, "wb") as f:
                f.write(content)


def write_op(fn, message):
    """Safe write: taaza pull -> kaam -> GitHub par commit. Fail par rollback."""
    with _lock:
        pull(force=True)
        before = snapshot()
        try:
            result = fn()
            push_changes(before, message)
            return result
        except Exception:
            restore(before)
            raise
