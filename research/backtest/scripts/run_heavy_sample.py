"""Chhota heavy walk-forward sample: 60 block x 4 din (naksha 002/002b, steps 007, ens). real + shuffle control.
Usage: python run_heavy_sample.py <tag> [row|col] [seed]    # cache: <tag>_h60_{heavy,ens}.csv.gz. Resume: bani file chhod deta hai. 2 workers."""
import os, sys, time, random
from multiprocessing import Pool
import harness as h


def main():
    tag = sys.argv[1]; shuf = sys.argv[2] if len(sys.argv) > 2 else None; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    name = f"{tag}_h60"
    if os.path.exists(os.path.join(h.CACHE, f"{name}_heavy.csv.gz")):
        return
    h.init(shuf, seed); ts = h.valid_ts(h.G["full"])
    rng = random.Random(1234); starts = sorted(rng.sample(range(len(ts) - 4), 60))
    hts = sorted({ts[s + j] for s in starts for j in range(4) if ts[s + j] - ts[s] == j})
    prog = os.path.join(h.OUT, "progress_heavy60.txt"); t0 = time.time(); R, E = [], []
    with Pool(2, initializer=h.init, initargs=(shuf, seed)) as p:
        for k, (r, e) in enumerate(p.imap(h.heavy_day, hts, chunksize=2), 1):
            R += r; E += e
            if k % 20 == 0: open(prog, "a").write(f"{name} {k}/{len(hts)} {time.time()-t0:.0f}s\n")
    h.write(os.path.join(h.CACHE, f"{name}_heavy.csv.gz"), h.COLS, R)
    h.write(os.path.join(h.CACHE, f"{name}_ens.csv.gz"), ["t","date","n","v_nak","v_nak2","v_fam","v_copy","v_dana","v_steps","tok","hit","cnt"], E)
    open(prog, "a").write(f"{name} DONE {time.time()-t0:.0f}s ({len(hts)} din)\n")


if __name__ == "__main__":
    main()
