# File Name: main.py
import os, urllib.parse, datetime, json, re
from collections import Counter

import step1_tokari, step2_evergreen, step3_universal, step4_magic
import step5_dayfix, step6_murda, step7_haruf, step8_baki, step9_monthtrend

RECORD_FILE     = "lifetime_record.txt"
PENDING_FILE    = "pending_result.json"
PRED_HIST_FILE  = "prediction_history.json"

# ══════════════════════════════════════════════
#  FILE HELPERS
# ══════════════════════════════════════════════

def load_history():
    history = {}
    if not os.path.exists(RECORD_FILE):
        return history
    with open(RECORD_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "|" in line and not line.startswith("#"):
                parts = line.split("|")
                date_part = parts[0].strip()
                vals = [int(x) for x in re.findall(r'\d+', parts[1])]
                vals = [100 if x == 0 else x for x in vals]
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

def fmt_num(n):
    return "100" if n == 100 else f"{n:02d}"

def append_to_record(date_str, fd, gb, gl, ds):
    history = load_history()
    if date_str in history:
        print(f"\n[!] {date_str} ka record PEHLE SE HAI. Option 3 se update karein.")
        return False
    line = f"{date_str} | {fmt_num(fd)} {fmt_num(gb)} {fmt_num(gl)} {fmt_num(ds)}\n"
    with open(RECORD_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(f"\n[✓] Record save ho gaya => {line.strip()}")
    # Auto check prediction
    check_prediction_result(date_str, [fd, gb, gl, ds])
    return True

def update_record_line(date_str, fd, gb, gl, ds):
    if not os.path.exists(RECORD_FILE):
        return False
    lines = open(RECORD_FILE, "r", encoding="utf-8").readlines()
    new_line = f"{date_str} | {fmt_num(fd)} {fmt_num(gb)} {fmt_num(gl)} {fmt_num(ds)}\n"
    found = False
    for i, l in enumerate(lines):
        if l.startswith(date_str):
            lines[i] = new_line
            found = True
            break
    if found:
        with open(RECORD_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"\n[✓] Record update ho gaya => {new_line.strip()}")
        check_prediction_result(date_str, [fd, gb, gl, ds])
    return found

# ══════════════════════════════════════════════
#  PASS / FAIL TRACKER
# ══════════════════════════════════════════════

def save_prediction_entry(game_date, result_used, L1, L2, L3):
    ph = load_pred_hist()
    ph[game_date] = {
        "game_date":    game_date,
        "result_used":  result_used,
        "L1": L1, "L2": L2, "L3": L3,
        "actual_result": None,
        "status": "PENDING"
    }
    save_pred_hist(ph)
    print(f"\n[✓] Prediction {game_date} ke liye history mein save ho gayi.")

def check_prediction_result(date_str, actual_vals):
    ph = load_pred_hist()
    if date_str not in ph:
        return
    entry   = ph[date_str]
    actual_set = set(str(v).zfill(2) if v != 100 else "00" for v in actual_vals)
    L1_set  = set(entry["L1"])
    L2_set  = set(entry["L2"])
    L3_set  = set(entry["L3"])

    if actual_set & L1_set:
        status = "PASS_L1"
        matched = actual_set & L1_set
    elif actual_set & L2_set:
        status = "PASS_L2"
        matched = actual_set & L2_set
    elif actual_set & L3_set:
        status = "PASS_L3"
        matched = actual_set & L3_set
    else:
        status  = "FAIL"
        matched = set()

    entry["actual_result"] = [fmt_num(v) for v in actual_vals]
    entry["status"]        = status
    entry["matched"]       = list(matched)
    ph[date_str]           = entry
    save_pred_hist(ph)

    print("\n" + "="*50)
    if status.startswith("PASS"):
        print(f"  *** RESULT: {status} *** Matched: {', '.join(matched)}")
    else:
        print(f"  *** RESULT: FAIL *** Koi bhi number match nahi hua.")
    print("="*50)

def show_pass_fail_stats():
    ph = load_pred_hist()
    if not ph:
        print("\n=> Abhi tak koi prediction save nahi hui. Pehle Prediction chalao.")
        return

    print("\n" + "="*60)
    print("         *** PASS / FAIL HISTORY ***")
    print("="*60)
    print(f"  {'Date':<12} {'Status':<12} {'Matched':<12} {'Actual Result'}")
    print("-"*60)

    total = pass_l1 = pass_l2 = pass_l3 = fail = pending = 0
    for date in sorted(ph.keys()):
        e = ph[date]
        status  = e.get("status", "PENDING")
        matched = ", ".join(e.get("matched", [])) or "--"
        actual  = " ".join(e.get("actual_result") or []) or "--"

        icon = {"PASS_L1":"✓L1","PASS_L2":"✓L2","PASS_L3":"✓L3","FAIL":"✗","PENDING":"??"}.get(status,"??")
        print(f"  {date:<12} {icon:<12} {matched:<12} {actual}")

        total += 1
        if status == "PASS_L1": pass_l1 += 1
        elif status == "PASS_L2": pass_l2 += 1
        elif status == "PASS_L3": pass_l3 += 1
        elif status == "FAIL": fail += 1
        else: pending += 1

    passed = pass_l1 + pass_l2 + pass_l3
    print("="*60)
    print(f"  TOTAL: {total}  |  PASS: {passed} (L1:{pass_l1} L2:{pass_l2} L3:{pass_l3})  |  FAIL: {fail}  |  PENDING: {pending}")
    if total - pending > 0:
        pct = round(passed / (total - pending) * 100, 1)
        print(f"  SUCCESS RATE: {pct}%")
    print("="*60)

# ══════════════════════════════════════════════
#  PREDICTION ENGINE
# ══════════════════════════════════════════════

def get_palat(jodi):
    if jodi == 100: return 100
    val = int(f"{jodi:02d}"[::-1])
    return 100 if val == 0 else val

def run_prediction():
    print("\n" + "="*50)
    print("      *** SAHIL BHAI ENGINE 1 (CUSTOM) ***")
    print("="*50)

    pending = load_pending()
    latest_4_results = None
    used_date = None

    if pending:
        complete = {d: v for d, v in pending.items() if None not in v}
        if complete:
            print("\n[!] Ye dates ke POORE results pending hain (use kar sakte hain):")
            for d, v in complete.items():
                print(f"    {d} => FD:{v[0]} GB:{v[1]} GL:{v[2]} DS:{v[3]}")
            use_p = input("\n=> Inhe use karein? (H/N): ").strip().upper()
            if use_p == 'H':
                d = sorted(complete.keys())[0]
                used_date = d
                latest_4_results = [100 if x == 0 else x for x in complete[d]]
                print(f"=> {d} ka result use kar raha hoon.")

    if latest_4_results is None:
        user_input = input("\n=> Kal ka FD GB GL DS dalein (jaise: 34 23 12 45): ").strip().split()
        latest_4_results = []
        for x in user_input:
            try:
                n = int(x); latest_4_results.append(100 if n == 0 else n)
            except: pass
        if len(latest_4_results) < 4:
            print("=> Galti: Poore 4 number chahiye!"); return

    # Tokari
    raw_list = []
    for r in latest_4_results:
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
            combined_counts[f"{dj}/{dp}" if palat != jodi else dj] = total_cnt

    print("\n" + "="*50)
    print("   *** TOKARI COUNT SUMMARY ***")
    print("="*50)
    for jodi_str, cnt in sorted(combined_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"-> {jodi_str} [{cnt} baar]")
    print("="*50)
    input("=> Milan kar lein. ENTER dabayein...")

    print("\n[2] Evergreen (+7)    [3] Universal (+10)")
    print("[4] Magic (+15)       [5] Day Fix (+5)")
    print("[6] Murda (+10)       [7] Haruf (+5)")
    print("[8] Baki (+3)         [9] Month Trend (+3)\n")
    user_choice = input("=> Formula number dalein (jaise: 2 5 6): ").strip().split()

    history       = load_history()
    today_date    = datetime.date.today()
    today_weekday = today_date.weekday()
    dates_list    = sorted(history.keys())
    past_murda    = []
    if len(dates_list) >= 3:
        for d in dates_list[-3:]: past_murda.extend(history[d])
    current_ym         = today_date.strftime("%Y-%m")
    current_month_nums = list(set([x for d, v in history.items() if d.startswith(current_ym) for x in v]))
    magic_list  = [12, 23, 84, 96]
    top_harufs  = ['3', '0']

    basket = step1_tokari.create_basket(latest_4_results)
    final_scores = {}
    for jodi, base_point in basket.items():
        tp = base_point
        if '2' in user_choice: pts, _ = step2_evergreen.check_evergreen(jodi); tp += pts
        if '3' in user_choice: pts, _ = step3_universal.check_universal(jodi, today_date); tp += pts
        if '4' in user_choice: pts, _ = step4_magic.check_magic(jodi); tp += pts
        if '5' in user_choice: pts, _ = step5_dayfix.check_dayfix(jodi, today_weekday); tp += pts
        if '6' in user_choice: pts, _ = step6_murda.check_murda(jodi, past_murda); tp += pts
        if '7' in user_choice: pts, _ = step7_haruf.check_haruf(jodi, today_date, 'Y', top_harufs); tp += pts
        if '8' in user_choice: pts, _ = step8_baki.check_baki(jodi, past_murda, magic_list); tp += pts
        if '9' in user_choice: pts, _ = step9_monthtrend.check_monthtrend(jodi, current_month_nums); tp += pts
        final_scores[jodi] = tp

    final_list = [j for j, _ in sorted(final_scores.items(), key=lambda x: x[1], reverse=True)][:30]
    L1 = [fmt_num(j) for j in final_list[:4]]
    L2 = [fmt_num(j) for j in final_list[4:14]]
    L3 = [fmt_num(j) for j in final_list[14:30]]

    print("\n" + "="*50)
    print("      *** Parcha Generation ***")
    print("="*50)
    amt_L1 = int(input("=> L1 (Super VIP) amount: "))
    amt_L2 = int(input("=> L2 (Main 10)   amount: "))
    amt_L3 = int(input("=> L3 (Support 16) amount: "))

    parcha_lines = ["           *** FINAL GAME KA PARCHA ***"]
    def print_section(title, num_list, cost):
        if not num_list: return 0
        count = len(num_list); subtotal = count * cost
        l1 = f"=> {title} ({cost} Into): {', '.join(num_list)}"
        l2 = f"   * [{count} jodi x {cost} = Rs {subtotal}]"
        print(l1); print(l2); print("-"*50)
        parcha_lines.extend([l1, l2]); return subtotal

    print("\n" + "="*50)
    total_inv = 0
    total_inv += print_section("L1 (Super VIP)",  L1, amt_L1)
    total_inv += print_section("L2 (Main 10)",    L2, amt_L2)
    total_inv += print_section("L3 (Support 16)", L3, amt_L3)
    inv_line = f"=> Total Investment: Rs {total_inv}"
    print(inv_line); parcha_lines.append(inv_line); print("="*50)

    wa_text = "*** SAHIL BHAI PARCHA ***\n\n" + "\n".join(parcha_lines)
    print("\n" + "="*60)
    print("   *** AAPKA PARCHA (Copy karein) ***")
    print("="*60)
    print(wa_text)
    print("="*60)

    # Prediction history mein save karo
    game_date_str = today_date.strftime("%Y-%m-%d")
    game_date_inp = input(f"\n=> Aaj ki game ki date? (ENTER = {game_date_str}): ").strip()
    game_date_str = game_date_inp if game_date_inp else game_date_str
    save_prediction_entry(game_date_str, [fmt_num(x) for x in latest_4_results], L1, L2, L3)

    w = input("\n=> WhatsApp link? (1: Mera no. / 2: Doosra no. / 3: Skip): ").strip()
    if w in ['1', '2']:
        phone = "918562891905" if w == '1' else re.sub(r'\D', '', input("=> Number (91XXXXXXXXXX): ").strip())
        url   = f"https://api.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(wa_text)}"
        print("\n=> WHATSAPP LINK:")
        print(url)

# ══════════════════════════════════════════════
#  OPTION 2 – RESULT SAVE (EK EK KARKE)
# ══════════════════════════════════════════════

def save_individual_result():
    print("\n" + "="*50)
    print("   *** RESULT SAVE KARO (FD / GB / GL / DS) ***")
    print("="*50)

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    date_inp  = input(f"=> Date (ENTER = {today_str}): ").strip()
    date_str  = date_inp if date_inp else today_str

    pending = load_pending()
    if date_str not in pending:
        pending[date_str] = [None, None, None, None]

    names = ["FD", "GB", "GL", "DS"]
    print(f"\n=> {date_str} ka abhi tak ka data:")
    for i, name in enumerate(names):
        v = pending[date_str][i]
        print(f"   [{i+1}] {name}: {v if v is not None else '--  (nahi aaya)'}")

    print("\n=> Kaunsa result save karein?")
    print("   [1] FD   [2] GB   [3] GL   [4] DS   [5] Wapas")
    choice = input("=> Choose: ").strip()

    if choice in ['1', '2', '3', '4']:
        idx  = int(choice) - 1
        name = names[idx]
        try:
            val = int(input(f"=> {name} ka result: ").strip())
            if val == 0: val = 100
            pending[date_str][idx] = val
            save_pending(pending)
            print(f"\n[✓] {name} = {val} save ho gaya!")
        except:
            print("=> Galti: Sirf number dalein!"); return

        if None not in pending[date_str]:
            fd, gb, gl, ds = pending[date_str]
            print(f"\n[✓] {date_str} ke SAARE 4 results aa gaye!")
            print(f"    FD:{fd}  GB:{gb}  GL:{gl}  DS:{ds}")
            confirm = input("\n=> lifetime_record.txt mein save karein? (H/N): ").strip().upper()
            if confirm == 'H':
                ok = append_to_record(date_str, fd, gb, gl, ds)
                if ok:
                    del pending[date_str]
                    save_pending(pending)
                    print("[✓] Pending se hata diya!")
    elif choice != '5':
        print("=> Galat choice!")

# ══════════════════════════════════════════════
#  OPTION 3 – RECORD DEKHEIN / UPDATE KAREIN
# ══════════════════════════════════════════════

def manage_records():
    while True:
        print("\n" + "="*50)
        print("   *** RECORD DEKHEIN / UPDATE KAREIN ***")
        print("="*50)
        print("  [1] Kisi date ka record dekhein")
        print("  [2] Kisi date ka record update karein")
        print("  [3] Aakhri 10 records dekhein")
        print("  [4] Wapas")
        choice = input("=> Choose: ").strip()
        history = load_history()

        if choice == '1':
            d = input("=> Date (jaise 2026-06-22): ").strip()
            if d in history:
                v = history[d]
                print(f"\n  {d} => FD:{v[0]}  GB:{v[1]}  GL:{v[2]}  DS:{v[3]}")
            else:
                print(f"=> {d} ka record nahi mila.")

        elif choice == '2':
            d = input("=> Kaun si date update karein: ").strip()
            if d not in history:
                print(f"=> {d} ka record nahi mila."); continue
            old = history[d]
            print(f"\n=> Purana: FD:{old[0]}  GB:{old[1]}  GL:{old[2]}  DS:{old[3]}")
            try:
                vals = list(map(int, input("=> Naya FD GB GL DS dalein: ").strip().split()))
                if len(vals) != 4: print("=> 4 number chahiye!"); continue
                vals = [100 if v == 0 else v for v in vals]
                update_record_line(d, *vals)
            except:
                print("=> Galat input!")

        elif choice == '3':
            dates = sorted(history.keys())[-10:]
            print("\n=> Aakhri 10 records:")
            print("-"*42)
            for d in dates:
                v = history[d]
                print(f"  {d}  |  FD:{v[0]:>3}  GB:{v[1]:>3}  GL:{v[2]:>3}  DS:{v[3]:>3}")
            print("-"*42)

        elif choice == '4':
            break
        else:
            print("=> 1 se 4 mein se choose karein.")

# ══════════════════════════════════════════════
#  OPTION 4 – PASS / FAIL STATS
# ══════════════════════════════════════════════

def pass_fail_menu():
    while True:
        print("\n" + "="*50)
        print("       *** PASS / FAIL TRACKER ***")
        print("="*50)
        print("  [1] Poori history dekhein + stats")
        print("  [2] Kisi date ka result manually check karein")
        print("  [3] Wapas")
        choice = input("=> Choose: ").strip()

        if choice == '1':
            show_pass_fail_stats()

        elif choice == '2':
            ph = load_pred_hist()
            if not ph:
                print("=> Koi prediction saved nahi hai."); continue
            d = input("=> Kaun si date check karein: ").strip()
            if d not in ph:
                print(f"=> {d} ki prediction nahi mili."); continue
            e = ph[d]
            print(f"\n  L1: {', '.join(e['L1'])}")
            print(f"  L2: {', '.join(e['L2'])}")
            print(f"  L3: {', '.join(e['L3'])}")
            try:
                vals = list(map(int, input("=> Actual result dalein (FD GB GL DS): ").strip().split()))
                if len(vals) != 4: print("=> 4 number chahiye!"); continue
                vals = [100 if v == 0 else v for v in vals]
                check_prediction_result(d, vals)
                # Also save to record if not already there
                history = load_history()
                if d not in history:
                    save_q = input("=> Ise lifetime record mein bhi save karein? (H/N): ").strip().upper()
                    if save_q == 'H':
                        append_to_record(d, *vals)
            except:
                print("=> Galat input!")

        elif choice == '3':
            break
        else:
            print("=> 1 se 3 mein se choose karein.")

# ══════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════

def main():
    while True:
        pending      = load_pending()
        pred_hist    = load_pred_hist()
        pending_c    = len(pending)
        pend_pred_c  = sum(1 for e in pred_hist.values() if e.get("status") == "PENDING")

        print("\n" + "="*52)
        print("      *** SAHIL BHAI MASTER SYSTEM ***")
        print("="*52)
        if pending_c:
            print(f"  [!] {pending_c} date ke aadhe results pending hain")
        if pend_pred_c:
            print(f"  [!] {pend_pred_c} prediction(s) ka result abhi check nahi hua")
        print()
        print("  [1]  Prediction chalao")
        print("  [2]  Result save karo  (FD / GB / GL / DS alag alag)")
        print("  [3]  Record dekhein / update karein")
        print("  [4]  Pass / Fail tracker")
        print("  [5]  Bahar jaao")
        print()
        choice = input("=> Kya karna hai: ").strip()

        if   choice == '1': run_prediction()
        elif choice == '2': save_individual_result()
        elif choice == '3': manage_records()
        elif choice == '4': pass_fail_menu()
        elif choice == '5':
            print("\n=> Alvida! Kal phir milenge.\n"); break
        else:
            print("=> 1 se 5 mein se choose karein.")

if __name__ == "__main__":
    main()
