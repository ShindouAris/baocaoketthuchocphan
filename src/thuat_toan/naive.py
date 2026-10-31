


def naive(text, pat):
    """Thuật toán duyệt trâu. (Naive / Brute-force)"""
    n, m = len(text), len(pat)
    res, cmp_ = [], 0
    for i in range(n - m + 1):
        j = 0
        while j < m:
            cmp_ += 1
            if text[i + j] != pat[j]:
                break
            j += 1
        if j == m:
            res.append(i)
    return res, cmp_


"""Độ phức tạp O(n*m)."""