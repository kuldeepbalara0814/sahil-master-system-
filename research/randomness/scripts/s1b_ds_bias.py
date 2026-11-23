"""1b) DS me jo sthayi (stable) frequency jhukav dikha: split-half + walk-forward (sirf pichla data dekh kar agla saal)."""
import numpy as np, common as c
R = c.rng(11)
D, x = c.load("DS"); Y = c.years(D); n = len(x)
res = {}
# (a) DS 2013+ alag
m = Y >= 2013; xx = x[m]
st, df, p = c.chi2_gof(np.bincount(xx, minlength=100), np.full(100, .01))
sims = R.multinomial(len(xx), np.full(100, .01), size=2000); s = ((sims - len(xx) / 100) ** 2 / (len(xx) / 100)).sum(1)
res["DS_2013plus_number_chi2"] = dict(n=int(len(xx)), stat=st, df=df, p_asym=p, p_mc=c.mc_p(st, s))
for nm, f in (("tens", lambda v: v // 10), ("unit", lambda v: v % 10)):
    cnt = np.bincount(f(xx), minlength=10); res["DS_2013plus_" + nm] = dict(zip(range(10), (cnt / len(xx)).round(4).tolist()), p=c.chi2_gof(cnt, np.full(10, .1))[2])
# (b) split half: pehla aadha vs doosra aadha
h = n // 2
a, b = np.bincount(x[:h], minlength=100) / h, np.bincount(x[h:], minlength=100) / (n - h)
r = float(np.corrcoef(a, b)[0, 1])
perm = np.array([np.corrcoef(a, R.permutation(b))[0, 1] for _ in range(5000)])
res["split_half_corr_of_number_freq"] = dict(r=r, p_perm=c.mc_p(r, perm), split_date=str(D[h]))
# (c) walk-forward: har saal ke pehle ke saare saal se top-10 / bottom-10 number; us saal par hit-rate
rows = []; hitsT = hitsB = tot = 0
for y in range(1990, 2027):
    tr = x[Y < y]; te = x[Y == y]
    cnt = np.bincount(tr, minlength=100); o = np.argsort(cnt)
    top, bot = o[-10:], o[:10]
    hT = int(np.isin(te, top).sum()); hB = int(np.isin(te, bot).sum())
    rows.append([y, len(te), hT, hB]); hitsT += hT; hitsB += hB; tot += len(te)
c.save_csv("s1b_walkforward.csv", ["year", "n_test", "hits_top10", "hits_bottom10"], rows)
for nm, h_ in (("top10_hot", hitsT), ("bottom10_cold", hitsB)):
    p0 = .10; rate = h_ / tot; se = np.sqrt(p0 * .9 / tot)
    res["walkforward_" + nm] = dict(n=tot, hits=h_, rate=rate, rate_vs_random=rate / .10, z=(rate - p0) / se, ci95=(rate - 1.96 * np.sqrt(rate * (1 - rate) / tot), rate + 1.96 * np.sqrt(rate * (1 - rate) / tot)))
# (d) sirf 2013+ ke saal, 1966-2012 se seekha hua top10 (FB/GB/GL par bhi: kya DS wala jhukav inme hai?)
cnt = np.bincount(x[Y < 2013], minlength=100); top = np.argsort(cnt)[-10:]; bot = np.argsort(cnt)[:10]
for g in ["FB", "GB", "GL", "DS"]:
    Dg, xg = c.load(g); mg = c.years(Dg) >= 2013; xg = xg[mg]
    for nm, S in (("top10", top), ("bottom10", bot)):
        k = int(np.isin(xg, S).sum()); N = len(xg); z = (k / N - .1) / np.sqrt(.09 / N)
        res["learned_on_DS_1966_2012_tested_on_%s_2013plus_%s" % (g, nm)] = dict(n=N, rate=k / N, z=z, p=c.norm_2p(z))
# (e) digit-level: kaun se tens/unit digit upar/niche (poore DS me), 95% CI
for nm, f in (("tens", x // 10), ("unit", x % 10)):
    cnt = np.bincount(f, minlength=10) / n
    res["DS_all_" + nm + "_share"] = {str(i): [float(cnt[i]), float(1.96 * np.sqrt(cnt[i] * (1 - cnt[i]) / n))] for i in range(10)}
cnt = np.bincount(x, minlength=100); o = np.argsort(cnt)
res["DS_top8_numbers"] = [(int(i), int(cnt[i]), round(float((cnt[i] - n / 100) / np.sqrt(n * .01 * .99)), 2)) for i in o[-8:][::-1]]
res["DS_bottom8_numbers"] = [(int(i), int(cnt[i]), round(float((cnt[i] - n / 100) / np.sqrt(n * .01 * .99)), 2)) for i in o[:8]]
# edge ka andaza: top10 numbers ki asli probability poore DS me
res["DS_top10_share_all"] = float(cnt[o[-10:]].sum() / n)
res["DS_bottom10_share_all"] = float(cnt[o[:10]].sum() / n)
c.save_json("s1b_ds_bias.json", res)
import json; print(json.dumps(res, indent=1, default=float))
