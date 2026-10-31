"""Sinh cac file testcases/*.in va *.out.

Dinh dang .in : dong 1 = van ban (text), dong 2 = mau (pattern).
Dinh dang .out: dong 1 = so vi tri khop, dong 2 = cac vi tri khop (tinh tu 0), cach nhau boi dau cach.
Ket qua .out duoc tinh bang str.find (doc lap voi 3 thuat toan can kiem tra).

Chay: py gen_testcases.py
"""
import random
from pathlib import Path

DIR = Path(__file__).parent.parent / "testcases"
ALPHA = "abcdefghijklmnopqrstuvwxyz"


def rnd(n, alphabet, seed):
    r = random.Random(seed)
    return "".join(r.choice(alphabet) for _ in range(n))


def find_all(text, pat):
    res, i = [], text.find(pat)
    while i != -1:
        res.append(i)
        i = text.find(pat, i + 1)      # cho phep khop chong lan
    return res


def cases():
    n = 100_000
    t1 = rnd(n, ALPHA, 1)
    t7 = rnd(n, "01", 7)
    t8 = rnd(n, ALPHA, 8)
    return [
        # Nhom 1: van ban dai, mau ngan
        ("1", t1, t1[n // 2:n // 2 + 5]),                  # mau lay tu van ban
        ("2", t1, "#####"),                                # mau khong ton tai
        # Nhom 2: van ban lap lai cao, mau lap lai
        ("3", "ab" * (n // 2), "aba"),                     # khop chong lan lien tuc
        ("4", "a" * n, "a" * 99 + "b"),                    # xau nhat cua Naive, khong khop
        ("5", "ab" * (n // 2), "ab" * 50 + "c"),           # lap lai, khong khop
        ("6", "a" * 20_000, "a" * 50),                     # moi vi tri deu khop (xau nhat Rabin-Karp)
        # Nhom 3: ngau nhien
        ("7", t7, rnd(20, "01", 70)),                      # nhi phan
        ("8", t8, t8[n // 3:n // 3 + 100]),                # 26 ky tu, mau dai 100
        ("9", rnd(n, ALPHA, 9), rnd(8, ALPHA, 90)),        # van ban va mau doc lap
        # Bien
        ("10", "abc", "abc"),                              # mau trung ca van ban
        ("11", "abc", "abcd"),                             # mau dai hon van ban
        ("12", "abcabcabc", "abc"),                        # nhieu khop sat nhau
        # Test nho cho visual.py: che do "ca 3 cung luc", toc do Vua (0.15s/buoc) ~ 126 buoc ~ 19 giay
        ("13", rnd(107, "abcdefghij", 11), "cab"),         # dai-ngan, ngau nhien
        ("14", "ab" * 22, "aba"),                          # lap lai, khop chong lan
        ("15", "a" * 34, "aaab"),                          # xau nhat cua Naive, khong khop
        ("16", "a" * 24, "aaaa"),                          # moi vi tri khop (xau nhat Rabin-Karp)
        ("17", rnd(66, "ab", 3), "abba"),                  # ngau nhien nhi phan
        ("18", "ab" * 23, "ababc"),                        # lap lai, khong khop
    ]


def main():
    DIR.mkdir(exist_ok=True)
    for name, text, pat in cases():
        pos = find_all(text, pat)
        (DIR / f"{name}.in").write_text(f"{text}\n{pat}\n", encoding="utf-8")
        (DIR / f"{name}.out").write_text(f"{len(pos)}\n{' '.join(map(str, pos))}\n", encoding="utf-8")
        print(f"{name}.in/.out: n={len(text)}, m={len(pat)}, so khop={len(pos)}")


if __name__ == "__main__":
    main()
