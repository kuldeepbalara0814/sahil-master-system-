"""GitHub se data files padhna/likhna (Render ka disk restart par mit jaata hai).

Padhna: public repo ho to bina token ke bhi chalta hai (raw.githubusercontent). Likhne ke liye GITHUB_TOKEN chahiye
(fine-grained, sirf is repo par Contents: Read and write).
"""
import base64
import hashlib
import json
import os
import threading
import time
import urllib.error
import urllib.request

from .fetcher import ipv4_first

FILES = ["results.csv", "paper_ledger.json", "friends_snapshot.json", "drift_log.json", "monitor.json", "fetch_log.json", "ideas.json", "boards.json", "patterns_today.json", "play_log.json", "active_log.json", "hit_log.json", "review_log.json", "manual_results.json", "window_log.json", "help_requests.json", "partial_results.json", "alerts.json"]
API = os.environ.get("GITHUB_API", "https://api.github.com").rstrip("/")
RAW = os.environ.get("GITHUB_RAW", "https://raw.githubusercontent.com").rstrip("/")


# aap ke haath se dali / dabayi cheezein: takraav me inhe bachana hai
USER_FILES = {"manual_results.json", "help_requests.json", "ideas.json", "boards.json", "play_log.json", "review_log.json", "paper_ledger.json"}


class SyncError(Exception):
    pass


def blob_sha(content):
    """Git jaisa file-sha (GitHub Contents API ka 'sha')."""
    return hashlib.sha1(b"blob %d\0" % len(content) + content).hexdigest()


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

    def _local(self, name):
        try:
            with open(os.path.join(self.dir, name), "rb") as f:
                return f.read()
        except OSError:
            return None

    def _write(self, name, content):
        """Atomic: aadhi likhi file kabhi koi padh na paye."""
        p = os.path.join(self.dir, name)
        tmp = f"{p}.{os.getpid()}.{threading.get_ident()}.sync"
        with open(tmp, "wb") as f:
            f.write(content)
        os.replace(tmp, p)

    def _fetch(self, name):
        """GitHub wali file: (content, sha) ya None (file nahi hai)."""
        path = f"{self.subdir}/{name}"
        if self.token:
            code, body = self._req("GET", f"{API}/repos/{self.repo}/contents/{path}?ref={self.branch}")
            if code == 404:
                return None
            if code != 200:
                raise SyncError(f"{name} nahi mili (code {code})")
            j = json.loads(body)
            if j.get("content"):
                return base64.b64decode(j["content"]), j["sha"]
            code, content = self._req("GET", j["download_url"])
            if code != 200:
                raise SyncError(f"{name} nahi mili (code {code})")
            return content, j["sha"]
        code, content = self._req("GET", f"{RAW}/{self.repo}/{self.branch}/{path}", accept="*/*")
        if code == 404:
            return None
        if code != 200:
            raise SyncError(f"{name} nahi mili (code {code})")
        return content, blob_sha(content)

    def pull(self, force=False):
        """GitHub se taaza files. Local file sirf tab badalti hai jab GitHub wali file pichhli baar se badli ho -
        isliye local par likha (abhi push na hua) kaam purane se nahi dabta."""
        with self.lock:
            if not force and time.time() - self.last < self.ttl:
                return
            for name in FILES:
                got = self._fetch(name)
                if got is None:
                    continue
                content, sha = got
                if self.sha.get(name) == sha and self._local(name) is not None:
                    continue
                self._write(name, content)
                self.sha[name] = sha
            self.last = time.time()

    def dispatch(self, workflow="daily.yml"):
        """GitHub Action ko haath se chalao (workflow_dispatch). (code, jawab). 204 = chal gaya."""
        if not self.can_write:
            return 0, "GITHUB_TOKEN nahi hai"
        code, body = self._req("POST", f"{API}/repos/{self.repo}/actions/workflows/{workflow}/dispatches", {"ref": self.branch})
        return code, body.decode("utf-8", "replace")[:200]

    def push(self, names, message):
        """Sirf badli hui files GitHub par commit karo (token chahiye). Takraav (409: beech me kisi aur ne badla) ho to
        aap ke haath se dali files (USER_FILES) aap ki hi jati hain; apne aap banne wali files me GitHub wali (nayi) rehti hai."""
        if not self.can_write:
            raise SyncError("GITHUB_TOKEN set nahi hai, isliye GitHub par save nahi ho sakta.")
        with self.lock:
            for name in names:
                data = self._local(name)
                if data is None or self.sha.get(name) == blob_sha(data):          # badli hi nahi: khali commit nahi
                    continue
                path = f"{self.subdir}/{name}"
                if name not in self.sha:
                    code, body = self._req("GET", f"{API}/repos/{self.repo}/contents/{path}?ref={self.branch}")
                    if code == 200:
                        self.sha[name] = json.loads(body)["sha"]
                for attempt in range(2):
                    b = {"message": message, "content": base64.b64encode(data).decode(), "branch": self.branch}
                    if name in self.sha:
                        b["sha"] = self.sha[name]
                    code, body = self._req("PUT", f"{API}/repos/{self.repo}/contents/{path}", b)
                    if code in (200, 201):
                        self.sha[name] = json.loads(body)["content"]["sha"]
                        break
                    if code not in (409, 422) or attempt:
                        raise SyncError(f"{name} GitHub par save nahi hui (code {code})")
                    got = self._fetch(name)
                    if got is None:
                        self.sha.pop(name, None)
                        continue
                    content, sha = got
                    self.sha[name] = sha
                    if name not in USER_FILES:
                        self._write(name, content)
                        break
