"""
sahil_system/api.py
JSON CLI API - Express server calls this with: python3 api.py <command> '<json_args>'
Outputs JSON to stdout.
"""
import sys, os, json, datetime, re
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
import step1_tokari, step2_evergreen, step3_universal, step4_magic
import step5_dayfix, step6_murda, step7_haruf, step8_baki, step9_monthtrend

RECORD_FILE   = os.path.join(os.path.dirname(__file__), "lifetime_record.txt")
PENDING_FILE  = os.path.join(os.path.dirname(__file__), "pending_result.json")
PRED_HIST_FILE = os.path.join(os.path.dirname(__file__), "prediction_history.json")

# ──────────────────────────────────────────────
#  FILE HELPERS
# ──────────────────────────────────────────────

def fmt_num(n):
    return "00" if n == 100 else f"{n:02d}"

def load_history():
    history = {}
    if not os.path.exists(RECORD_FILE):
        return history
    with open(RECORD_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "|" in line and not line.startswith("#"):
                parts = line.split("|")
                date_part = parts[0].strip()
                vals = [int(x) for x in re.findall(r'\d+', parts[1])]
                vals = [100 if x == 0 else x for x in vals]
                if len(vals) == 4:
                    history[date_part] = vals
    return history

def load_pending():
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_pending(data):
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_pred_hist():
    if os.path.exists(PRED_HIST_FILE):
        with open(PRED_HIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_pred_hist(data):
    with open(PRED_HIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_palat(jodi):
    if jodi == 100: return 100
    val = int(f"{jodi:02d}"[::-1])
    return 100 if val == 0 else val

# ──────────────────────────────────────────────
#  COMMANDS
# ──────────────────────────────────────────────

def cmd_records_list(args):
    history = load_history()
    result = []
    for date_str, vals in sorted(history.items()):
        result.append({
            "date": date_str,
            "fd":   0 if vals[0] == 100 else vals[0],
            "gb":   0 if vals[1] == 100 else vals[1],
            "gl":   0 if vals[2] == 100 else vals[2],
            "ds":   0 if vals[3] == 100 else vals[3],
        })
    return result

def cmd_records_add(args):
    date_str = args["date"]
    fd = 100 if args["fd"] == 0 else args["fd"]
    gb = 100 if args["gb"] == 0 else args["gb"]
    gl = 100 if args["gl"] == 0 else args["gl"]
    ds = 100 if args["ds"] == 0 else args["ds"]

    history = load_history()
    if date_str in history:
        return {"success": False, "message": f"{date_str} ka record pehle se hai.", "conflict": True}

    line = f"{date_str} | {fmt_num(fd)} {fmt_num(gb)} {fmt_num(gl)} {fmt_num(ds)}\n"
    with open(RECORD_FILE, "a", encoding="utf-8") as f:
        f.write(line)

    check_and_update_prediction(date_str, [fd, gb, gl, ds])
    return {"success": True, "message": f"Record save ho gaya: {line.strip()}"}

def cmd_records_update(args):
    date_str = args["date"]
    fd = 100 if args["fd"] == 0 else args["fd"]
    gb = 100 if args["gb"] == 0 else args["gb"]
    gl = 100 if args["gl"] == 0 else args["gl"]
    ds = 100 if args["ds"] == 0 else args["ds"]

    if not os.path.exists(RECORD_FILE):
        return {"success": False, "message": "Record file nahi mili.", "notFound": True}

    lines = open(RECORD_FILE, "r", encoding="utf-8").readlines()
    new_line = f"{date_str} | {fmt_num(fd)} {fmt_num(gb)} {fmt_num(gl)} {fmt_num(ds)}\n"
    found = False
    for i, l in enumerate(lines):
        if l.startswith(date_str):
            lines[i] = new_line
            found = True
            break

    if not found:
        return {"success": False, "message": f"{date_str} ka record nahi mila.", "notFound": True}

    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

    check_and_update_prediction(date_str, [fd, gb, gl, ds])
    return {"success": True, "message": f"Record update ho gaya: {new_line.strip()}"}

def cmd_pending_get(args):
    pending = load_pending()
    result = []
    for date_str, vals in sorted(pending.items()):
        result.append({
            "date": date_str,
            "fd":   vals[0],
            "gb":   vals[1],
            "gl":   vals[2],
            "ds":   vals[3],
            "complete": None not in vals,
        })
    return result

def cmd_pending_save(args):
    date_str = args["date"]
    field    = args["field"]
    value    = args["value"]

    field_map = {"fd": 0, "gb": 1, "gl": 2, "ds": 3}
    idx = field_map.get(field)
    if idx is None:
        return {"saved": False, "complete": False, "entry": None}

    pending = load_pending()
    if date_str not in pending:
        pending[date_str] = [None, None, None, None]

    pending[date_str][idx] = value
    save_pending(pending)

    entry = pending[date_str]
    complete = None not in entry

    return {
        "saved": True,
        "complete": complete,
        "entry": {
            "date": date_str,
            "fd":   entry[0],
            "gb":   entry[1],
            "gl":   entry[2],
            "ds":   entry[3],
            "complete": complete,
        }
    }

def cmd_predict(args):
    fd = 100 if args["fd"] == 0 else args["fd"]
    gb = 100 if args["gb"] == 0 else args["gb"]
    gl = 100 if args["gl"] == 0 else args["gl"]
    ds = 100 if args["ds"] == 0 else args["ds"]
    formula      = args.get("formula", ["2","5","6"])
    game_date    = args.get("gameDate", str(datetime.date.today()))

    latest_4 = [fd, gb, gl, ds]

    # Tokari
    raw_list = []
    for r in latest_4:
        if r in step1_tokari.MASTER_SHEET:
            raw_list.extend(step1_tokari.MASTER_SHEET[r])
    counts = Counter(raw_list)
    combined_counts = {}
    seen_pairs = set()
    for jodi, cnt in counts.items():
        palat = get_palat(jodi)
        pair  = tuple(sorted([jodi, palat]))
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            total_cnt = cnt + (counts[palat] if palat != jodi and palat in counts else 0)
            dj = "00" if jodi == 100 else f"{jodi:02d}"
            dp = "00" if palat == 100 else f"{palat:02d}"
            key = f"{dj}/{dp}" if palat != jodi else dj
            combined_counts[key] = total_cnt

    tokari_sorted = [{"jodi": k, "count": v}
                     for k, v in sorted(combined_counts.items(), key=lambda x: x[1], reverse=True)]

    # Formula scoring
    history       = load_history()
    today_date    = datetime.date.fromisoformat(game_date) if game_date else datetime.date.today()
    today_weekday = today_date.weekday()
    dates_list    = sorted(history.keys())
    past_murda    = []
    if len(dates_list) >= 3:
        for d in dates_list[-3:]: past_murda.extend(history[d])
    current_ym         = today_date.strftime("%Y-%m")
    current_month_nums = list(set([x for d, v in history.items() if d.startswith(current_ym) for x in v]))
    magic_list  = [12, 23, 84, 96]
    top_harufs  = ['3', '0']

    basket = step1_tokari.create_basket(latest_4)
    final_scores = {}
    for jodi, base_point in basket.items():
        tp = base_point
        if '2' in formula: pts, _ = step2_evergreen.check_evergreen(jodi); tp += pts
        if '3' in formula: pts, _ = step3_universal.check_universal(jodi, today_date); tp += pts
        if '4' in formula: pts, _ = step4_magic.check_magic(jodi); tp += pts
        if '5' in formula: pts, _ = step5_dayfix.check_dayfix(jodi, today_weekday); tp += pts
        if '6' in formula: pts, _ = step6_murda.check_murda(jodi, past_murda); tp += pts
        if '7' in formula: pts, _ = step7_haruf.check_haruf(jodi, today_date, 'Y', top_harufs); tp += pts
        if '8' in formula: pts, _ = step8_baki.check_baki(jodi, past_murda, magic_list); tp += pts
        if '9' in formula: pts, _ = step9_monthtrend.check_monthtrend(jodi, current_month_nums); tp += pts
        final_scores[jodi] = tp

    final_list = [j for j, _ in sorted(final_scores.items(), key=lambda x: x[1], reverse=True)][:30]
    L1 = [fmt_num(j) for j in final_list[:4]]
    L2 = [fmt_num(j) for j in final_list[4:14]]
    L3 = [fmt_num(j) for j in final_list[14:30]]

    # Save to prediction history
    ph = load_pred_hist()
    ph[game_date] = {
        "game_date":   game_date,
        "result_used": [fmt_num(v) for v in latest_4],
        "L1": L1, "L2": L2, "L3": L3,
        "actual_result": None,
        "status": "PENDING"
    }
    save_pred_hist(ph)

    return {
        "tokari":   tokari_sorted,
        "L1":       L1,
        "L2":       L2,
        "L3":       L3,
        "gameDate": game_date,
    }

def check_and_update_prediction(date_str, actual_vals):
    ph = load_pred_hist()
    if date_str not in ph:
        return
    entry      = ph[date_str]
    actual_set = set(fmt_num(v) for v in actual_vals)
    L1_set     = set(entry["L1"])
    L2_set     = set(entry["L2"])
    L3_set     = set(entry["L3"])

    if actual_set & L1_set:
        status  = "PASS_L1"; matched = actual_set & L1_set
    elif actual_set & L2_set:
        status  = "PASS_L2"; matched = actual_set & L2_set
    elif actual_set & L3_set:
        status  = "PASS_L3"; matched = actual_set & L3_set
    else:
        status  = "FAIL";    matched = set()

    entry["actual_result"] = [fmt_num(v) for v in actual_vals]
    entry["status"]        = status
    entry["matched"]       = list(matched)
    ph[date_str]           = entry
    save_pred_hist(ph)

def cmd_predictions_list(args):
    ph = load_pred_hist()
    result = []
    for date_str in sorted(ph.keys(), reverse=True):
        e = ph[date_str]
        result.append({
            "gameDate":     e.get("game_date", date_str),
            "L1":           e.get("L1", []),
            "L2":           e.get("L2", []),
            "L3":           e.get("L3", []),
            "status":       e.get("status", "PENDING"),
            "matched":      e.get("matched", []),
            "actualResult": e.get("actual_result", []),
        })
    return result

def cmd_predictions_check(args):
    date_str = args["date"]
    fd = 100 if args["fd"] == 0 else args["fd"]
    gb = 100 if args["gb"] == 0 else args["gb"]
    gl = 100 if args["gl"] == 0 else args["gl"]
    ds = 100 if args["ds"] == 0 else args["ds"]
    check_and_update_prediction(date_str, [fd, gb, gl, ds])
    ph = load_pred_hist()
    if date_str in ph:
        e = ph[date_str]
        return {"status": e["status"], "matched": e.get("matched", [])}
    return {"status": "NOT_FOUND", "matched": []}

def cmd_stats(args):
    ph = load_pred_hist()
    total = pass_l1 = pass_l2 = pass_l3 = fail = pending = 0
    for e in ph.values():
        status = e.get("status", "PENDING")
        total += 1
        if status == "PASS_L1":  pass_l1 += 1
        elif status == "PASS_L2": pass_l2 += 1
        elif status == "PASS_L3": pass_l3 += 1
        elif status == "FAIL":    fail += 1
        else:                     pending += 1

    passed = pass_l1 + pass_l2 + pass_l3
    checked = total - pending
    success_rate = round(passed / checked * 100, 1) if checked > 0 else 0.0

    return {
        "total":       total,
        "passed":      passed,
        "failed":      fail,
        "pending":     pending,
        "passL1":      pass_l1,
        "passL2":      pass_l2,
        "passL3":      pass_l3,
        "successRate": success_rate,
    }

# ──────────────────────────────────────────────
#  ROUTER
# ──────────────────────────────────────────────

COMMANDS = {
    "records_list":       cmd_records_list,
    "records_add":        cmd_records_add,
    "records_update":     cmd_records_update,
    "pending_get":        cmd_pending_get,
    "pending_save":       cmd_pending_save,
    "predict":            cmd_predict,
    "predictions_list":   cmd_predictions_list,
    "predictions_check":  cmd_predictions_check,
    "stats":              cmd_stats,
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Command required"})); sys.exit(1)

    cmd  = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    if cmd not in COMMANDS:
        print(json.dumps({"error": f"Unknown command: {cmd}"})); sys.exit(1)

    try:
        result = COMMANDS[cmd](args)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)})); sys.exit(1)
