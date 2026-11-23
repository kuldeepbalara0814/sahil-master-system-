"""Ek hi process: light patterns (copy/family/dana/tokri) shuffled data par, seeds 11..(10+N). Cache: ../cache/shufL_<m><i>_light.csv.gz
Usage: python run_light_shuffles.py [N=12]   (resume: bani hui file chhod deta hai)"""
import os, sys, time
import harness as h
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
for i in range(11, 11 + N):
    m = "row" if i % 2 else "col"
    tag = f"shufL_{m}{i}"
    f = os.path.join(h.CACHE, f"{tag}_light.csv.gz")
    if os.path.exists(f):
        continue
    t0 = time.time()
    h.init(m, i)
    ts = h.valid_ts(h.G["full"])
    rows = []
    for t in ts:
        rows += h.light_day(t)
    h.write(f, h.COLS, rows)
    open(os.path.join(h.OUT, "progress_shuffles.txt"), "a").write(f"{tag} done {time.time()-t0:.0f}s\n")
