#!/usr/bin/env python3
"""Sahil Lab Help ka ASLI jaanch (Termux me chalao). Sarvam ko ek chhota sawaal bhejta hai aur dikhata hai ki jawab aaya ya nahi.

Key kahin likhi nahi jati, screen par nahi aati:
  - SARVAM_API_KEY environment me ho to wahi, warna chhupa kar (typing dikhti nahi) poochta hai.
  - Output me sirf status number, model, URL, token ginti aur jawab ke pehle 220 akshar.
Chalane ka tarika:  git clone https://github.com/kuldeepbalara0814/sahil-master-system-.git && cd sahil-master-system- && python3 scripts/help_selftest.py
(sirf Python3 chahiye, koi pip install nahi)
"""
import getpass
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab import help_bot  # noqa: E402


def main():
    if not os.environ.get("SARVAM_API_KEY", "").strip():
        os.environ["SARVAM_API_KEY"] = getpass.getpass("Sarvam API key (dikhegi nahi): ").strip()
    model = help_bot.model_name()
    url = help_bot.endpoint(model)
    print(f"Model: {model}\nURL  : {url}\nreasoning 'none' bheja jayega: {help_bot.supports_none(model)}")
    q = "Meri Window me pattern number se kaise kholte hain? Chhota jawab do."
    payload = {"model": model, "temperature": 0.2, "max_tokens": 300,
               "messages": [{"role": "system", "content": help_bot.system_prompt("(test)", q)}, {"role": "user", "content": q}]}
    if help_bot.supports_none(model):
        payload["reasoning_effort"] = "none"
    status, resp = help_bot._http_post(url, {"Content-Type": "application/json", "api-subscription-key": os.environ["SARVAM_API_KEY"]}, payload)
    print(f"HTTP status: {status}")
    ans = help_bot._extract(resp) if status == 200 and resp else None
    if ans:
        use = (resp or {}).get("usage") or {}
        print("Usage:", json.dumps({k: use.get(k) for k in ("prompt_tokens", "completion_tokens", "total_tokens")}))
        print("Jawab:", ans[:220].replace("\n", " "))
        print("\nSAB THEEK: key kaam kar rahi hai. Ab Render me SARVAM_API_KEY aur HELP_PIN set karo.")
        return 0
    print("FAIL:", help_bot.upstream_message(status))
    return 1


if __name__ == "__main__":
    sys.exit(main())
