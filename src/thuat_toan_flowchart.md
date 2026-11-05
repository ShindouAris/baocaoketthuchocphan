# Lưu đồ 3 thuật toán tìm kiếm chuỗi

Dựa trên cài đặt thực trong `thuat_toan/naive.py`, `thuat_toan/kmp.py`, `thuat_toan/rabin_karp.py`.
Cả 3 thuật toán đều trả về: danh sách vị trí khớp và số phép so sánh ký tự.

## 1. Thuật toán duyệt trâu (Naive), độ phức tạp O(n·m)

```mermaid
flowchart TD
    A(["Bắt đầu: nhận văn bản và mẫu"]) --> B["Tính độ dài văn bản và độ dài mẫu<br/>Danh sách vị trí khớp = rỗng<br/>Số phép so sánh = 0"]
    B --> C["Đặt vị trí đặt mẫu = 0"]
    C --> D{"Vị trí đặt mẫu<br/>≤ độ dài văn bản − độ dài mẫu ?"}
    D -- Không --> Z(["Trả về danh sách vị trí khớp<br/>và số phép so sánh"])
    D -- Có --> E["Số ký tự đã khớp = 0"]
    E --> F{"Số ký tự đã khớp<br/>< độ dài mẫu ?"}
    F -- Không --> I
    F -- Có --> G["Số phép so sánh tăng 1"]
    G --> H{"Ký tự văn bản<br/>khác ký tự mẫu ?"}
    H -- Có --> I
    H -- Không --> H1["Số ký tự đã khớp tăng 1"] --> F
    I{"Đã khớp đủ<br/>toàn bộ mẫu ?"}
    I -- Có --> J["Thêm vị trí đặt mẫu<br/>vào danh sách vị trí khớp"] --> K
    I -- Không --> K["Dịch mẫu sang phải 1 bước<br/>(so lại từ đầu mẫu)"]
    K --> D
```

## 2. Thuật toán Knuth-Morris-Pratt (KMP), độ phức tạp O(n + m)

### 2a. Xây bảng tiền tố – hậu tố

```mermaid
flowchart TD
    A(["Bắt đầu: nhận mẫu"]) --> B["Bảng tiền tố–hậu tố gồm toàn số 0<br/>Độ dài tiền tố đang khớp = 0"]
    B --> C["Xét ký tự thứ 2 của mẫu trở đi"]
    C --> D{"Còn ký tự<br/>chưa xét ?"}
    D -- Không --> Z(["Trả về bảng tiền tố–hậu tố"])
    D -- Có --> E{"Độ dài tiền tố đang khớp > 0<br/>và ký tự đang xét khác<br/>ký tự kế tiếp của tiền tố ?"}
    E -- Có --> F["Thu ngắn tiền tố:<br/>lấy giá trị đã ghi ở ô liền trước"] --> E
    E -- Không --> G{"Ký tự đang xét giống<br/>ký tự kế tiếp của tiền tố ?"}
    G -- Có --> H["Độ dài tiền tố đang khớp tăng 1"] --> I
    G -- Không --> I["Ghi độ dài tiền tố đang khớp<br/>vào ô của ký tự đang xét"]
    I --> J["Chuyển sang ký tự kế tiếp"] --> D
```

### 2b. Tìm kiếm bằng KMP

