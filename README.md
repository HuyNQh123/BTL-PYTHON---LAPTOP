# Laptops – Quản lý & Dự đoán Giá Laptop (Machine Learning)

Hệ thống Web Server bằng Python (Flask) tích hợp Trí tuệ Nhân tạo / Học máy (Machine Learning) phục vụ việc quản lý, làm sạch và dự đoán giá bán laptop từ 225 mẫu máy thực tế trên thị trường Việt Nam.

---

## 🚀 Các tính năng chính

### 1. Khởi tạo Máy chủ Web (Flask Server)
- Server nhẹ nhàng, linh hoạt, cấu trúc phân tầng rõ ràng (Routing, Controller, Data Cleaning Layer, ML Prediction Layer).
- Trang chủ hiển thị số liệu thống kê tổng hợp: Tổng số mẫu (225 laptop), số thương hiệu (8 hãng), giá trung bình và giá cao nhất.
- Hỗ trợ đầy đủ REST API:
  - `GET /api/laptops`: Trả về toàn bộ danh sách laptop dưới dạng JSON.
  - `POST /api/predict`: API dự đoán giá bán tức thì từ payload 9 thông số kỹ thuật và đề xuất 5 mẫu tương đồng.

### 2. Kho Dữ liệu Laptop (`/laptops`)
- 225 mẫu laptop thực tế với đầy đủ 14 thông số chi tiết (Tên máy, Hãng, CPU, Điểm CPU PassMark, GPU, Điểm GPU PassMark, RAM, Ổ cứng, Màn hình, Tần số quét, Trọng lượng, Pin, Đánh giá, Giá bán).
- Tích hợp bộ lọc nhanh 1-Click theo nhu cầu sinh viên:
  - 💰 Học tập giá mềm (<= 20 triệu)
  - 🪶 Siêu mỏng nhẹ (<= 1.5 kg)
  - 🔥 Đồ họa & Gaming (GPU rời)
  - 💾 Đa nhiệm mượt (RAM >= 16GB)
  - 🍎 Apple MacBook
- Hỗ trợ tìm kiếm theo từ khóa thời gian thực, sắp xếp tăng/giảm và phân trang tương tác qua DataTables.

### 3. Pipeline Làm sạch Dữ liệu (`src/data_cleaning.py`)
- Tự động xóa trùng lặp (Remove Duplicates).
- Chuẩn hóa tên thương hiệu (Normalize Brand: ASUS, HP, MSI, Apple...).
- Chuyển đổi định dạng số (Convert Numeric Columns).
- Xử lý giá trị khuyết thiếu (Handle Missing Values với Median cho số, N/A cho chuỗi).

### 4. Dự đoán Giá Laptop bằng Machine Learning (Phần 4 - `/predict`)
- **Huấn luyện & Đánh giá 2 Mô hình Học máy**:
  - **Linear Regression Pipeline**: Tích hợp bộ chuẩn hóa dữ liệu `StandardScaler()`.
  - **Random Forest Regressor**: Mô hình rừng ngẫu nhiên 100 cây quyết định (`n_estimators=100, random_state=42`).
- **Đánh giá khách quan trên tập Test (20% = 45 mẫu)**:
  - **Linear Regression**: $MAE \approx 6,060,150$ VNĐ | $RMSE \approx 7,791,430$ VNĐ | $R^2 \approx 0.8098$.
  - **Random Forest Regressor**: $MAE \approx 4,106,067$ VNĐ | $RMSE \approx 6,133,598$ VNĐ | $R^2 \approx 0.8821$.
  - Mô hình có $R^2$ cao hơn (**Random Forest Regressor**) được tự động đóng gói bằng `joblib` vào `models/laptop_price_model.pkl`.
- **Giao diện Định giá & Tư vấn 2 Lớp**:
  - **Lớp 1 - Preset 1-Click theo ngành học**: Kinh tế / Văn phòng / Xã hội, CNTT / Lập trình, Đồ họa / Kỹ thuật / Gaming.
  - **Lớp 2 - Tùy chỉnh 9 thông số kỹ thuật**: Điểm CPU PassMark, Điểm GPU PassMark, RAM, Ổ cứng, Kích thước màn hình, Tần số quét, Trọng lượng, Dung lượng pin, Điểm đánh giá (Rating).
- **Thuật toán Đề xuất Top 5 Laptop tương đồng**:
  - Lọc các mẫu trong dải chênh lệch giá $\pm 1 - 2$ triệu VNĐ so với giá dự đoán.
  - Chuẩn hóa Z-score và trọng số hóa linh kiện cốt lõi: CPU Mark (2.5), GPU Mark (2.5), RAM (2.0), Ổ cứng (1.5), Màn hình (1.0), Tần số quét (1.0), Trọng lượng (1.0), Dung lượng Pin (1.0).
  - Tính tỷ lệ phần trăm tương đồng cấu hình (% similarity) và xếp hạng gợi ý.

---

## 🛠️ Cấu trúc thư mục dự án

```text
Laptops/
├── data/
│   ├── laptops.csv                  # Bộ dữ liệu 225 laptop thực tế
│   └── laptop_sources.csv           # 1.125 trích dẫn nguồn kiểm chứng
├── models/
│   └── laptop_price_model.pkl       # Mô hình Học máy (ML Pipeline) đã huấn luyện
├── src/
│   ├── data_cleaning.py             # Pipeline làm sạch dữ liệu
│   └── price_prediction.py          # Huấn luyện, đánh giá & dự đoán giá (Phần 4)
├── static/
│   └── css/
│       └── style.css                # Định dạng giao diện tùy biến
├── templates/
│   ├── base.html                    # Layout khung xương chuẩn Bootstrap 5
│   ├── index.html                   # Trang chủ tổng quan & banner Phần 4
│   ├── laptops.html                 # Bảng dữ liệu DataTables & Lọc nhanh
│   └── predict.html                 # Giao diện Form định giá & tư vấn cấu hình
├── app.py                           # Máy chủ web Flask (hỗ trợ Web & REST API)
├── requirements.txt                 # Danh sách thư viện cần thiết
└── README.md                        # Tài liệu hướng dẫn sử dụng
```

---

## ⚙️ Hướng dẫn cài đặt & Khởi chạy

### Bước 1: Mở Terminal tại thư mục `Laptops`

```bash
cd Laptops
```

### Bước 2: Kích hoạt môi trường ảo Python

```powershell
# Trên Windows PowerShell:
.\.venv\Scripts\Activate.ps1
```

### Bước 3: Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

### Bước 4: (Tùy chọn) Chạy kiểm thử độc lập Module Dự đoán giá

```bash
python -m src.price_prediction
```

### Bước 5: Khởi động Web Server Flask

```bash
python app.py
```

### Bước 6: Mở trình duyệt web để trải nghiệm

- **Trang chủ**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Kho dữ liệu 225 laptop**: [http://127.0.0.1:5000/laptops](http://127.0.0.1:5000/laptops)
- **Dự đoán giá & Gợi ý tương đồng (Phần 4)**: [http://127.0.0.1:5000/predict](http://127.0.0.1:5000/predict)
- **REST API Dự đoán giá**: `POST http://127.0.0.1:5000/api/predict`
