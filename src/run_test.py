import random, time, json, statistics, sys
from pathlib import Path

from thuat_toan.naive import naive
from thuat_toan.kmp import kmp
from thuat_toan.rabin_karp import rabin_karp

# ---------------------------------------------------------------- 1. Thuat toan (moi thuat toan 1 file)
ALGOS = {"Naive": naive, "KMP": kmp, "Rabin-Karp": rabin_karp}

# ---------------------------------------------------------------- 2. Du lieu
def gen_random(n, alphabet, seed):
    r = random.Random(seed)
    return "".join(r.choice(alphabet) for _ in range(n))

def scenarios(n):
    r = random.Random(42)
    sc = []
    # A: van ban dai, mau ngan (ngau nhien, bang chu cai 26 ky tu)
    t = gen_random(n, "abcdefghijklmnopqrstuvwxyz", 1)
    sc.append(("A: Dai-ngan (random 26 ky tu)", t, t[n//2:n//2 + 5]))
    # B1: lap lai cao 'abab...', mau 'aba'
    sc.append(("B1: Lap lai (abab.. / aba)", "ab" * (n // 2), "aba"))
    # B2: truong hop xau nhat cua Naive: aaaa...a / aaa...ab
    sc.append(("B2: Xau nhat Naive (a^n / a^99 b)", "a" * n, "a" * 99 + "b"))
    # B4: moi vi tri deu khop (xau nhat cua Rabin-Karp: hash trung + xac minh m ky tu)
    sc.append(("B4: Moi vi tri khop (a^n / a^50)", "a" * n, "a" * 50))
    # B3: lap lai, mau dai lap lai
    sc.append(("B3: Lap lai (abab.. / (ab)^50 c)", "ab" * (n // 2), "ab" * 50 + "c"))
    # C1: ngau nhien, bang chu cai nhi phan
    t = gen_random(n, "01", 2)
    sc.append(("C1: Random nhi phan, mau 20", t, gen_random(20, "01", 3)))
    # C2: ngau nhien 26 ky tu, mau dai 100 (lay tu van ban)
    t = gen_random(n, "abcdefghijklmnopqrstuvwxyz", 4)
    sc.append(("C2: Random 26 ky tu, mau 100", t, t[n//3:n//3 + 100]))
    return sc

# ---------------------------------------------------------------- 3. Do
def measure(fn, text, pat, repeats=5):
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        res, c = fn(text, pat)
        times.append(time.perf_counter() - t0)
    return min(times), statistics.median(times), res, c

def run(n, repeats=5):
    out = []
    for name, text, pat in scenarios(n):
        ref = [i for i in range(len(text) - len(pat) + 1) if text.startswith(pat, i)]
        for an, fn in ALGOS.items():
            tmin, tmed, res, c = measure(fn, text, pat, repeats)
            assert res == ref, f"{an} sai o kich ban {name}"
            out.append(dict(n=n, scenario=name, algo=an, m=len(pat),
                            matches=len(res), t_min=tmin, t_med=tmed, cmps=c))
    return out

def scaling(sizes, repeats=3):
    out = []
    for n in sizes:
        t = gen_random(n, "abcdefghijklmnopqrstuvwxyz", 7)
        pat = t[n // 2:n // 2 + 8]
        for an, fn in ALGOS.items():
            tmin, tmed, res, c = measure(fn, t, pat, repeats)
            out.append(dict(n=n, algo=an, t_min=tmin, cmps=c))
        t = "a" * n; pat = "a" * 99 + "b"
        for an, fn in ALGOS.items():
            tmin, tmed, res, c = measure(fn, t, pat, repeats)
            out.append(dict(n=n, algo=an, t_min=tmin, cmps=c, worst=True))
    return out

# ---------------------------------------------------------------- 4. Testcases (.in / .out)
TESTDIR = Path(__file__).parent / "testcases"

def read_case(inp):
    text, pat = inp.read_text(encoding="utf-8").splitlines()[:2]
    lines = inp.with_suffix(".out").read_text(encoding="utf-8").splitlines()
    expected = list(map(int, lines[1].split())) if len(lines) > 1 else []
    assert int(lines[0]) == len(expected)
    return text, pat, expected

def run_testcases(repeats=3):
    """Kiem tra dung/sai cua 3 thuat toan tren testcases/*.in va do thoi gian."""
    out, ok = [], True
    files = sorted(TESTDIR.glob("*.in"), key=lambda p: int(p.stem))
    for f in files:
        text, pat, expected = read_case(f)
        for an, fn in ALGOS.items():
            tmin, tmed, res, c = measure(fn, text, pat, repeats)
            passed = res == expected
            ok &= passed
            out.append(dict(case=f.stem, n=len(text), m=len(pat), algo=an,
                            matches=len(res), t_min=tmin, cmps=c, passed=passed))
    return out, ok

if __name__ == "__main__":
    tc, ok = run_testcases()
    print(f"{'Test':6s}{'n':>9s}{'m':>6s}  {'Thuat toan':12s}{'t_min(ms)':>11s}{'so sanh':>12s}{'khop':>9s}  KQ")
    for r in tc:
        print(f"{r['case']:6s}{r['n']:9d}{r['m']:6d}  {r['algo']:12s}{r['t_min']*1000:11.2f}{r['cmps']:12d}{r['matches']:9d}  {'OK' if r['passed'] else 'SAI'}")
    if not ok:
        sys.exit("Co testcase SAI")
    print("Tat ca testcases dung.")
    # N = 1_000_000
    # main = run(N)
    # sc = scaling([100_000, 200_000, 400_000, 800_000, 1_600_000])
    # json.dump(dict(main=main, scaling=sc), open("results.json", "w"), indent=1)
    # print(f"{'Kich ban':42s}{'Thuat toan':12s}{'t_min(ms)':>11s}{'so sanh':>12s}{'khop':>9s}")
    # for r in main:
    #     print(f"{r['scenario']:42s}{r['algo']:12s}{r['t_min']*1000:11.1f}{r['cmps']:12d}{r['matches']:9d}")