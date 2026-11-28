"""Sahil Lab ka MCP endpoint (Claude ke custom connector ke liye).

Kya hai: Claude (claude.ai > Customize > Connectors > Add custom connector) is pate se baat karta hai:
    https://<site>/mcp/<MCP_KEY>
Ye "Streamable HTTP" MCP ka sabse saada roop hai: har POST me ek JSON-RPC sandesh, jawab seedha JSON me
(koi SSE stream nahi, koi session nahi). Bahar ki koi library nahi chahiye.

Sirf PADHNE wale tool: koi bet, fetch, save ya GitHub push yahan se nahi hota.
Tool khud lab_server.py me bante hain (wahan data aur cache hai); ye file sirf protocol sambhalti hai.
"""
import hmac
import json

# Jo MCP versions ye server samajhta hai (naya pehle). Client jo maange, wo is list me ho to wahi lautao.
VERSIONS = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]
SERVER_INFO = {"name": "sahil-lab", "title": "Sahil Lab (kagaz ka puzzle khel)", "version": "1.1"}
INSTRUCTIONS = ("Sahil Lab ek KAGAZ KA KALPNIK PUZZLE KHEL hai (paper trading testing; asli paisa nahi). Har jawab me ye saaf rakho: "
                "ise asli khel, salah ya bhavishyavani na samjho; ab tak natija random jaisa hai. Jawab saral Hinglish me, jodi do ankon me (07). "
                "Ek request_likho ke alawa saare tools sirf padhte hain: sehat, results, aaj ki list/tokri, do list ki tulna, jodi khojo, naksha, card 007, din ka natija, "
                "kagaz pocket, error jaanch, guide. Bug, idea ya badlav ho to user se poochh kar request_likho se likho (public repo me jata hai: key/PIN kabhi nahi); Ruflo (Claude Code) jaanch kar user ki haan ke baad badlega. requests_dekho se haal pata karo. "
                "Free server so jata hai, isliye pehla jawab der se aa sakta hai; fail ho to ek baar dobara poochho.")
MAX_TEXT = 60000          # ek jawab ki had (characters), taaki Claude ke context me bahut bada data na jaye
MIN_KEY = 24              # isse chhoti key ho to endpoint band (andaza lagane layak key na chale)

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS, INTERNAL_ERROR = -32700, -32600, -32601, -32602, -32603


class Tool:
    """Ek tool: naam, Claude ke liye samjhane wali line, input ka JSON schema, aur chalane wala function.
    write=True sirf request box ke liye (baaki sab sirf padhte hain)."""

    def __init__(self, name, title, description, fn, properties=None, required=None, write=False):
        self.name, self.title, self.description, self.fn, self.write = name, title, description, fn, write
        self.schema = {"type": "object", "properties": properties or {}, "additionalProperties": False}
        if required:
            self.schema["required"] = list(required)

    def spec(self):
        return {"name": self.name, "title": self.title, "description": self.description, "inputSchema": self.schema,
                "annotations": {"title": self.title, "readOnlyHint": not self.write, "destructiveHint": False,
                                "idempotentHint": not self.write, "openWorldHint": False}}


def key_ok(given, expected):
    """URL wali key sahi hai? expected na ho ya chhoti ho to hamesha nahi (endpoint band)."""
    if not expected or len(expected) < MIN_KEY:
        return False
    return hmac.compare_digest((given or "").encode(), expected.encode())


def _err(mid, code, msg):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": msg}}


def _ok(mid, result):
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def _text(obj):
    t = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, default=str, separators=(",", ":"))
    if len(t) > MAX_TEXT:
        t = t[:MAX_TEXT] + " ...[jawab bahut lamba tha, yahan kaat diya]"
    return t


def _check_args(tool, args):
    """Halki jaanch: anjaan naam nahi, zaroori naam maujood, int/string ka type sahi."""
    props = tool.schema["properties"]
    for k in args:
        if k not in props:
            return f"'{k}' is tool ka input nahi hai"
    for k in tool.schema.get("required", []):
        if k not in args:
            return f"'{k}' chahiye"
    for k, v in args.items():
        t = props[k].get("type")
        if t == "integer" and (not isinstance(v, int) or isinstance(v, bool)):
            return f"'{k}' poora number hona chahiye"
        if t == "string" and not isinstance(v, str):
            return f"'{k}' text hona chahiye"
        if t == "integer" and ("minimum" in props[k] and v < props[k]["minimum"] or "maximum" in props[k] and v > props[k]["maximum"]):
            return f"'{k}' {props[k].get('minimum')} se {props[k].get('maximum')} ke beech ho"
    return None


def _one(msg, tools, log=None):
    """Ek JSON-RPC sandesh. Notification (bina id) ka jawab None."""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
        if isinstance(msg, dict) and "method" not in msg and ("result" in msg or "error" in msg):
            return None                                        # client ka jawab (hum kuch poochhte nahi), chhod do
        return _err(msg.get("id") if isinstance(msg, dict) else None, INVALID_REQUEST, "Galat JSON-RPC sandesh")
    method, mid, params = msg["method"], msg.get("id"), msg.get("params") or {}
    if "id" not in msg:                                        # notifications/initialized, cancelled waghaira
        return None
    if not isinstance(params, dict):
        return _err(mid, INVALID_PARAMS, "params object hona chahiye")
    if method == "initialize":
        asked = params.get("protocolVersion")
        return _ok(mid, {"protocolVersion": asked if asked in VERSIONS else VERSIONS[0],
                         "capabilities": {"tools": {"listChanged": False}},
                         "serverInfo": SERVER_INFO, "instructions": INSTRUCTIONS})
    if method == "ping":
        return _ok(mid, {})
    if method == "tools/list":
        return _ok(mid, {"tools": [t.spec() for t in tools.values()]})
    if method == "tools/call":
        tool = tools.get(params.get("name"))
        if tool is None:
            return _err(mid, INVALID_PARAMS, f"Anjaan tool: {params.get('name')}")
        args = params.get("arguments") or {}
        if not isinstance(args, dict):
            return _err(mid, INVALID_PARAMS, "arguments object hona chahiye")
        bad = _check_args(tool, args)
        if bad:
            return _ok(mid, {"content": [{"type": "text", "text": bad}], "isError": True})
        try:
            out = tool.fn(**args)
        except Exception as e:                                 # tool ki galti Claude ko dikhe, server na gire
            if log:
                log(tool.name, e)
            return _ok(mid, {"content": [{"type": "text", "text": f"Tool me galti: {type(e).__name__}: {str(e)[:200]}"}], "isError": True})
        return _ok(mid, {"content": [{"type": "text", "text": _text(out)}], "isError": False})
    return _err(mid, METHOD_NOT_FOUND, f"Ye method nahi hai: {method}")


def handle(raw, tools, log=None):
    """POST body (bytes/str) -> (HTTP status, jawab ka JSON ya None). None + 202 = sirf notification aayi thi."""
    try:
        msg = json.loads(raw or b"")
    except (ValueError, UnicodeDecodeError):
        return 400, _err(None, PARSE_ERROR, "JSON padha nahi gaya")
    if isinstance(msg, list):                                  # purane (2025-03-26) client batch bhej sakte hain
        if not msg:
            return 400, _err(None, INVALID_REQUEST, "Khali batch")
        outs = [o for o in (_one(m, tools, log) for m in msg) if o is not None]
        return (200, outs) if outs else (202, None)
    out = _one(msg, tools, log)
    if out is None:
        return 202, None
    return (400 if out.get("error", {}).get("code") in (INVALID_REQUEST, PARSE_ERROR) else 200), out
