"""GitHub se data files padhna/likhna (Render ka disk restart par mit jaata hai).

Padhna: public repo ho to bina token ke bhi chalta hai (raw.githubusercontent). Likhne ke liye GITHUB_TOKEN chahiye
(fine-grained, sirf is repo par Contents: Read and write).
"""
import base64
import json
import os
import threading
import time
import urllib.error
import urllib.request

from .fetcher import ipv4_first

FILES = ["results.csv", "paper_ledger.json", "friends_snapshot.json", "drift_log.json", "monitor.json", "fetch_log.json", "ideas.json", "boards.json"]
API = os.environ.get("GITHUB_API", "https://api.github.com").rstrip("/")
RAW = os.environ.get("GITHUB_RAW", "https://raw.githubusercontent.com").rstrip("/")


class SyncError(Exception):
    pass


class Sync:
    def __init__(self, local_dir, repo, branch="main", token="", subdir="data", ttl=60):
        self.dir, self.repo, self.branch, self.token, self.subdir, self.ttl = local_dir, repo, branch, token, subdir, ttl
        self.sha, self.last, self.lock = {}, 0.0, threading.RLock()
        os.makedirs(local_dir, exist_ok=True)

    @property
    def can_write(self):
        return bool(self.token)

    def _req(self, method, url, body=None, accept="application/vnd.github+json"):
        h = {"User-Agent": "sahil-lab", "Accept": accept}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        if body is not None:
            h["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, method=method, headers=h)
        try:
            with ipv4_first(), urllib.request.urlopen(req, timeout=25) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()
        except Exception as e:
            raise SyncError(f"GitHub se baat nahi ho payi: {e}")

    def pull(self, force=False):
        with self.lock:
            if not force and time.time() - self.last < self.ttl:
                return
            for name in FILES:
                path = f"{self.subdir}/{name}"
                if self.token:
                    code, body = self._req("GET", f"{API}/repos/{self.repo}/contents/{path}?ref={self.branch}")
                    if code == 200:
                        j = json.loads(body)
                        content = base64.b64decode(j["content"]) if j.get("content") else self._req("GET", j["download_url"])[1]
                        self.sha[name] = j["sha"]
                    elif code == 404:
                        continue
                    else:
                        raise SyncError(f"{name} nahi mili (code {code})")
                else:
                    code, content = self._req("GET", f"{RAW}/{self.repo}/{self.branch}/{path}", accept="*/*")
                    if code == 404:
                        continue
                    if code != 200:
                        raise SyncError(f"{name} nahi mili (code {code})")
                with open(os.path.join(self.dir, name), "wb") as f:
                    f.write(content)
            self.last = time.time()

    def dispatch(self, workflow="daily.yml"):
        """GitHub Action ko haath se chalao (workflow_dispatch). (code, jawab). 204 = chal gaya."""
        if not self.can_write:
            return 0, "GITHUB_TOKEN nahi hai"
        code, body = self._req("POST", f"{API}/repos/{self.repo}/actions/workflows/{workflow}/dispatches", {"ref": self.branch})
        return code, body.decode("utf-8", "replace")[:200]

    def push(self, names, message):
        """Badli hui files GitHub par commit karo (token chahiye)."""
        if not self.can_write:
            raise SyncError("GITHUB_TOKEN set nahi hai, isliye GitHub par save nahi ho sakta.")
        with self.lock:
            for name in names:
                p = os.path.join(self.dir, name)
                if not os.path.exists(p):
                    continue
                path = f"{self.subdir}/{name}"
                for attempt in range(2):
                    if name not in self.sha or attempt:
                        code, body = self._req("GET", f"{API}/repos/{self.repo}/contents/{path}?ref={self.branch}")
                        if code == 200:
                            self.sha[name] = json.loads(body)["sha"]
                        elif code == 404:
                            self.sha.pop(name, None)
                    with open(p, "rb") as f:
                        b = {"message": message, "content": base64.b64encode(f.read()).decode(), "branch": self.branch}
                    if name in self.sha:
                        b["sha"] = self.sha[name]
                    code, body = self._req("PUT", f"{API}/repos/{self.repo}/contents/{path}", b)
                    if code in (200, 201):
                        self.sha[name] = json.loads(body)["content"]["sha"]
                        break
                    if code != 409 or attempt:
                        raise SyncError(f"{name} GitHub par save nahi hui (code {code})")
