"""Tạo bảng so sánh (markdown) cho thuyết trình từ 5 testcase tiêu biểu.

Chạy:  py bang_so_sanh.py      -> in ra màn hình và ghi bang_so_sanh.md
Thời gian = nhỏ nhất của 3 lần chạy (ms); số phép so sánh = số lần so sánh ký tự.
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from main import ALGOS, TESTDIR, measure, read_case

# (file testcase, nhóm theo đề bài, tên tình huống, vì sao chọn)
CHON = [
    ("2", "Văn bản dài, mẫu ngắn", "Văn bản ngẫu nhiên, mẫu không có trong văn bản",
     "Trường hợp thông thường nhất: tìm một từ ngắn trong văn bản dài"),
    ("3", "Văn bản lặp lại", "Văn bản abab…ab, mẫu aba (khớp chồng lấn liên tục)",
     "Văn bản và mẫu cùng lặp lại, có rất nhiều vị trí khớp"),
    ("4", "Văn bản lặp lại", "Văn bản toàn chữ a, mẫu aaa…ab (99 chữ a + b)",
     "Xấu nhất của Naive: mỗi vị trí so gần hết mẫu rồi mới lệch ở ký tự cuối"),
    ("6", "Văn bản lặp lại", "Văn bản toàn chữ a, mẫu 50 chữ a (khớp ở mọi vị trí)",
     "Xấu nhất của Rabin-Karp: hash luôn trùng nên lần nào cũng phải kiểm tra lại cả mẫu"),
    ("8", "Văn bản và mẫu ngẫu nhiên", "Văn bản ngẫu nhiên 26 chữ cái, mẫu dài 100 ký tự",
     "Dữ liệu ngẫu nhiên với mẫu dài"),
]
TEN = list(ALGOS)
NL = chr(10)
MAU = {"Naive": "#d9534f", "KMP": "#337ab7", "Rabin-Karp": "#5cb85c"}
# nhãn ngắn (xuống dòng) cho trục x của biểu đồ, theo thứ tự CHON
NHAN = [
    ["Text ngẫu nhiên", "mẫu ngắn (5 ký tự)", "không khớp"],
    ["Text abab…ab", "mẫu aba", "khớp chồng lấn"],
    ["Text toàn 'a'", "mẫu a⁹⁹b", "(xấu nhất của Naive)"],
    ["Text toàn 'a'", "mẫu a⁵⁰", "(xấu nhất của Rabin-Karp)"],
    ["Text ngẫu nhiên", "mẫu dài (100 ký tự)"],
]


def fmt_ms(x):
    return f"{x:,.1f}".replace(",", ".")


def fmt_int(x):
    return f"{x:,}".replace(",", ".")


def do():
    rows = []
    for tc, nhom, ten, ly_do in CHON:
        text, pat, exp = read_case(TESTDIR / f"{tc}.in")
        r = {"nhom": nhom, "ten": ten, "ly_do": ly_do, "n": len(text), "m": len(pat), "khop": len(exp)}
        for a in TEN:
            tmin, _, res, cmps = measure(ALGOS[a], text, pat, 3)
            assert res == exp, f"{a} sai ở testcase {tc}"
            r[a] = (tmin * 1000, cmps)
        rows.append(r)
        print(f"  xong testcase {tc}", file=sys.stderr)
    return rows


def best(vals):
    """Chỉ số các giá trị nhỏ nhất (cho phép hòa trong 5%)."""
    lo = min(vals)
    return {i for i, v in enumerate(vals) if v <= lo * 1.05}


def ve(rows, khoa, ten_file, tieu_de, ylabel, he_so=1.0, nho_nhat=1e-1):
    """Biểu đồ cột nhóm, trục y logarit; ghi giá trị lên đầu mỗi cột."""
    x = range(len(rows))
    w = 0.27
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, a in enumerate(TEN):
        vals = [r[a][khoa] * he_so for r in rows]
        pos = [k + (i - 1) * w for k in x]
        bars = ax.bar(pos, vals, w, label=a, color=MAU[a])
        for b, v in zip(bars, vals):
            txt = fmt_ms(v) if khoa == 0 else fmt_int(int(v))
            y = b.get_height() if v > 0 else nho_nhat * 2      # giá trị 0: không có cột, chỉ ghi số 0
            ax.annotate(txt, (b.get_x() + b.get_width() / 2, y), xytext=(0, 3),
                        textcoords="offset points", ha="center", fontsize=8)
    ax.set_yscale("log")
    ax.set_xticks(list(x))
    ax.set_xticklabels([NL.join(n) for n in NHAN[:len(rows)]], fontsize=9)
    ax.set_ylabel(ylabel)
    ax.set_title(tieu_de, fontsize=13, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=nho_nhat if khoa else None, top=ax.get_ylim()[1] * 3)
    ax.legend(title="Thuật toán")
    fig.tight_layout()
    fig.savefig(ten_file, dpi=150)
    plt.close(fig)


def ve_tat_ca(rows):
    ve(rows, 0, "chart_thoi_gian.png", "Thời gian chạy của 3 thuật toán (thấp hơn = nhanh hơn)",
       "Thời gian (mili giây, thang logarit)")
    ve(rows, 1, "chart_so_sanh.png", "Số phép so sánh ký tự (thấp hơn = ít việc hơn)",
       "Số phép so sánh (thang logarit; ghi 0 = không so sánh lần nào)", nho_nhat=0.5)


def md(rows):
    out = ["# So sánh 3 thuật toán tìm kiếm chuỗi", "",
           "Đo trên máy thật, Python; thời gian là nhỏ nhất của 3 lần chạy. **In đậm = nhanh nhất / ít phép so sánh nhất.**", "",
           "## Bảng 1. Thời gian chạy (mili giây, càng nhỏ càng tốt)", "",
           "| Tình huống | Độ dài văn bản | Độ dài mẫu | Số vị trí khớp | Naive (duyệt trâu) | KMP | Rabin-Karp |",
           "|---|--:|--:|--:|--:|--:|--:|"]
    for r in rows:
        t = [r[a][0] for a in TEN]
        b = best(t)
        cells = [f"**{fmt_ms(v)}**" if i in b else fmt_ms(v) for i, v in enumerate(t)]
        out.append(f"| {r['ten']} | {fmt_int(r['n'])} | {fmt_int(r['m'])} | {fmt_int(r['khop'])} | " + " | ".join(cells) + " |")
    out += ["", "## Bảng 2. Số phép so sánh ký tự (càng nhỏ càng tốt)", "",
            "| Tình huống | Naive (duyệt trâu) | KMP | Rabin-Karp |", "|---|--:|--:|--:|"]
    for r in rows:
        c = [r[a][1] for a in TEN]
        b = best(c)
        cells = [f"**{fmt_int(v)}**" if i in b else fmt_int(v) for i, v in enumerate(c)]
        out.append(f"| {r['ten']} | " + " | ".join(cells) + " |")
    out += ["", "![Biểu đồ thời gian chạy](chart_thoi_gian.png)", "", "![Biểu đồ số phép so sánh](chart_so_sanh.png)"]
    out += ["", "> Rabin-Karp chỉ so sánh ký tự khi hash trùng, nên số phép so sánh có thể rất nhỏ (thậm chí 0) dù vẫn phải tính hash ở mọi vị trí; vì vậy cần đối chiếu cả hai bảng.", "",
            "## Vì sao chọn các tình huống này", "",
            "| Tình huống | Thuộc nhóm của đề bài | Lý do chọn |", "|---|---|---|"]
    for r in rows:
        out.append(f"| {r['ten']} | {r['nhom']} | {r['ly_do']} |")
    return NL.join(out) + NL


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rows = do()
    ve_tat_ca(rows)
    text = md(rows)
    open("bang_so_sanh.md", "w", encoding="utf-8").write(text)
    print(text)
