import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Thiết lập UTF-8
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def set_cell_background(cell, fill_hex):
    """Đặt màu nền cho cell trong bảng."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    """Thiết lập padding cho cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report():
    doc = docx.Document()
    
    # Định dạng trang A4
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        
    COLOR_PRIMARY = RGBColor(13, 110, 253)    # Xanh dương Bootstrap
    COLOR_DARK = RGBColor(33, 37, 41)         # Xám đen
    COLOR_MUTED = RGBColor(108, 117, 125)     # Xám mờ
    COLOR_SUCCESS = RGBColor(25, 135, 84)     # Xanh lá
    HEX_PRIMARY_BG = "E7F1FF"
    HEX_HEADER_BG = "0D6EFD"
    HEX_ALT_ROW = "F8F9FA"

    # ==================== TRANG BÌA TIÊU ĐỀ ====================
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(10)
    title_p.paragraph_format.space_after = Pt(4)
    run_sub = title_p.add_run("BÁO CÁO KỸ THUẬT DỰ ÁN KHOA HỌC DỮ LIỆU & HỌC MÁY\n")
    run_sub.font.size = Pt(13)
    run_sub.font.bold = True
    run_sub.font.color.rgb = COLOR_MUTED

    run_title = title_p.add_run("PHẦN 4: XÂY DỰNG MÔ HÌNH HỌC MÁY DỰ ĐOÁN GIÁ LAPTOP\n& HỆ THỐNG GỢI Ý CẤU HÌNH TƯƠNG ĐỒNG\n")
    run_title.font.size = Pt(19)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    run_proj = title_p.add_run("(LAPINSIGHT – LAPTOP PRICE PREDICTION SYSTEM)\n")
    run_proj.font.size = Pt(13)
    run_proj.font.bold = True
    run_proj.font.color.rgb = COLOR_DARK

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(18)
    run_meta = p_meta.add_run("Tập dữ liệu: 225 Laptop thực tế | Ngôn ngữ: Python 3.13 | Framework: Flask & Scikit-Learn | Năm thực hiện: 2026")
    run_meta.font.size = Pt(10)
    run_meta.font.italic = True
    run_meta.font.color.rgb = COLOR_MUTED

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ==================== MỤC LỤC TÓM TẮT ====================
    h_toc = doc.add_heading("CẤU TRÚC NỘI DUNG BÁO CÁO", level=1)
    h_toc.paragraph_format.space_after = Pt(6)
    
    toc_p = doc.add_paragraph()
    toc_p.paragraph_format.line_spacing = 1.2
    toc_items = [
        "CHƯƠNG 1: TỔNG QUAN BÀI TOÁN DỰ ĐOÁN GIÁ & NGĂN XẾP CÔNG NGHỆ",
        "CHƯƠNG 2: TIỀN XỬ LÝ & THIẾT KẾ PIPELINE HUẤN LUYỆN MÔ HÌNH",
        "CHƯƠNG 3: ĐÁNH GIÁ, SO SÁNH HIỆU NĂNG MÔ HÌNH & ĐÓNG GÓI JOBLIB",
        "CHƯƠNG 4: THUẬT TOÁN GỢI Ý TOP 5 LAPTOP TƯƠNG ĐỒNG (SIMILARITY SCORING)",
        "CHƯƠNG 5: THIẾT KẾ GIAO DIỆN FORM ĐỊNH GIÁ 2 LỚP & REST API ENDPOINTS",
        "CHƯƠNG 6: HƯỚNG DẪN KHỞI CHẠY & KẾT QUẢ KIỂM THỬ THỰC TẾ",
        "CHƯƠNG 7: KẾT LUẬN & HƯỚNG ỨNG DỤNG THỰC TIỄN"
    ]
    for item in toc_items:
        r = toc_p.add_run(f"• {item}\n")
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ==================== CHƯƠNG 1 ====================
    doc.add_heading("CHƯƠNG 1: TỔNG QUAN BÀI TOÁN DỰ ĐOÁN GIÁ & CÔNG NGHỆ", level=1)
    
    p = doc.add_paragraph()
    p.add_run("1.1. Bối cảnh và Đặt vấn đề:\n").bold = True
    p.add_run(
        "Thị trường laptop hiện nay vô cùng đa dạng với hàng trăm mẫu mã, linh kiện và mức giá biến động từ phân khúc bình dân (dưới 10 triệu đồng) "
        "đến phân khúc máy trạm đồ họa chuyên nghiệp và gaming cao cấp (trên 60 triệu đồng). Người tiêu dùng, đặc biệt là sinh viên và người đi làm, "
        "thường gặp khó khăn trong việc định giá một cấu hình phần cứng: 'Liệu mức giá niêm yết có tương xứng với hiệu năng thực tế hay không?'. "
        "Phần 4 của dự án LapInsight giải quyết trọn vẹn bài toán này bằng cách ứng dụng Học máy có giám sát (Supervised Regression) "
        "để tự động hóa quá trình ước tính giá bán laptop dựa trên thông số kỹ thuật thực tế, kết hợp bộ đề xuất 5 sản phẩm tương đồng."
    )

    p = doc.add_paragraph()
    p.add_run("1.2. Danh mục 9 thuộc tính đầu vào (Features) & Biến mục tiêu (Target):\n").bold = True
    p.add_run(
        "Mô hình sử dụng 9 biến độc lập đại diện toàn diện cho sức mạnh phần cứng, tính cơ động và trải nghiệm hiển thị của laptop:"
    )

    # Bảng 1: Danh mục thuộc tính
    table_feat = doc.add_table(rows=10, cols=4)
    table_feat.alignment = WD_TABLE_ALIGNMENT.CENTER
    feat_headers = ["STT", "Tên thuộc tính (Field)", "Kiểu dữ liệu & Đơn vị", "Ý nghĩa & Chuẩn đo lường"]
    for i, h in enumerate(feat_headers):
        cell = table_feat.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, HEX_HEADER_BG)
        set_cell_margins(cell)

    feat_data = [
        ("1", "cpu_score", "Số nguyên (Points)", "Điểm hiệu năng PassMark CPU Mark tổng thể đa nhân (PassMark 2026)."),
        ("2", "gpu_score", "Số nguyên (Points)", "Điểm đồ họa 3D PassMark G3D Mark (NVIDIA GeForce, Intel Arc, AMD)."),
        ("3", "ram", "Số nguyên (GB)", "Dung lượng bộ nhớ truy xuất ngẫu nhiên RAM (8, 16, 24, 32, 64 GB)."),
        ("4", "storage", "Số nguyên (GB)", "Dung lượng ổ lưu trữ thể rắn SSD NVMe (256, 512, 1024, 2048 GB)."),
        ("5", "screen_size", "Số thực (Inches)", "Kích thước đường chéo màn hình hiển thị (13.3, 14.0, 15.6, 16.0, 17.3)."),
        ("6", "refresh_rate", "Số nguyên (Hz)", "Tần số quét làm mới khung hình của màn hình (60, 90, 120, 144, 165, 240 Hz)."),
        ("7", "weight", "Số thực (kg)", "Trọng lượng vật lý của laptop theo công bố nhà sản xuất (0.96 kg - 2.8 kg)."),
        ("8", "battery", "Số thực (Wh)", "Dung lượng pin năng lượng tính theo Watt-giờ (Watt-hour: 38 Wh - 99.9 Wh)."),
        ("9", "rating", "Số thực (Thang 5.0)", "Điểm đánh giá chất lượng hoàn thiện từ người dùng thực tế tại Việt Nam.")
    ]
    for row_idx, data in enumerate(feat_data, start=1):
        bg = HEX_ALT_ROW if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate(data):
            cell = table_feat.cell(row_idx, col_idx)
            cell.text = val
            set_cell_background(cell, bg)
            set_cell_margins(cell)
            if col_idx in [0, 2]:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph()
    p.add_run("1.3. Ngăn xếp Công nghệ Học máy (Machine Learning Tech Stack):\n").bold = True
    p.add_run(
        "• Thư viện Học máy cốt lõi: Scikit-Learn 1.9+ (LinearRegression, RandomForestRegressor, StandardScaler, Pipeline, train_test_split).\n"
        "• Thư viện Đóng gói Model: Joblib 1.6+ (lưu trữ và tải tuần tự đối tượng Model Payload nhị phân .pkl).\n"
        "• Thư viện Tính toán khoa học: NumPy 2.5+ và Pandas 3.0+ (xử lý vector, ma trận khoảng cách và chuẩn hóa Z-score).\n"
        "• Web Framework: Flask 3.1+ (kết nối trực tiếp Model với Web Controller và REST API)."
    )

    # ==================== CHƯƠNG 2 ====================
    doc.add_heading("CHƯƠNG 2: TIỀN XỬ LÝ & THIẾT KẾ PIPELINE HUẤN LUYỆN", level=1)
    
    p = doc.add_paragraph()
    p.add_run("2.1. Phân chia tập dữ liệu Train / Test (80% / 20%):\n").bold = True
    p.add_run(
        "Toàn bộ 225 mẫu laptop thực tế sau khi qua quy trình làm sạch (Data Cleaning) được đưa vào mô hình. "
        "Áp dụng hàm train_test_split với tỷ lệ test_size=0.2 (20%) và cố định random_state=42 để đảm bảo kết quả thực nghiệm hoàn toàn có thể tái lập:\n"
        "• Tập huấn luyện (Train set): 180 mẫu (80%) – dùng để khớp các tham số mô hình và huấn luyện các cây quyết định.\n"
        "• Tập kiểm thử (Test set): 45 mẫu (20%) – tập độc lập hoàn toàn không xuất hiện trong quá trình train, dùng đánh giá độ sai lệch khách quan."
    )

    p = doc.add_paragraph()
    p.add_run("2.2. Kiến trúc Pipeline Hồi quy Tuyến tính (Linear Regression with StandardScaler):\n").bold = True
    p.add_run(
        "Do các đặc trưng có khoảng giá trị rất chênh lệch (ví dụ cpu_score từ 3,000 đến 35,000, trong khi weight chỉ từ 1.0 đến 2.5 kg), "
        "nếu không chuẩn hóa, các thuộc tính có giá trị tuyệt đối lớn sẽ lấn át hoàn toàn gradient của các thuộc tính nhỏ. "
        "Do đó, mô hình Hồi quy Tuyến tính được đóng gói trong một Pipeline gồm 2 bước:\n"
        "1. Bước 1 ('scaler'): StandardScaler() thực hiện chuẩn hóa z = (x - u) / s đưa mọi thuộc tính về phân phối chuẩn có kỳ vọng 0 và phương sai 1.\n"
        "2. Bước 2 ('model'): LinearRegression() tối thiểu hóa tổng bình phương sai số (Ordinary Least Squares)."
    )

    p = doc.add_paragraph()
    p.add_run("2.3. Cấu hình Mô hình Rừng Ngẫu nhiên (Random Forest Regressor):\n").bold = True
    p.add_run(
        "Mô hình Random Forest Regressor thuộc nhóm thuật toán Ensemble Learning (Ensemble Averaging) kết hợp 100 cây quyết định (n_estimators=100). "
        "Mỗi cây được xây dựng trên một tập con lấy mẫu ngẫu nhiên có hoàn lại (Bootstrap Sampling). Tại mỗi điểm chia nút, một tập con ngẫu nhiên "
        "các thuộc tính được lựa chọn để giảm phương sai và chống hiện tượng quá khớp (Overfitting). "
        "Random Forest có khả năng nắm bắt xuất sắc các mối quan hệ phi tuyến tính phức tạp giữa cấu hình phần cứng và giá bán."
    )

    # ==================== CHƯƠNG 3 ====================
    doc.add_heading("CHƯƠNG 3: ĐÁNH GIÁ, SO SÁNH HIỆU NĂNG & ĐÓNG GÓI", level=1)

    p = doc.add_paragraph()
    p.add_run("3.1. Các thang đo đánh giá chất lượng mô hình hồi quy:\n").bold = True
    p.add_run(
        "• MAE (Mean Absolute Error): Độ lệch tuyệt đối trung bình giữa giá dự đoán và giá niêm yết thực tế (tính theo VNĐ).\n"
        "• RMSE (Root Mean Squared Error): Căn bậc hai của sai số bình phương trung bình, giúp đo lường mức độ ảnh hưởng của các lỗi dự đoán lớn.\n"
        "• R² Score (Coefficient of Determination): Đo lường tỷ lệ phương sai của giá bán laptop được giải thích bởi cấu hình phần cứng."
    )

    # Bảng 2: Kết quả thực nghiệm
    table_res = doc.add_table(rows=3, cols=5)
    table_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    res_headers = ["Mô hình Học máy", "Đặc trưng Tiền xử lý", "MAE (VNĐ)", "RMSE (VNĐ)", "R² Score"]
    for i, h in enumerate(res_headers):
        cell = table_res.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, HEX_HEADER_BG)
        set_cell_margins(cell)

    res_data = [
        ("Linear Regression", "StandardScaler() Pipeline", "6,060,150 VNĐ", "7,791,430 VNĐ", "0.8098 (80.98%)"),
        ("Random Forest Regressor (100 Trees)", "Không cần scale (Tree-based)", "4,106,067 VNĐ", "6,133,598 VNĐ", "0.8821 (88.21%)")
    ]
    for row_idx, data in enumerate(res_data, start=1):
        bg = HEX_PRIMARY_BG if row_idx == 2 else "FFFFFF"
        for col_idx, val in enumerate(data):
            cell = table_res.cell(row_idx, col_idx)
            cell.text = val
            set_cell_background(cell, bg)
            set_cell_margins(cell)
            if col_idx in [2, 3, 4]:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                if row_idx == 2:
                    cell.paragraphs[0].runs[0].font.bold = True
                    cell.paragraphs[0].runs[0].font.color.rgb = COLOR_SUCCESS

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph()
    p.add_run("3.2. Phân tích kết quả & Lựa chọn mô hình thành phẩm:\n").bold = True
    p.add_run(
        "Kết quả đánh giá trên 45 mẫu Test độc lập cho thấy:\n"
        "• Random Forest Regressor vượt trội toàn diện so với Linear Regression: Sai số trung bình MAE giảm mạnh từ 6.06 triệu xuống còn 4.10 triệu VNĐ "
        "(cải thiện hơn 32.2%), đồng thời hệ số giải thích phương sai R² tăng từ 80.98% lên 88.21%.\n"
        "• Hệ thống thiết kế cơ chế tự động hóa: Tự động so sánh R² của cả hai thuật toán và lưu trữ mô hình có R² cao nhất vào file nhị phân models/laptop_price_model.pkl.\n"
        "• Cấu trúc Model Payload được đóng gói bằng Joblib gồm: model pipeline, model_name, danh sách features, chỉ số đánh giá của cả hai mô hình (MAE, RMSE, R²), kích thước tập train và test."
    )

    # ==================== CHƯƠNG 4 ====================
    doc.add_heading("CHƯƠNG 4: THUẬT TOÁN GỢI Ý TOP 5 LAPTOP TƯƠNG ĐỒNG", level=1)
    
    p = doc.add_paragraph()
    p.add_run("4.1. Bài toán Đề xuất Sản phẩm theo Tầm giá & Cấu hình:\n").bold = True
    p.add_run(
        "Một hệ thống định giá thông minh không thể chỉ trả về một con số giá đơn độc. Để tối ưu giá trị cho người dùng, hệ thống tích hợp hàm "
        "recommend_similar_laptops() tự động quét toàn bộ 225 laptop thực tế để tìm ra 5 mẫu máy có giá xấp xỉ mức giá ước tính "
        "(chênh lệch trong khoảng ±1 đến 2 triệu đồng) và có sự tương đồng cao nhất về phần cứng."
    )

    p = doc.add_paragraph()
    p.add_run("4.2. Trọng số hóa linh kiện phần cứng (Weighted Normalized Distance):\n").bold = True
    p.add_run(
        "Không phải linh kiện nào cũng đóng vai trò quyết định tương đương nhau khi so sánh laptop. CPU và GPU là hai bộ não chính định hình hiệu năng, "
        "do đó được gán trọng số cao nhất. Bảng trọng số thành phần cấu hình:"
    )

    # Bảng 3: Trọng số cấu hình
    table_w = doc.add_table(rows=9, cols=3)
    table_w.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_headers = ["Linh kiện / Đặc trưng", "Trọng số (Weight)", "Mức độ ưu tiên & Giải thích"]
    for i, h in enumerate(w_headers):
        cell = table_w.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, HEX_HEADER_BG)
        set_cell_margins(cell)

    w_data = [
        ("cpu_score (Điểm CPU)", "2.5", "Rất cao – Quyết định sức mạnh tính toán tổng thể."),
        ("gpu_score (Điểm GPU)", "2.5", "Rất cao – Quyết định khả năng xử lý đồ họa, render & game."),
        ("ram (Dung lượng RAM)", "2.0", "Cao – Khả năng chạy đa nhiệm và mở nhiều tác vụ."),
        ("storage (Dung lượng SSD)", "1.5", "Trung bình cao – Không gian lưu trữ dữ liệu."),
        ("screen_size (Màn hình)", "1.0", "Tiêu chuẩn – Yếu tố kích thước hiển thị."),
        ("refresh_rate (Tần số quét)", "1.0", "Tiêu chuẩn – Độ mượt mà khi chơi game hoặc xem nội dung."),
        ("weight (Trọng lượng)", "1.0", "Tiêu chuẩn – Tính cơ động khi di chuyển."),
        ("battery (Dung lượng Pin)", "1.0", "Tiêu chuẩn – Thời lượng sử dụng độc lập nguồn điện.")
    ]
    for row_idx, data in enumerate(w_data, start=1):
        bg = HEX_ALT_ROW if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate(data):
            cell = table_w.cell(row_idx, col_idx)
            cell.text = val
            set_cell_background(cell, bg)
            set_cell_margins(cell)
            if col_idx == 1:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph()
    p.add_run("4.3. Công thức Tính Tỷ lệ Phần trăm Tương đồng (% Similarity):\n").bold = True
    p.add_run(
        "Khoảng cách chuẩn hóa có trọng số (config_dist) được quy đổi sang tỷ lệ phần trăm tương đồng tiệm cận tự nhiên bằng hàm hàm mũ giảm dần:\n"
        "    Similarity (%) = Clip(100.0 * exp(-0.25 * config_dist), 35.0, 99.5)\n"
        "Công thức này đảm bảo tỷ lệ tương đồng phản ánh chính xác trực giác của người dùng: các máy cấu hình gần giống nhau đạt 90-99%, "
        "trong khi các máy chênh lệch cấu hình nhiều sẽ giảm dần về ngưỡng sàn 35%."
    )

    # ==================== CHƯƠNG 5 ====================
    doc.add_heading("CHƯƠNG 5: THIẾT KẾ GIAO DIỆN & REST API ENDPOINTS", level=1)
    
    p = doc.add_paragraph()
    p.add_run("5.1. Khung Form Trải nghiệm 2 Lớp (predict.html):\n").bold = True
    p.add_run(
        "• Lớp 1 (Preset 1-Click theo Ngành học): Người dùng chỉ cần nhấp vào 1 trong 3 ngành học phổ biến (Kinh tế / Văn phòng, CNTT / Lập trình, "
        "Đồ họa / Gaming), hệ thống JavaScript sẽ tự động điền các thông số kỹ thuật chuẩn, tạo hiệu ứng cuộn mượt và highlight viền xanh tức thì.\n"
        "• Lớp 2 (Form Tinh chỉnh 9 Thông số): Người dùng có thể tự do điều chỉnh từng thông số kỹ thuật với đầy đủ nhãn giải thích và gợi ý giá trị tiêu chuẩn.\n"
        "• Thẻ Kết quả Định giá: Hiển thị mức giá ước tính định dạng tiền tệ VNĐ nổi bật, đi kèm thẻ so sánh trực quan (Tiết kiệm hơn / Cao hơn bao nhiêu tiền).\n"
        "• Bảng Top 5 Laptop Đề xuất: Mỗi mẫu laptop hiển thị đầy đủ thương hiệu, tên model, giá bán, thanh tiến trình % tương đồng cấu hình và nút xem trực tiếp trong kho máy."
    )

    p = doc.add_paragraph()
    p.add_run("5.2. Danh mục URL Endpoints & REST API:\n").bold = True

    # Bảng 4: Endpoints
    table_ep = doc.add_table(rows=4, cols=4)
    table_ep.alignment = WD_TABLE_ALIGNMENT.CENTER
    ep_headers = ["Phương thức (Method)", "URL Endpoint", "Định dạng Dữ liệu", "Chức năng & Tác dụng"]
    for i, h in enumerate(ep_headers):
        cell = table_ep.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, HEX_HEADER_BG)
        set_cell_margins(cell)

    ep_data = [
        ("GET", "/predict", "HTML Web Page", "Hiển thị trang định giá, 3 preset mẫu và các chỉ số MAE/RMSE/R² của mô hình."),
        ("POST", "/predict", "HTML Form Body", "Xác thực dữ liệu đầu vào (Validation), tính toán giá ước tính và hiển thị Top 5 gợi ý."),
        ("POST", "/api/predict", "JSON Request / Response", "REST API dự đoán giá cho client bên ngoài, trả về giá bán và danh sách đề xuất dạng JSON.")
    ]
    for row_idx, data in enumerate(ep_data, start=1):
        bg = HEX_ALT_ROW if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate(data):
            cell = table_ep.cell(row_idx, col_idx)
            cell.text = val
            set_cell_background(cell, bg)
            set_cell_margins(cell)
            if col_idx in [0, 2]:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ==================== CHƯƠNG 6 ====================
    doc.add_heading("CHƯƠNG 6: HƯỚNG DẪN KHỞI CHẠY & KIỂM THỬ THỰC TẾ", level=1)
    
    p = doc.add_paragraph()
    p.add_run("6.1. Hướng dẫn Khởi chạy Từng bước:\n").bold = True
    p.add_run(
        "Bước 1: Mở Terminal tại thư mục dự án Laptops:\n"
        "    cd c:\\Users\\chaut\\Documents\\Laptops\n\n"
        "Bước 2: Kích hoạt môi trường ảo Python (.venv):\n"
        "    .\\.venv\\Scripts\\Activate.ps1\n\n"
        "Bước 3: (Tùy chọn) Chạy kiểm thử huấn luyện và đánh giá độc lập module Học máy:\n"
        "    python -m src.price_prediction\n\n"
        "Bước 4: Khởi động máy chủ Web Flask:\n"
        "    python app.py\n\n"
        "Bước 5: Truy cập trình duyệt web tại địa chỉ:\n"
        "    http://127.0.0.1:5000/predict"
    )

    p = doc.add_paragraph()
    p.add_run("6.2. Kết quả Kiểm thử Tự động (Automated Test Report):\n").bold = True
    p.add_run(
        "Toàn bộ các bài kiểm tra tự động (Unit Test & Integration Test) đã được thực thi và đạt tỷ lệ thành công 100%:\n"
        "• Test 1 (GET /): Mã trạng thái HTTP 200 OK, hiển thị đầy đủ số liệu 225 mẫu laptop và banner Phần 4.\n"
        "• Test 2 (GET /predict): Mã trạng thái HTTP 200 OK, nạp đúng model payload và hiển thị form định giá.\n"
        "• Test 3 (POST /predict): Mã trạng thái HTTP 200 OK, form validation hoạt động chuẩn xác, hiển thị kết quả giá ước tính và Top 5 laptop tương đồng.\n"
        "• Test 4 (POST /api/predict): Mã trạng thái HTTP 200 OK, phản hồi JSON đầy đủ trường status: 'success', predicted_price_formatted và recommendations."
    )

    # ==================== CHƯƠNG 7 ====================
    doc.add_heading("CHƯƠNG 7: KẾT LUẬN & HƯỚNG PHÁT TRIỂN TIẾP THEO", level=1)
    p = doc.add_paragraph()
    p.add_run(
        "Phần 4: Xây dựng Mô hình Học máy Dự đoán Giá Laptop đã được hoàn thành xuất sắc và tích hợp toàn diện vào dự án Laptops. "
        "Mô hình đạt độ chính xác cao (R² đạt 88.21%), thuật toán gợi ý sản phẩm thông minh và giao diện người dùng thân thiện, hiện đại. "
        "Hệ thống không chỉ đáp ứng trọn vẹn các yêu cầu học thuật khắt khe của môn học Khoa học Dữ liệu mà còn mang tính ứng dụng thực tiễn cao, "
        "trở thành một công cụ tư vấn mua sắm công nghệ đáng tin cậy cho sinh viên và cộng đồng người dùng."
    )

    out_path = r"c:\Users\chaut\Documents\Laptops\Bao_Cao_Phan_4_Du_Doan_Gia_Laptop.docx"
    doc.save(out_path)
    print(f"Đã tạo thành công báo cáo Word: {out_path}")

if __name__ == '__main__':
    create_report()
