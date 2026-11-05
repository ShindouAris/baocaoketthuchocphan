"""Trực quan hóa 3 thuật toán tìm kiếm chuỗi trên terminal.

Chạy:  py visual.py          (cần: py -m pip install inquirer)

- Chọn thuật toán (Naive / KMP / Rabin-Karp / cả 3) bằng inquirer.
- Chọn nguồn dữ liệu: testcase có sẵn (testcases/*.in) hoặc tự nhập text + pattern.
- Chọn tốc độ: từng bước (Enter) / chậm / vừa / nhanh / tức thì.

Các hàm trace_* là bản "ghi lại từng bước" của đúng thuật toán trong naive.py, kmp.py,
rabin_karp.py; cuối mỗi lần chạy kết quả được đối chiếu lại với cài đặt thực.
"""
import bisect
import os
import shutil
import sys
import time
from collections import namedtuple

import inquirer

from thuat_toan.kmp import build_lps
from run_test import ALGOS, TESTDIR, read_case

NL = chr(10)
ESC = chr(27)
ALGO_COLOR = {"Naive": "1;94", "KMP": "1;96", "Rabin-Karp": "1;95"}   # màu riêng mỗi thuật toán
PREFIX = 10  # độ rộng nhãn "Text    : "

# kind: cmp | shift | hash | found ; shift = vị trí đặt đầu mẫu trên text
# ti = chỉ số ký tự text đang xét (hoặc None), pj = chỉ số trong mẫu (hoặc None)
Ev = namedtuple("Ev", "kind shift ti pj ok note")


# ---------------------------------------------------------------- 1. Trace từng thuật toán
def trace_naive(text, pat):
    n, m = len(text), len(pat)
    for i in range(n - m + 1):
        j = 0
        while j < m:
            ok = text[i + j] == pat[j]
            kq = "khớp" if ok else "LỆCH"
            yield Ev("cmp", i, i + j, j, ok,
                     f"Mẫu đặt tại {i}: text[{i + j}]='{text[i + j]}' vs pat[{j}]='{pat[j]}' → {kq}"
                     + ("" if ok else f" → dịch mẫu 1 bước, so lại từ đầu"))
            if not ok:
                break
            j += 1
        if j == m:
            yield Ev("found", i, None, m, True, f"KHỚP tại vị trí {i}")


def trace_kmp(text, pat):
    n, m = len(text), len(pat)
    if m == 0 or m > n:
        return
    lps = build_lps(pat)
    j = 0
    for i in range(n):
        while True:
            ok = text[i] == pat[j]
            kq = "khớp" if ok else "LỆCH"
            yield Ev("cmp", i - j, i, j, ok,
                     f"i={i}, j={j}: text[{i}]='{text[i]}' vs pat[{j}]='{pat[j]}' → {kq}")
            if ok:
                j += 1
                break
            if j > 0:
                nj = lps[j - 1]
                yield Ev("shift", i - j, i, j, False,
                         f"Lệch ở j={j}: j ← lps[{j - 1}]={nj}, dịch mẫu {j - nj} bước, KHÔNG lùi con trỏ text")
                j = nj
            else:
                break
        if j == m:
            yield Ev("found", i - m + 1, None, m, True, f"KHỚP tại vị trí {i - m + 1}")
            j = lps[j - 1]


def trace_rk(text, pat, base=256, mod=1_000_000_007):
    n, m = len(text), len(pat)
    if m == 0 or m > n:
        return
    h = pow(base, m - 1, mod)
    hp = ht = 0
    for i in range(m):
        hp = (hp * base + ord(pat[i])) % mod
        ht = (ht * base + ord(text[i])) % mod
    for i in range(n - m + 1):
        eq = hp == ht
        yield Ev("hash", i, None, None, eq,
                 f"hash(text[{i}:{i + m}])={ht} vs hash(pat)={hp} → "
                 + ("TRÙNG, kiểm tra từng ký tự" if eq else "khác, bỏ qua (không so ký tự)"))
        if eq:
            j = 0
            while j < m:
                ok = text[i + j] == pat[j]
                kq = "khớp" if ok else "LỆCH (hash trùng giả)"
                yield Ev("cmp", i, i + j, j, ok,
                         f"Xác minh: text[{i + j}]='{text[i + j]}' vs pat[{j}]='{pat[j]}' → {kq}")
                if not ok:
                    break
                j += 1
            if j == m:
                yield Ev("found", i, None, m, True, f"KHỚP tại vị trí {i}")
        if i < n - m:
            ht = ((ht - ord(text[i]) * h) * base + ord(text[i + m])) % mod


