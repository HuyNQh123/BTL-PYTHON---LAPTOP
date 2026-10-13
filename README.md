# Laptops – Quản lý & Khám phá Dữ liệu Laptop

Hệ thống Web Server bằng Python (Flask) phục vụ việc quản lý, làm sạch và tra cứu dữ liệu 225 mẫu laptop thực tế trên thị trường Việt Nam.

---

## 🚀 Các tính năng chính

1. **Khởi tạo Máy chủ Web (Flask Server)**:
   - Server nhẹ nhàng, linh hoạt, cấu trúc phân tầng rõ ràng (Routing, Controller, Data Cleaning Layer).
   - Trang chủ hiển thị số liệu thống kê tổng hợp: Tổng số mẫu, số thương hiệu, giá trung bình và giá cao nhất.
   - Hỗ trợ REST API `/api/laptops` trả về dữ liệu định dạng JSON.

2. **Kho Dữ liệu Laptop (`/laptops`)**:
   - 225 mẫu laptop thực tế với đầy đủ 14 thông số chi tiết (Tên máy, Hãng, CPU, Điểm CPU PassMark, GPU, Điểm GPU PassMark, RAM, Ổ cứng, Màn hình, Tần số quét, Trọng lượng, Pin, Đánh giá, Giá bán).
   - Tích hợp bộ lọc nhanh 1-Click theo nhu cầu sinh viên:
     - 💰 Học tập giá mềm (<= 20 triệu)
     - 🪶 Siêu mỏng nhẹ (<= 1.5 kg)
     - 🔥 Đồ họa & Gaming (GPU rời)
     - 💾 Đa nhiệm mượt (RAM >= 16GB)
     - 🍎 Apple MacBook
   - Hỗ trợ tìm kiếm theo từ khóa thời gian thực, sắp xếp tăng/giảm và phân trang tương tác qua DataTables.

3. **Pipeline Làm sạch Dữ liệu (`src/data_cleaning.py`)**:
   - Tự động xóa trùng lặp (Remove Duplicates).
   - Chuẩn hóa tên thương hiệu (Normalize Brand: ASUS, HP, MSI, Apple...).
   - Chuyển đổi định dạng số (Convert Numeric Columns).
   - Xử lý giá trị khuyết thiếu (Handle Missing Values).

---

## 🛠️ Cấu trúc thư mục

```text
Laptops/
├── data/
│   ├── laptops.csv            # Bộ dữ liệu 225 laptop thực tế
│   └── laptop_sources.csv     # 1.125 trích dẫn nguồn kiểm chứng
├── src/
│   └── data_cleaning.py       # Pipeline làm sạch dữ liệu
├── static/
│   └── css/
│       └── style.css          # Định dạng giao diện
├── templates/
│   ├── base.html              # Layout khung xương
│   ├── index.html             # Trang chủ tổng quan
│   └── laptops.html           # Bảng dữ liệu DataTables & Lọc nhanh
├── app.py                     # Máy chủ web Flask
├── requirements.txt           # Danh sách thư viện cần thiết
└── README.md                  # Hướng dẫn sử dụng
```

---

## ⚙️ Hướng dẫn cài đặt & Khởi chạy

### Bước 1: Mở Terminal tại thư mục `Laptops`

```bash
cd Laptops
```

### Bước 2: Tạo và kích hoạt môi trường ảo (Khuyên dùng)

```bash
python -m venv .venv

# Trên Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Trên Linux / macOS:
source .venv/bin/activate
```

### Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 4: Khởi động Web Server

```bash
python app.py
```

### Bước 5: Truy cập ứng dụng

Mở trình duyệt web và truy cập: **`http://127.0.0.1:5000`** hoặc **`http://127.0.0.1:5000/laptops`**.
