"""healthchecks.io jaisi 'zinda ho?' ghanti: HEALTHCHECK_URL (Render env / GitHub secret) ho to har update ke baad ping.
Ping na aaye (ya /fail aaye) to wo service email karti hai. URL na ho to kuch nahi hota. URL repo me kabhi nahi."""
import os
import urllib.request


def ping(ok=True):
    url = os.environ.get("HEALTHCHECK_URL", "").strip().rstrip("/")
    if not url.startswith("https://"):
        return False
    try:
        with urllib.request.urlopen(urllib.request.Request(url + ("" if ok else "/fail"), headers={"User-Agent": "sahil-lab"}), timeout=10):
            return True
    except Exception:                       # ghanti na baje to update nahi rukna chahiye
        return False