TRACES = {"Naive": trace_naive, "KMP": trace_kmp, "Rabin-Karp": trace_rk}


# ---------------------------------------------------------------- 2. Vẽ khung hình
def color(code, s):
    return f"{ESC}[{code}m{s}{ESC}[0m"


def clean(s):
    return "".join(c if c.isprintable() else "?" for c in s)


def pat_style(pi, ev):
    """Mã màu ANSI cho ký tự thứ pi của mẫu ở khung ev."""
    if ev.kind == "found":
        return "1;30;42"
    if ev.kind == "hash":
        return "30;43" if ev.ok else "90"
    if pi < ev.pj:
        return "30;42"
    if pi == ev.pj:
        return "30;42" if ev.ok else "97;41"
    return "90"


def frame(name, text, pat, ev, st, compact=False):
    cols = shutil.get_terminal_size((100, 30)).columns
    W = max(20, cols - PREFIX - 1)
    n, m = len(text), len(pat)
    shift = ev.shift
    if shift < st["view"] or shift + min(m, W) > st["view"] + W:
        st["view"] = max(0, shift - 3)
    v = st["view"]
    seg = text[v:v + W]
    found = st["found"]

    tline = []
    for k, ch in enumerate(clean(seg)):
        idx = v + k
        pi = idx - shift
        if 0 <= pi < m:
            tline.append(color(pat_style(pi, ev), ch))
        else:
            f = bisect.bisect_right(found, idx) - 1
            if f >= 0 and idx < found[f] + m:
                tline.append(color("4;32", ch))     # đã khớp ở lượt trước
            else:
                tline.append(ch)
    lines = []
    t_now = st.get("t_end") or time.perf_counter()
    lines.append(color(ALGO_COLOR[name], f"[{name}]") + f"  n={n}  m={m}  bước={st['steps']}  "
                 f"số phép so sánh ký tự={st['cmps']}  số khớp={len(found)}  "
                 + color("1;33", f"⏱ {t_now - st['t0']:.1f}s")
                 + (color("1;32", "  ✔ xong") if st.get("done") else ""))
    lines.append("")
    left = "" if v == 0 else "…"
    lines.append("Text    : " + "".join(tline) + ("…" if v + W < n else ""))
    if ev.ti is not None and v <= ev.ti < v + W:
        lines.append(" " * (PREFIX + ev.ti - v) + color("1;33", "↑") + color("33", f" i={ev.ti}"))
    else:
        lines.append("")
    room = W - (shift - v)
    pcells = [color(pat_style(pi, ev), ch) for pi, ch in enumerate(clean(pat[:max(room, 0)]))]
    lines.append("Pattern : " + " " * (shift - v) + "".join(pcells) + ("…" if m > room else ""))
    lines.append(f"          (mẫu đặt tại vị trí {shift}; cửa sổ text đang xem từ {v}{left and ' (có phần bị ẩn bên trái)'})")
    lines.append("")
    if name == "KMP":
        lines.append("LPS     : " + " ".join(map(str, st["lps"]))[:W])
    elif name == "Rabin-Karp":
        lines.append("Hash    : base=256, mod=10^9+7 (rolling hash)")
    else:
        lines.append("")
    lines.append(color("1", "Bước   : ") + ev.note)
    lines.append("Vị trí khớp: " + (", ".join(map(str, found[:30])) + (" …" if len(found) > 30 else "") if found else "(chưa có)"))
    lines.append(color("42;30", " xanh ") + " khớp   " + color("41;97", " đỏ ") + " lệch   "
                 + color("43;30", " vàng ") + " hash trùng   " + color("4;32", "gạch chân") + " đã khớp trước đó")
    if compact:   # tiêu đề, text, mũi tên, pattern, ghi chú bước
        note = color("1", "Bước   : ") + (ev.note if len(ev.note) < cols - 10 else ev.note[:cols - 11] + "…")
        return [lines[0], lines[2], lines[3], lines[4], note]
    return lines


def banner(name):
    return color(ALGO_COLOR[name], "=" * 30 + f" {name} " + "=" * 30)


def paint(lines):
    out = [ESC + "[H"]
    for ln in lines:
        out.append(ln + ESC + "[K" + NL)
    out.append(ESC + "[J")
    sys.stdout.write("".join(out))
    sys.stdout.flush()


# ---------------------------------------------------------------- 3. Chạy một thuật toán
DELAYS = {"step": None, "slow": 0.5, "normal": 0.15, "fast": 0.03, "instant": 0}


class Abort(Exception):
    pass


