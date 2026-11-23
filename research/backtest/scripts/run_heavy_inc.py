"""Heavy walk-forward sample, 1 process, har din ke baad file me append (crash par bhi partial bacha rehta hai). run_heavy_sample.py jaisa hi sample (seed 1234, 60 block x 4 din).
Usage: python run_heavy_inc.py [tag=inc] [row|col] [seed]   -> ../cache/inc_h60_heavy.csv, inc_h60_ens.csv, inc_h60_done.txt (done t list). Resume: done t chhod deta hai."""
import os, sys, csv, time, random
import harness as h

def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "inc"; shuf = sys.argv[2] if len(sys.argv) > 2 else None; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    h.init(shuf, seed); ts = h.valid_ts(h.G["full"])
    rng = random.Random(1234); starts = sorted(rng.sample(range(len(ts) - 4), 60))
    hts = sorted({ts[s + j] for s in starts for j in range(4) if ts[s + j] - ts[s] == j})
    fd = os.path.join(h.CACHE, f"{tag}_h60_done.txt"); fh = os.path.join(h.CACHE, f"{tag}_h60_heavy.csv"); fe = os.path.join(h.CACHE, f"{tag}_h60_ens.csv")
    done = set(int(x) for x in open(fd).read().split()) if os.path.exists(fd) else set()
    new = not os.path.exists(fh)
    prog = os.path.join(h.OUT, f"progress_heavy_{tag}.txt"); t0 = time.time()
    with open(fh, "a", newline="") as a, open(fe, "a", newline="") as b:
        wa, wb = csv.writer(a), csv.writer(b)
        if new:
            wa.writerow(h.COLS); wb.writerow(["t","date","n","v_nak","v_nak2","v_fam","v_copy","v_dana","v_steps","tok","hit","cnt"])
        for k, t in enumerate(hts, 1):
            if t in done: continue
            r, e = h.heavy_day(t)
            for x in r: wa.writerow([x.get(c, "") for c in h.COLS] if isinstance(x, dict) else x)
            for x in e: wb.writerow(x)
            a.flush(); b.flush(); open(fd, "a").write(f"{t}\n")
            open(prog, "a").write(f"{k}/{len(hts)} t={t} {time.time()-t0:.0f}s\n")
main()
