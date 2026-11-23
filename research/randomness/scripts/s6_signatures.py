"""6) Non-random generator signatures: no-replacement/deck, digit independence, mod structure, spectral, birthday-spacing, compression, LCG/LFG."""
import numpy as np, common as c, zlib, bz2, lzma, sys
S = c.load_all(); NS = 200
res = {}; rows = []

def add(g, hyp, test, stat, p, verdict=""):
    rows.append([g, hyp, test, stat, p, verdict])

for g, (D, x) in S.items():
    n = len(x); rg = c.rng(71 + n); cnt = np.bincount(x, minlength=100); pm = cnt / n
    # (a) no-replacement within window W
    def dup(v, W):
        return sum(int((v[:-k] == v[k:]).sum()) for k in range(1, W + 1))
    for W in (2, 5, 10, 20, 50, 100):
        o = dup(x, W); sims = np.array([dup(rg.permutation(x), W) for _ in range(60 if W >= 50 else NS)])
        z = (o - sims.mean()) / sims.std(); add(g, "sampling without replacement (window W=%d)" % W, "repeats within W vs shuffle (ratio obs/null %.3f)" % (o / sims.mean()), z, c.mc_p(o, sims, "two"))
    for B in (10, 20, 50, 100):
        fr = []
        for off in range(B):
            v = x[off:]; k = len(v) // B; blk = v[:k * B].reshape(k, B)
            fr.append(np.mean([len(set(r)) == B for r in blk]))
        add(g, "fresh shuffled deck of %d (all distinct in aligned block)" % B, "max over offsets of share of blocks with no repeat (iid expects %.4f)" % np.prod(1 - np.arange(B) / 100.0), float(max(fr)), 0.0, "REJECT" if max(fr) < 0.5 else "")
    # (b) digit independence / transitions
    t, u = x // 10, x % 10
    for nm, a_, b_ in (("tens(t) vs unit(t)", t, u), ("tens(t) vs tens(t+1)", t[:-1], t[1:]), ("unit(t) vs unit(t+1)", u[:-1], u[1:]), ("tens(t) vs unit(t+1)", t[:-1], u[1:]), ("unit(t) vs tens(t+1)", u[:-1], t[1:])):
        tab = np.zeros((10, 10)); np.add.at(tab, (a_, b_), 1); st, df, p = c.chi2_indep(tab); add(g, "digit-wise generator", "chi2 independence " + nm + " df=%d" % df, st, p)
    # (c) mod structure
    for m in range(2, 14):
        pe = np.bincount(np.arange(100) % m, minlength=m) / 100; st, df, p = c.chi2_gof(np.bincount(x % m, minlength=m), pe); add(g, "mod structure", "number mod %d" % m, st, p)
    for m in (2, 3, 5, 7, 9, 10, 11):
        pe = np.zeros(m); [pe.__setitem__((a_ // 10 + a_ % 10) % m, pe[(a_ // 10 + a_ % 10) % m] + .01) for a_ in range(100)]
        st, df, p = c.chi2_gof(np.bincount((t + u) % m, minlength=m), pe); add(g, "mod structure", "digit-sum mod %d" % m, st, p)
    # (d) spectral
    def pgram(v):
        v = v - v.mean(); F = np.abs(np.fft.rfft(v)) ** 2; F = F[1:-1]; return F / F.sum()
    for nm, v in (("number", x.astype(float)), ("tens", t.astype(float)), ("unit", u.astype(float)), ("double", c.DOUBLE[x].astype(float)), ("class", c.CLS[x].astype(float))):
        P = pgram(v); k = int(P.argmax()); per = n / (k + 1); mx = P.max() * len(P)
        sims = np.array([pgram(rg.permutation(v)).max() * len(P) for _ in range(NS)])
        add(g, "periodicity (FFT)", "%s: max peak/mean=%.2f at period %.1f rows" % (nm, mx, per), mx, c.mc_p(mx, sims))
    X = np.zeros((100, n)); X[x, np.arange(n)] = 1; X -= X.mean(1, keepdims=True)
    def pg2(M): F = np.abs(np.fft.rfft(M, axis=1)) ** 2; F = F[:, 1:-1]; return F / np.where(F.sum(1, keepdims=True) > 0, F.sum(1, keepdims=True), 1)
    P2 = pg2(X); mx = P2.max() * P2.shape[1]; i, k = np.unravel_index(P2.argmax(), P2.shape)
    sims = []
    for _ in range(40):
        xs = rg.permutation(x); Z = np.zeros((100, n)); Z[xs, np.arange(n)] = 1; Z -= Z.mean(1, keepdims=True); sims.append(pg2(Z).max() * P2.shape[1])
    add(g, "periodicity (FFT)", "100 per-number indicators: max peak at number %d, period %.1f rows" % (i, n / (k + 1)), mx, c.mc_p(mx, sims))
    # (e) birthday spacing
    m_ = 16; k = n // m_; blk = np.sort(x[:k * m_].reshape(k, m_), axis=1); sp = np.diff(blk, axis=1)
    def dupsp(sp_):
        s = np.sort(sp_, axis=1); return (s[:, 1:] == s[:, :-1]).sum(1).mean()
    ob = dupsp(sp); sims = []
    for _ in range(100):
        v = rg.permutation(x)[:k * m_].reshape(k, m_); sims.append(dupsp(np.diff(np.sort(v, axis=1), axis=1)))
    add(g, "birthday-spacing / near-duplicate", "mean duplicate spacings per block of 16 (shuffle mean %.3f)" % np.mean(sims), ob, c.mc_p(ob, sims, "two"))
    dd = np.abs(np.diff(x)); exp_d = np.zeros(100)
    for a_ in range(100):
        for b_ in range(100): exp_d[abs(a_ - b_)] += pm[a_] * pm[b_]
    st, df, p = c.chi2_gof(np.bincount(dd, minlength=100)[:50].tolist() + [np.bincount(dd, minlength=100)[50:].sum()], exp_d[:50].tolist() + [exp_d[50:].sum()]); add(g, "near-duplicate", "|x(t+1)-x(t)| distribution vs product-of-marginals chi2 df=%d" % df, st, p)
    # (f) compression
    def sizes(v):
        b = bytes(v.astype(np.uint8)); return np.array([len(zlib.compress(b, 9)), len(bz2.compress(b, 9)), len(lzma.compress(b))], float)
    o = sizes(x); sm = np.array([sizes(rg.permutation(x)) for _ in range(40)])
    for j, nm in enumerate(["zlib", "bz2", "lzma"]):
        z = (o[j] - sm[:, j].mean()) / sm[:, j].std(); add(g, "low-entropy / structure (compression)", "%s size %d vs shuffle mean %.0f (ratio %.4f)" % (nm, o[j], sm[:, j].mean(), o[j] / sm[:, j].mean()), z, c.mc_p(o[j], sm[:, j], "lower"))
    # (g) LCG: x[t+1] = a x[t] + b mod 100
    def lcg_max(v):
        best = 0
        for a_ in range(100):
            r = (v[1:] - a_ * v[:-1]) % 100; best = max(best, int(np.bincount(r, minlength=100).max()))
        return best
    ob = lcg_max(x); sims = [lcg_max(rg.permutation(x)) for _ in range(60)]
    add(g, "seeded PRNG (LCG mod 100)", "best (a,b) fits %d of %d transitions (shuffle mean %.1f; a pure LCG would fit all)" % (ob, n - 1, np.mean(sims)), (ob - np.mean(sims)) / np.std(sims), c.mc_p(ob, sims))
    # LFG sum/diff mod 100 uniformity at lags 1..60
    ps = []
    conv_s = np.zeros(100); conv_d = np.zeros(100)
    for a_ in range(100):
        for b_ in range(100): conv_s[(a_ + b_) % 100] += pm[a_] * pm[b_]; conv_d[(a_ - b_) % 100] += pm[a_] * pm[b_]
    for k_ in range(1, 61):
        for nm, v, pe in (("sum", (x[k_:] + x[:-k_]) % 100, conv_s), ("diff", (x[k_:] - x[:-k_]) % 100, conv_d)):
            st, df, p = c.chi2_gof(np.bincount(v, minlength=100), pe); ps.append(p)
    ks, _ = c.ks_uniform_p(ps)
    add(g, "lagged-Fibonacci (x(t) +/- x(t-k) mod 100, k=1..60, 120 tests)", "n p<.05 = %d (expect 6), min p %.4f, BH rejects %d" % (sum(p < .05 for p in ps), min(ps), c.bh(ps)), float(min(ps)), ks, "KS-uniformity p in last col")
c.save_csv("s6_signatures.csv", ["game", "hypothesis", "test", "stat_or_z", "p", "note"], rows)
for r in rows: print(r)
