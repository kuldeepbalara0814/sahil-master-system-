"""MCP endpoint (Claude connector) ki jaanch: protocol, key, aur sabse zaroori: koi tool kuch likhta nahi."""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from lab import mcp_endpoint  # noqa: E402

KEY = "k" * 32                                                  # sirf test ki nakli key


def rpc(method, params=None, mid=1):
    m = {"jsonrpc": "2.0", "method": method, "id": mid}
    if params is not None:
        m["params"] = params
    return json.dumps(m)


class ProtocolTests(unittest.TestCase):
    """Bina Flask: sirf protocol."""

    def setUp(self):
        self.tools = {"jod": mcp_endpoint.Tool("jod", "Jod", "Do number jodo", lambda a, b=0: {"jod": a + b},
                                               {"a": {"type": "integer", "minimum": 0, "maximum": 99}, "b": {"type": "integer"}}, ["a"]),
                      "toota": mcp_endpoint.Tool("toota", "Toota", "Hamesha galti", lambda: 1 / 0)}

    def test_key(self):
        self.assertTrue(mcp_endpoint.key_ok(KEY, KEY))
        self.assertFalse(mcp_endpoint.key_ok("galat" + KEY[5:], KEY))
        self.assertFalse(mcp_endpoint.key_ok("", ""))            # key set nahi = band
        self.assertFalse(mcp_endpoint.key_ok("chhoti", "chhoti"))  # chhoti key = band

    def test_initialize_and_list(self):
        code, out = mcp_endpoint.handle(rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                                           "clientInfo": {"name": "t", "version": "1"}}), self.tools)
        self.assertEqual(code, 200)
        self.assertEqual(out["result"]["protocolVersion"], "2025-06-18")
        self.assertIn("tools", out["result"]["capabilities"])
        code, out = mcp_endpoint.handle(rpc("initialize", {"protocolVersion": "1999-01-01"}), self.tools)
        self.assertEqual(out["result"]["protocolVersion"], mcp_endpoint.VERSIONS[0])
        code, out = mcp_endpoint.handle(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}), self.tools)
        self.assertEqual((code, out), (202, None))
        code, out = mcp_endpoint.handle(rpc("tools/list"), self.tools)
        names = [t["name"] for t in out["result"]["tools"]]
        self.assertEqual(names, ["jod", "toota"])
        self.assertTrue(all(t["annotations"]["readOnlyHint"] for t in out["result"]["tools"]))
        self.assertEqual(mcp_endpoint.handle(rpc("ping"), self.tools)[1]["result"], {})

    def test_call(self):
        out = mcp_endpoint.handle(rpc("tools/call", {"name": "jod", "arguments": {"a": 2, "b": 3}}), self.tools)[1]
        self.assertFalse(out["result"]["isError"])
        self.assertEqual(json.loads(out["result"]["content"][0]["text"]), {"jod": 5})
        for bad in ({"b": 1}, {"a": "2"}, {"a": 200}, {"a": 1, "c": 1}, {"a": True}):
            out = mcp_endpoint.handle(rpc("tools/call", {"name": "jod", "arguments": bad}), self.tools)[1]
            self.assertTrue(out["result"]["isError"], bad)
        out = mcp_endpoint.handle(rpc("tools/call", {"name": "toota"}), self.tools)[1]
        self.assertTrue(out["result"]["isError"])
        self.assertIn("ZeroDivisionError", out["result"]["content"][0]["text"])
        out = mcp_endpoint.handle(rpc("tools/call", {"name": "nahi_hai"}), self.tools)[1]
        self.assertEqual(out["error"]["code"], mcp_endpoint.INVALID_PARAMS)

    def test_bad_input(self):
        self.assertEqual(mcp_endpoint.handle(b"{tuta", self.tools)[1]["error"]["code"], mcp_endpoint.PARSE_ERROR)
        self.assertEqual(mcp_endpoint.handle(json.dumps({"id": 1}), self.tools)[0], 400)
        self.assertEqual(mcp_endpoint.handle(rpc("resources/list"), self.tools)[1]["error"]["code"], mcp_endpoint.METHOD_NOT_FOUND)
        code, out = mcp_endpoint.handle(json.dumps([json.loads(rpc("ping", mid=1)), json.loads(rpc("ping", mid=2))]), self.tools)
        self.assertEqual((code, [o["id"] for o in out]), (200, [1, 2]))
        self.assertEqual(mcp_endpoint.handle("[]", self.tools)[0], 400)

    def test_long_text_is_cut(self):
        t = mcp_endpoint._text("x" * (mcp_endpoint.MAX_TEXT + 10))
        self.assertLess(len(t), mcp_endpoint.MAX_TEXT + 100)