def play(name, text, pat, speed):
    st = dict(view=0, found=[], cmps=0, steps=0, t0=time.perf_counter(), lps=build_lps(pat) if pat else [])
    delay = DELAYS[speed]
    instant = speed == "instant"
    animated = not instant
    if animated:
        sys.stdout.write(ESC + "[2J" + ESC + "[?25l")
    last = None
    try:
        for ev in TRACES[name](text, pat):
            st["steps"] += 1
            if ev.kind == "cmp":
                st["cmps"] += 1
            elif ev.kind == "found":
                st["found"].append(ev.shift)
            last = ev
            if not animated:
                continue
            try:
                paint([banner(name)] + frame(name, text, pat, ev, st))
                if delay is None:
                    ans = input(color("90", "Enter = bước tiếp | a = tự chạy | q = thoát | Ctrl+C = chạy nhanh tới cuối > ")).strip().lower()
                    if ans == "q":
                        raise Abort
                    if ans == "a":
                        delay = DELAYS["normal"]
                else:
                    time.sleep(delay)
            except KeyboardInterrupt:
                animated = False          # bỏ animation, tính nhanh tới cuối
    except Abort:
        pass
    finally:
        if speed != "instant":
            sys.stdout.write(ESC + "[?25h")
    st["t_end"] = time.perf_counter()
    st["done"] = True
    if animated and last is not None:
        paint([banner(name)] + frame(name, text, pat, last, st))
    print()
    summarize(name, text, pat, st)


def play_together(text, pat, speed):
    """Chạy 3 thuật toán song song: mỗi nhịp mỗi thuật toán đi 1 bước, 3 khung xếp chồng."""
    names = list(TRACES)
    sts = {a: dict(view=0, found=[], cmps=0, steps=0, done=False, t0=time.perf_counter(), lps=build_lps(pat) if pat else []) for a in names}
    gens = {a: TRACES[a](text, pat) for a in names}
    last = {a: None for a in names}
    delay = DELAYS[speed]
    animated = speed != "instant"
    legend = (color("42;30", " xanh ") + " khớp  " + color("41;97", " đỏ ") + " lệch  "
              + color("43;30", " vàng ") + " hash trùng  " + color("4;32", "gạch chân") + " đã khớp trước đó")
    if animated:
        sys.stdout.write(ESC + "[2J" + ESC + "[?25l")

    def render():
        lines = []
        for a in names:
            lines.append(banner(a))
            if last[a] is not None:
                lines += frame(a, text, pat, last[a], sts[a], compact=True)
            else:
                lines.append(color(ALGO_COLOR[a], f"[{a}]") + " (không có bước nào: mẫu rỗng hoặc dài hơn text)")
        lines.append(color("90", "=" * 70))
        lines.append(legend)
        paint(lines)

    try:
        while not all(sts[a]["done"] for a in names):
            for a in names:
                st = sts[a]
                if st["done"]:
                    continue
                ev = next(gens[a], None)
                if ev is None:
                    st["done"] = True
                    st["t_end"] = time.perf_counter()
                    continue
                st["steps"] += 1
                if ev.kind == "cmp":
                    st["cmps"] += 1
                elif ev.kind == "found":
                    st["found"].append(ev.shift)
                last[a] = ev
            if not animated:
                continue
            try:
                render()
                if delay is None:
                    ans = input(color("90", "Enter = bước tiếp | a = tự chạy | q = thoát | Ctrl+C = chạy nhanh tới cuối > ")).strip().lower()
                    if ans == "q":
                        raise Abort
                    if ans == "a":
                        delay = DELAYS["normal"]
                else:
                    time.sleep(delay)
            except KeyboardInterrupt:
                animated = False
    except Abort:
        pass
    finally:
        if speed != "instant":
            sys.stdout.write(ESC + "[?25h")
    if speed != "instant":
        render()
    print()
    for a in names:
        summarize(a, text, pat, sts[a])
    print(color("1;36", "== So sánh =="))
    print(f"{'Thuật toán':12s}{'số bước':>12s}{'số so sánh ký tự':>20s}{'số khớp':>10s}")
    for a in names:
        s = sts[a]
        print(f"{a:12s}{s['steps']:12d}{s['cmps']:20d}{len(s['found']):10d}")
    print()


def summarize(name, text, pat, st):
    found = st["found"]
    print(color("1;36", f"== Kết quả {name} =="))
    print(f"n={len(text)}, m={len(pat)}, số khớp={len(found)}, số phép so sánh ký tự={st['cmps']}, số bước={st['steps']}")
    print("Vị trí khớp:", (", ".join(map(str, found[:30])) + (" …" if len(found) > 30 else "")) if found else "(không có)")
    res, cmps = ALGOS[name](text, pat)
    ref = [i for i in range(len(text) - len(pat) + 1) if text.startswith(pat, i)] if pat else []
    ok = res == found == ref and cmps == st["cmps"]
    print(color("32", "✔ Trùng với cài đặt thực và với str.startswith") if ok
          else color("31", f"✘ KHÁC cài đặt thực: thực={len(res)} khớp/{cmps} so sánh, str.startswith={len(ref)} khớp"))
    print()


