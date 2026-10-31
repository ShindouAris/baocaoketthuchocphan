def rabin_karp(text, pat, base=256, mod=1_000_000_007):
    """Thuật toán Rabin-Karp."""
    n, m = len(text), len(pat)
    res, cmp_ = [], 0
    if m == 0 or m > n:
        return res, cmp_
    h = pow(base, m - 1, mod)
    hp = ht = 0
    for i in range(m):
        hp = (hp * base + ord(pat[i])) % mod
        ht = (ht * base + ord(text[i])) % mod
    for i in range(n - m + 1):
        if hp == ht:                       # nếu hash khớp, kiểm tra từng ký tự
            j = 0
            while j < m:
                cmp_ += 1
                if text[i + j] != pat[j]:
                    break
                j += 1
            if j == m:
                res.append(i)
        if i < n - m:
            ht = ((ht - ord(text[i]) * h) * base + ord(text[i + m])) % mod
    return res, cmp_


"""AVG O(n + m), Worst O(n*m)."""