```mermaid
flowchart TD
    A(["Bắt đầu: nhận văn bản và mẫu"]) --> B["Tính độ dài văn bản và độ dài mẫu<br/>Danh sách vị trí khớp = rỗng<br/>Số phép so sánh = 0"]
    B --> C{"Mẫu rỗng hoặc<br/>mẫu dài hơn văn bản ?"}
    C -- Có --> Z(["Trả về danh sách vị trí khớp<br/>và số phép so sánh"])
    C -- Không --> D["Xây bảng tiền tố–hậu tố của mẫu<br/>Số ký tự đã khớp = 0<br/>Vị trí đang xét trên văn bản = 0"]
    D --> E{"Còn ký tự nào<br/>của văn bản chưa xét ?"}
    E -- Không --> Z
    E -- Có --> F["Số phép so sánh tăng 1"]
    F --> G{"Ký tự văn bản giống<br/>ký tự kế tiếp của mẫu ?"}
    G -- Có --> H["Số ký tự đã khớp tăng 1"] --> L
    G -- Không --> I{"Số ký tự đã khớp > 0 ?"}
    I -- Có --> J["Dịch mẫu theo bảng tiền tố–hậu tố:<br/>số ký tự đã khớp = giá trị ở ô liền trước<br/>(KHÔNG lùi con trỏ văn bản)"] --> F
    I -- Không --> L
    L{"Đã khớp đủ<br/>toàn bộ mẫu ?"}
    L -- Có --> M["Thêm vị trí đầu của đoạn khớp<br/>vào danh sách vị trí khớp<br/>Dịch mẫu theo bảng tiền tố–hậu tố"] --> N
    L -- Không --> N["Chuyển sang ký tự kế tiếp<br/>của văn bản"]
    N --> E
```

## 3. Thuật toán Rabin-Karp, trung bình O(n + m), xấu nhất O(n·m)

```mermaid
flowchart TD
    A(["Bắt đầu: nhận văn bản, mẫu,<br/>cơ số = 256, modulo = 10^9 + 7"]) --> B["Tính độ dài văn bản và độ dài mẫu<br/>Danh sách vị trí khớp = rỗng<br/>Số phép so sánh = 0"]
    B --> C{"Mẫu rỗng hoặc<br/>mẫu dài hơn văn bản ?"}
    C -- Có --> Z(["Trả về danh sách vị trí khớp<br/>và số phép so sánh"])
    C -- Không --> D["Tính hệ số của ký tự đầu cửa sổ<br/>= cơ số mũ (độ dài mẫu − 1) theo modulo"]
    D --> E["Tính mã băm của mẫu<br/>và mã băm của cửa sổ đầu tiên của văn bản<br/>(đọc từng ký tự: nhân cơ số, cộng mã ký tự, lấy dư)"]
    E --> F["Đặt vị trí cửa sổ = 0"]
    F --> G{"Vị trí cửa sổ<br/>≤ độ dài văn bản − độ dài mẫu ?"}
    G -- Không --> Z
    G -- Có --> H{"Mã băm cửa sổ<br/>bằng mã băm mẫu ?"}
    H -- Không --> R
    H -- Có --> I["Số ký tự đã khớp = 0"]
    I --> J{"Số ký tự đã khớp<br/>< độ dài mẫu ?"}
    J -- Không --> O
    J -- Có --> K["Số phép so sánh tăng 1"]
    K --> L{"Ký tự văn bản<br/>khác ký tự mẫu ?"}
    L -- Có --> O
    L -- Không --> M["Số ký tự đã khớp tăng 1"] --> J
    O{"Đã khớp đủ<br/>toàn bộ mẫu ?"}
    O -- Có --> P["Thêm vị trí cửa sổ<br/>vào danh sách vị trí khớp"] --> R
    O -- "Không (mã băm trùng giả)" --> R
    R{"Còn cửa sổ<br/>kế tiếp ?"}
    R -- Có --> S["Cập nhật mã băm lăn (rolling hash):<br/>bỏ ký tự đầu cửa sổ,<br/>thêm ký tự ngay sau cửa sổ"] --> T
    R -- Không --> T["Trượt cửa sổ sang phải 1 vị trí"]
    T --> G
```

## So sánh nhanh

| Thuật toán | Ý tưởng | Con trỏ văn bản | Độ phức tạp |
|---|---|---|---|
| Duyệt trâu | Thử mọi vị trí, so từ đầu mẫu | Quay lại khi lệch (dịch mẫu 1 bước, so lại từ đầu mẫu) | O(n·m) |
| KMP | Dùng bảng tiền tố–hậu tố để dịch mẫu thông minh | Không bao giờ lùi | O(n + m) |
| Rabin-Karp | So mã băm trước, chỉ so ký tự khi mã băm trùng | Trượt cửa sổ bằng mã băm lăn | Trung bình O(n + m), xấu nhất O(n·m) |