# ---------------------------------------------------------------- 4. Menu inquirer
TC_DESC = {
    "1": "Dài–ngắn, mẫu lấy từ text", "2": "Dài–ngắn, mẫu không tồn tại",
    "3": "Lặp lại: abab… / aba", "4": "Lặp lại: aaa… / a^99 b (xấu nhất Naive)",
    "5": "Lặp lại: (ab)^n / (ab)^50 c", "6": "Lặp lại: aaa… / a^50 (khớp mọi vị trí)",
    "7": "Ngẫu nhiên nhị phân", "8": "Ngẫu nhiên 26 ký tự, mẫu dài 100",
    "9": "Ngẫu nhiên, text và mẫu độc lập", "10": "Biên: mẫu trùng cả text",
    "11": "Biên: mẫu dài hơn text", "12": "Biên: nhiều khớp sát nhau",
    "13": "[Demo ~19s] Dài–ngắn, ngẫu nhiên", "14": "[Demo ~19s] Lặp lại abab… / aba",
    "15": "[Demo ~19s] Xấu nhất Naive: aaa… / aaab", "16": "[Demo ~19s] Xấu nhất Rabin-Karp: aaa… / aaaa",
    "17": "[Demo ~19s] Ngẫu nhiên nhị phân", "18": "[Demo ~19s] Lặp lại (ab)^n / ababc",
}


def ask(questions):
    ans = inquirer.prompt(questions)
    if ans is None:
        raise KeyboardInterrupt
    return ans


def choose_data():
    src = ask([inquirer.List("src", message="Nguồn dữ liệu",
                             choices=[("Testcase có sẵn (testcases/*.in)", "tc"), ("Tự nhập text và pattern", "manual")])])["src"]
    if src == "manual":
        a = ask([inquirer.Text("text", message="Nhập text", validate=lambda _, x: len(x) > 0),
                 inquirer.Text("pat", message="Nhập pattern", validate=lambda _, x: len(x) > 0)])
        return a["text"], a["pat"]
    files = sorted(TESTDIR.glob("*.in"), key=lambda p: int(p.stem))
    if not files:
        sys.exit("Không có testcase nào trong " + str(TESTDIR) + " (chạy py gen_testcases.py)")
    choices = []
    for f in files:
        t, p, exp = read_case(f)
        choices.append((f"{f.stem:>2}: n={len(t):<7} m={len(p):<4} khớp={len(exp):<6} {TC_DESC.get(f.stem, '')}", f))
    f = ask([inquirer.List("tc", message="Chọn testcase", choices=choices)])["tc"]
    t, p, _ = read_case(f)
    return t, p


def main():
    if os.name == "nt":
        os.system("")                       # bật ANSI escape trên Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    while True:
        try:
            algo = ask([inquirer.List("algo", message="Chọn thuật toán",
                                      choices=[("Naive (duyệt trâu)", "Naive"), ("Knuth-Morris-Pratt", "KMP"),
                                               ("Rabin-Karp", "Rabin-Karp"), ("Cả 3 cùng lúc (so sánh)", "together"),
                                               ("Cả 3 (lần lượt)", "all")])])["algo"]
            text, pat = choose_data()
            if len(text) > 3000:
                print(color("33", f"Text dài ({len(text)} ký tự): nên chọn 'Tức thì', hoặc nhấn Ctrl+C khi đang chạy để chạy nhanh tới cuối."))
            speed = ask([inquirer.List("speed", message="Tốc độ",
                                       choices=[("Từng bước (Enter)", "step"), ("Chậm (0.5s)", "slow"),
                                                ("Vừa (0.15s)", "normal"), ("Nhanh (0.03s)", "fast"),
                                                ("Tức thì (chỉ in kết quả)", "instant")])])["speed"]
            if algo == "together":
                play_together(text, pat, speed)
            else:
                for name in (list(TRACES) if algo == "all" else [algo]):
                    play(name, text, pat, speed)
            if not ask([inquirer.Confirm("again", message="Chạy tiếp?", default=True)])["again"]:
                break
        except KeyboardInterrupt:
            sys.stdout.write(ESC + "[?25h")
            break


if __name__ == "__main__":
    main()
