

def build_lps(pat):
    """Bảng tiền tố - hậu tố dài nhắt (longest proper prefix which is also suffix)."""
    m = len(pat)
    lps = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and pat[i] != pat[k]:
            k = lps[k - 1]
        if pat[i] == pat[k]:
            k += 1
        lps[i] = k
    return lps


def kmp(text, pat):
    """Trả về danh sách các vị trí khớp và số phép so sánh ký tự."""
    n, m = len(text), len(pat)
    res, cmp_ = [], 0
    if m == 0 or m > n:
        return res, cmp_
    lps = build_lps(pat)
    j = 0
    for i in range(n):
        while True:
            cmp_ += 1
            if text[i] == pat[j]:
                j += 1
                break
            if j > 0:
                j = lps[j - 1]      # dịch mẫu, không dịch văn bản
            else:
                break
        if j == m:
            res.append(i - m + 1)
            j = lps[j - 1]
    return res, cmp_


"""Thuật toán Knuth-Morris-Pratt. Độ phức tạp O(n + m)."""
