## Trình tạo bảng
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

d = json.load(open("results.json"))
main, sc = d["main"], d["scaling"]
order = []
for r in main:
    if r["scenario"] not in order: order.append(r["scenario"])
order.sort()
algos = ["Naive", "KMP", "Rabin-Karp"]
colors = {"Naive": "#d9534f", "KMP": "#337ab7", "Rabin-Karp": "#5cb85c"}
short = [s.split(":")[0] for s in order]

def grid(key, scale):
    return {a: [next(r[key] for r in main if r["scenario"] == s and r["algo"] == a) * scale for s in order] for a in algos}

def bars(key, scale, ylabel, title, fname, log=True):
    v = grid(key, scale); x = np.arange(len(order)); w = 0.27
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, a in enumerate(algos):
        ax.bar(x + (i - 1) * w, [max(t, 1e-1) for t in v[a]], w, label=a, color=colors[a])
    ax.set_xticks(x); ax.set_xticklabels(short)
    if log: ax.set_yscale("log")
    ax.set_ylabel(ylabel); ax.set_title(title); ax.legend(); ax.grid(axis="y", alpha=.3)
    fig.tight_layout(); fig.savefig(fname, dpi=150); plt.close(fig)

bars("t_min", 1000, "Thời gian (ms, thang log)", "Thời gian chạy theo kịch bản (n = 1.000.000)", "chart1_time.png")
bars("cmps", 1, "Số phép so sánh ký tự (thang log)", "Số phép so sánh ký tự theo kịch bản", "chart2_comparisons.png")

fig, axs = plt.subplots(1, 2, figsize=(11, 4.5))
for ax, worst, ttl in [(axs[0], False, "Văn bản ngẫu nhiên, mẫu 8 ký tự"), (axs[1], True, "Xấu nhất của Naive: aⁿ / a⁹⁹b")]:
    for a in algos:
        pts = [(r["n"], r["t_min"] * 1000) for r in sc if r["algo"] == a and bool(r.get("worst")) == worst]
        ax.plot(*zip(*pts), marker="o", label=a, color=colors[a])
    ax.set_title(ttl); ax.set_xlabel("Độ dài văn bản n"); ax.set_ylabel("Thời gian (ms)"); ax.grid(alpha=.3); ax.legend()
fig.tight_layout(); fig.savefig("chart3_scaling.png", dpi=150)