class RouteTests(unittest.TestCase):
    """Asli Flask route aur asli tool, repo ke data ki copy par."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        os.environ.setdefault("LAB_DATA_DIR", cls.tmp)          # test_server pehle import kar chuka ho to wahi dir chalega
        os.environ.setdefault("LAB_SYNC", "0")
        import lab_server
        cls.s = lab_server
        os.makedirs(lab_server.DATA_DIR, exist_ok=True)        # pichle test ne dir mita diya ho to data dobara rakho
        for f in os.listdir(os.path.join(ROOT, "data")):
            if f.endswith((".csv", ".json")) and not os.path.exists(os.path.join(lab_server.DATA_DIR, f)):
                shutil.copy(os.path.join(ROOT, "data", f), lab_server.DATA_DIR)
        cls.old_key, lab_server.MCP_KEY = lab_server.MCP_KEY, KEY
        cls.c = lab_server.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.s.MCP_KEY = cls.old_key
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def post(self, body, key=KEY):
        return self.c.post(f"/mcp/{key}", data=body, content_type="application/json",
                           headers={"Accept": "application/json, text/event-stream"})

    def snapshot(self):
        d = self.s.DATA_DIR
        out = {}
        for f in sorted(os.listdir(d)):
            with open(os.path.join(d, f), "rb") as fh:
                out[f] = hashlib.sha256(fh.read()).hexdigest()
        return out

    def test_key_and_methods(self):
        self.assertEqual(self.post(rpc("ping"), key="galat").status_code, 404)
        self.s.MCP_KEY = ""
        try:
            self.assertEqual(self.post(rpc("ping")).status_code, 404)      # key set nahi to pata band
        finally:
            self.s.MCP_KEY = KEY
        self.assertEqual(self.c.get(f"/mcp/{KEY}").status_code, 405)
        self.assertEqual(self.post(rpc("ping")).get_json()["result"], {})
        r = self.post(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        self.assertEqual((r.status_code, r.data), (202, b""))

    def test_all_tools_read_only(self):
        tools = self.post(rpc("tools/list")).get_json()["result"]["tools"]
        self.assertEqual({t["name"] for t in tools}, {"sehat", "aakhri_result", "aaj_ki_list", "paper_khata", "monitor",
                                                     "ds_rule_008", "ank_009", "active_patterns", "aaj_ki_tokri", "tulna", "jodi_khojo",
                                                     "naksha_aaj", "card_007", "din_ka_natija", "pocket_report", "error_jaanch", "guide"})
        before = self.snapshot()
        for t in tools:
            r = self.post(rpc("tools/call", {"name": t["name"], "arguments": {}}))
            self.assertEqual(r.status_code, 200, t["name"])
            res = r.get_json()["result"]
            self.assertFalse(res["isError"], (t["name"], res["content"][0]["text"][:300]))
            body = json.loads(res["content"][0]["text"])              # poora JSON aaya (kata nahi)
            self.assertIn("KALPNIK PUZZLE", body["dhyan"], t["name"])   # har jawab par kagaz wali mohar
        self.assertEqual(self.snapshot(), before)                      # kisi tool ne koi file nahi badli

    def test_tool_args(self):
        out = self.post(rpc("tools/call", {"name": "aakhri_result", "arguments": {"din": 3}})).get_json()["result"]
        res = json.loads(out["content"][0]["text"])
        self.assertEqual(len(res["results"]), 3)
        self.assertEqual(set(res["results"][0]), {"date", "FD", "GB", "GL", "DS"})
        out = self.post(rpc("tools/call", {"name": "aaj_ki_list", "arguments": {"known": "12,47"}})).get_json()["result"]
        self.assertEqual(json.loads(out["content"][0]["text"])["known"], [12, 47])
        out = self.post(rpc("tools/call", {"name": "aaj_ki_list", "arguments": {"known": "1,2,3,4"}})).get_json()["result"]
        self.assertTrue(out["isError"])
        out = self.post(rpc("tools/call", {"name": "aakhri_result", "arguments": {"din": 500}})).get_json()["result"]
        self.assertTrue(out["isError"])

    def call(self, name, args=None):
        res = self.post(rpc("tools/call", {"name": name, "arguments": args or {}})).get_json()["result"]
        return res["isError"], res["content"][0]["text"]

    def test_new_tools_answers(self):
        err, t = self.call("tulna", {"pehli": "top30", "doosri": "dost"})
        self.assertFalse(err, t)
        j = json.loads(t)
        a, b = j["pehli"]["ginti"], j["doosri"]["ginti"]
        self.assertEqual(j["dono_me"]["ginti"] + len(j["sirf_pehli_me"]), a)
        self.assertEqual(j["dono_me"]["ginti"] + len(j["sirf_doosri_me"]), b)
        n = json.loads(self.call("naksha_aaj")[1])
        self.assertEqual(n["kul_alag_jodi"], len(n["jodi"]))
        self.assertTrue(set(n["30_jodi_me_bhi"]) <= set(n["jodi"]))
        k = json.loads(self.call("jodi_khojo", {"jodi": int(n["jodi"][0])})[1])
        self.assertTrue(k["naksha_aaj"])
        last = json.loads(self.call("aakhri_result", {"din": 1})[1])["results"][0]
        d = json.loads(self.call("din_ka_natija", {"tarikh": last["date"]})[1])
        self.assertEqual({g: int(v) for g, v in d["result"].items()}, {g: last[g] for g in ("FD", "GB", "GL", "DS")})   # chaaron, app jaise naam
        self.assertNotIn('"FB"', self.call("naksha_aaj")[1])
        self.assertIn("007", self.call("guide", {"vishay": "007"})[1])
        self.assertTrue(self.call("guide", {"vishay": "../../etc"})[0])
        self.assertTrue(self.call("tulna", {"pehli": "galat"})[0])
        self.assertTrue(self.call("jodi_khojo", {"jodi": 100})[0])

    def test_old_routes_same(self):
        h = self.c.get("/api/health")
        self.assertEqual(h.status_code, 200)
        self.assertIn("last_date", h.get_json())
        t = self.c.get("/api/today?known=12,47").get_json()
        self.assertEqual(t["known"], [12, 47])
        self.assertEqual(self.c.get("/api/today?known=1,2,3,4").status_code, 400)


if __name__ == "__main__":
    unittest.main()
