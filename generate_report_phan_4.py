import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn

# Thiết lập UTF-8 cho console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

NS = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'

def set_cell_background(cell, fill_hex):
    """Đặt màu nền cho ô trong bảng."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    """Thiết lập padding cho ô trong bảng."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_equation_box(doc, math_xml, eq_number, title, variables=None):
    """
    Tạo khối hiển thị công thức toán học chuyên nghiệp (Callout Equation Box):
    - Khung viền trái màu xanh đậm nổi bật
    - Nền màu lam nhạt trang trọng
    - Công thức toán học OMML chuẩn Microsoft Word (Insert Equation)
    - Danh mục giải thích chi tiết từng biến số toán học.
    """
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    
    # Nền lam nhạt cao cấp
    set_cell_background(cell, "F4F8FD")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Thiết lập đường viền: Viền trái dày 3pt màu xanh #0D6EFD, các viền khác mờ
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '24')  # 3pt
    left.set(qn('w:space'), '0')
    left.set(qn('w:color'), '0D6EFD')
    tcBorders.append(left)
    
    for b_name in ['top', 'bottom', 'right']:
        b = OxmlElement(f'w:{b_name}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), '4')
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), 'DEE2E6')
        tcBorders.append(b)
        
    tcPr.append(tcBorders)
    
    # 1. Dòng tiêu đề công thức
    p_title = cell.paragraphs[0]
    p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_title.paragraph_format.space_after = Pt(4)
    run_t = p_title.add_run(f"✦ {eq_number}: {title}")
    run_t.bold = True
    run_t.font.size = Pt(11)
    run_t.font.color.rgb = RGBColor(13, 110, 253)
    
    # 2. Đoạn công thức toán học Word OMML (Căn giữa trang)
    p_math = cell.add_paragraph()
    p_math.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_math.paragraph_format.space_before = Pt(8)
    p_math.paragraph_format.space_after = Pt(8)
    omml_wrapper = f'<m:oMathPara {NS}><m:oMath>{math_xml}</m:oMath></m:oMathPara>'
    p_math._p.append(parse_xml(omml_wrapper))
    
    # 3. Diễn giải chi tiết từng biến số toán học
    if variables:
        p_vars = cell.add_paragraph()
        p_vars.paragraph_format.space_before = Pt(4)
        p_vars.paragraph_format.space_after = Pt(0)
        p_vars.paragraph_format.line_spacing = 1.2
        r_head = p_vars.add_run("Trong đó:\n")
        r_head.bold = True
        r_head.font.size = Pt(9.5)
        r_head.font.italic = True
        for sym, desc in variables:
            r_s = p_vars.add_run(f"  • {sym}: ")
            r_s.bold = True
            r_s.font.size = Pt(9.5)
            r_d = p_vars.add_run(f"{desc}\n")
            r_d.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def create_report():
    doc = docx.Document()
    
    # Cấu hình lề trang A4 chuẩn quốc tế
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
    HEX_HEADER_BG = "0D6EFD"
    HEX_ALT_ROW = "F8F9FA"
    HEX_PRIMARY_BG = "E7F1FF"

    # ==================== TRANG BÌA TIÊU ĐỀ ====================
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(8)
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
    p_meta.paragraph_format.space_after = Pt(16)
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
        "Thị trường máy tính xách tay hiện nay vô cùng phong phú và biến động không ngừng, với hàng trăm dòng sản phẩm thuộc nhiều phân khúc "
        "từ học tập cơ bản (dưới 10 triệu VNĐ) cho đến dòng đồ họa cao cấp và gaming chuyên nghiệp (trên 60 triệu VNĐ). Người tiêu dùng thường xuyên "
        "đối mặt với câu hỏi khó: 'Với cấu hình phần cứng này thì mức giá nào là hợp lý và đúng với giá trị thực tế?'. "
        "Phần 4 của dự án LapInsight giải quyết bài toán cốt lõi này bằng kỹ thuật Học máy có giám sát (Supervised Machine Learning Regression), "
        "cho phép tự động lượng hóa mối tương quan đa biến phức tạp giữa 9 thông số kỹ thuật phần cứng và giá bán thị trường."
    )

    p = doc.add_paragraph()
    p.add_run("1.2. Danh mục 9 thuộc tính đầu vào (Features) & Biến mục tiêu (Target):\n").bold = True
    p.add_run(
        "Không gian đặc trưng đầu vào X bao gồm 9 biến số đại diện cho hiệu năng, dung lượng lưu trữ, màn hình, trọng lượng và pin:"
    )

    # Bảng 1: Danh mục thuộc tính
    table_feat = doc.add_table(rows=10, cols=4)
    table_feat.alignment = WD_TABLE_ALIGNMENT.CENTER
    feat_headers = ["STT", "Tên thuộc tính (Field)", "Kiểu dữ liệu & Đơn vị", "Ý nghĩa & Tiêu chuẩn đo lường"]
    for i, h in enumerate(feat_headers):
        cell = table_feat.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, HEX_HEADER_BG)
        set_cell_margins(cell)

    feat_data = [
        ("1", "cpu_score", "Số nguyên (Points)", "Điểm hiệu năng PassMark CPU Mark tổng hợp (PassMark 2026)."),
        ("2", "gpu_score", "Số nguyên (Points)", "Điểm đồ họa PassMark G3D Mark (NVIDIA RTX, Intel Arc/Iris, AMD Radeon)."),
        ("3", "ram", "Số nguyên (GB)", "Dung lượng bộ nhớ truy xuất ngẫu nhiên RAM (8, 16, 24, 32, 64 GB)."),
        ("4", "storage", "Số nguyên (GB)", "Dung lượng ổ cứng lưu trữ thể rắn SSD NVMe (256, 512, 1024, 2048 GB)."),
        ("5", "screen_size", "Số thực (Inches)", "Kích thước đường chéo màn hình hiển thị (13.3, 14.0, 15.6, 16.0, 17.3)."),
        ("6", "refresh_rate", "Số nguyên (Hz)", "Tần số quét làm tươi màn hình (60, 90, 120, 144, 165, 240 Hz)."),
        ("7", "weight", "Số thực (kg)", "Khối lượng vật lý của máy theo công bố nhà sản xuất (0.96 kg - 2.8 kg)."),
        ("8", "battery", "Số thực (Wh)", "Dung lượng pin tính theo Watt-giờ (Watt-hour: 38 Wh - 99.9 Wh)."),
        ("9", "rating", "Số thực (Thang 5.0)", "Điểm đánh giá độ tin cậy từ người dùng thực tế tại hệ thống bán lẻ.")
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
        "• Thư viện Học máy: Scikit-Learn 1.9+ (LinearRegression, RandomForestRegressor, StandardScaler, Pipeline, train_test_split).\n"
        "• Đóng gói Mô hình: Joblib 1.6+ (lưu trữ và phục hồi mô hình nhị phân .pkl tối ưu tốc độ).\n"
        "• Tính toán Ma trận & Dữ liệu: NumPy 2.5+ và Pandas 3.0+ (xử lý vector hóa và khoảng cách Euclidean có trọng số).\n"
        "• Khung ứng dụng Web: Flask 3.1+ (kết nối trực quan hóa và API RESTful)."
    )

    # ==================== CHƯƠNG 2 ====================
    doc.add_heading("CHƯƠNG 2: TIỀN XỬ LÝ & THIẾT KẾ PIPELINE HUẤN LUYỆN", level=1)
    
    p = doc.add_paragraph()
    p.add_run("2.1. Phân chia tập dữ liệu Train / Test (80% / 20%):\n").bold = True
    p.add_run(
        "Toàn bộ 225 mẫu laptop thực tế được phân tách ngẫu nhiên thành 2 tập độc lập bằng phương thức train_test_split "
        "với random_state=42 để đảm bảo tính tái lập hoàn toàn:\n"
        "• Tập huấn luyện (Train Set): 180 mẫu (80%) – dùng để khớp tham số trọng số và cấu trúc cây quyết định.\n"
        "• Tập kiểm thử (Test Set): 45 mẫu (20%) – tập độc lập hoàn toàn dùng để đo lường độ sai lệch khách quan."
    )

    p = doc.add_paragraph()
    p.add_run("2.2. Chuẩn hóa Đặc trưng bằng StandardScaler:\n").bold = True
    p.add_run(
        "Do 9 đặc trưng đầu vào có đơn vị và thang đo chênh lệch rất lớn (ví dụ cpu_score từ 3,000 đến 35,000 trong khi weight chỉ từ 1.0 đến 2.5 kg), "
        "mô hình Hồi quy Tuyến tính bắt buộc phải được tiền xử lý bằng StandardScaler để đưa mọi thuộc tính về cùng một phân phối chuẩn."
    )

    # CÔNG THỨC 1: Z-SCORE
    math_zscore = """
    <m:r><m:t>z</m:t></m:r>
    <m:r><m:t>=</m:t></m:r>
    <m:f>
      <m:num>
        <m:r><m:t>x - μ</m:t></m:r>
      </m:num>
      <m:den>
        <m:r><m:t>σ</m:t></m:r>
      </m:den>
    </m:f>
    <m:r><m:t>    với    μ = </m:t></m:r>
    <m:f>
      <m:num><m:r><m:t>1</m:t></m:r></m:num>
      <m:den><m:r><m:t>N</m:t></m:r></m:den>
    </m:f>
    <m:nary>
      <m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>
      <m:sub><m:r><m:t>i=1</m:t></m:r></m:sub>
      <m:sup><m:r><m:t>N</m:t></m:r></m:sup>
      <m:e><m:sSub><m:e><m:r><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub></m:e>
    </m:nary>
    <m:r><m:t>,    σ = </m:t></m:r>
    <m:rad>
      <m:radPr><m:degHide m:val="1"/></m:radPr>
      <m:e>
        <m:f>
          <m:num><m:r><m:t>1</m:t></m:r></m:num>
          <m:den><m:r><m:t>N</m:t></m:r></m:den>
        </m:f>
        <m:nary>
          <m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>
          <m:sub><m:r><m:t>i=1</m:t></m:r></m:sub>
          <m:sup><m:r><m:t>N</m:t></m:r></m:sup>
          <m:e>
            <m:sSup>
              <m:e>
                <m:d>
                  <m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>
                  <m:e>
                    <m:sSub><m:e><m:r><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
                    <m:r><m:t>-</m:t></m:r>
                    <m:r><m:t>μ</m:t></m:r>
                  </m:e>
                </m:d>
              </m:e>
              <m:sup><m:r><m:t>2</m:t></m:r></m:sup>
            </m:sSup>
          </m:e>
        </m:nary>
      </m:e>
    </m:rad>
    """
    add_equation_box(doc, math_zscore, "Công thức 1", "Chuẩn hóa Z-Score trong StandardScaler", [
        ("z", "Giá trị thuộc tính sau khi chuẩn hóa (có kỳ vọng E[z] = 0 và phương sai Var(z) = 1)"),
        ("x", "Giá trị thuộc tính gốc ban đầu của mẫu laptop (điểm CPU, RAM, pin...)"),
        ("μ (Mu)", "Giá trị trung bình số học (Mean) của đặc trưng tương ứng trên 180 mẫu tập huấn luyện"),
        ("σ (Sigma)", "Độ lệch chuẩn (Standard Deviation) đo mức độ phân tán của đặc trưng trên tập huấn luyện"),
        ("N", "Số lượng mẫu trong tập huấn luyện (N = 180 mẫu)")
    ])

    p = doc.add_paragraph()
    p.add_run("2.3. Phương trình Hồi quy Tuyến tính Đa biến (Multivariate Linear Regression):\n").bold = True
    p.add_run(
        "Mô hình Hồi quy Tuyến tính dự đoán giá bán laptop bằng tổ hợp tuyến tính có trọng số của các đặc trưng chuẩn hóa:"
    )

    # CÔNG THỨC 2: LINEAR REGRESSION
    math_lr = """
    <m:sSup><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sup><m:r><m:t>^</m:t></m:r></m:sup></m:sSup>
    <m:r><m:t>=</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>0</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>+</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub>
    <m:sSub><m:e><m:r><m:t>z</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>+</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>2</m:t></m:r></m:sub></m:sSub>
    <m:sSub><m:e><m:r><m:t>z</m:t></m:r></m:e><m:sub><m:r><m:t>2</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>+</m:t></m:r>
    <m:r><m:t>⋯</m:t></m:r>
    <m:r><m:t>+</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>p</m:t></m:r></m:sub></m:sSub>
    <m:sSub><m:e><m:r><m:t>z</m:t></m:r></m:e><m:sub><m:r><m:t>p</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>=</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>0</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>+</m:t></m:r>
    <m:nary>
      <m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>
      <m:sub><m:r><m:t>j=1</m:t></m:r></m:sub>
      <m:sup><m:r><m:t>p</m:t></m:r></m:sup>
      <m:e>
        <m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub>
        <m:sSub><m:e><m:r><m:t>z</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub>
      </m:e>
    </m:nary>
    <m:r><m:t>=</m:t></m:r>
    <m:sSup><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sup><m:r><m:t>T</m:t></m:r></m:sup></m:sSup>
    <m:r><m:t>z</m:t></m:r>
    <m:r><m:t>+</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>0</m:t></m:r></m:sub></m:sSub>
    """
    add_equation_box(doc, math_lr, "Công thức 2", "Phương trình Hồi quy Tuyến tính Đa biến", [
        ("ŷ (y-hat)", "Mức giá laptop dự đoán ước tính (đơn vị: VNĐ)"),
        ("w₀", "Hệ số tự do (Bias / Intercept)"),
        ("wⱼ", "Hệ số góc trọng số của đặc trưng thứ j (với p = 9 đặc trưng)"),
        ("zⱼ", "Giá trị của đặc trưng thứ j sau khi chuẩn hóa Z-score"),
        ("w^T z", "Tích vô hướng giữa vector trọng số w và vector đặc trưng z")
    ])

    p = doc.add_paragraph()
    p.add_run("2.4. Hàm Mất mát Bình phương Tối thiểu OLS (Ordinary Least Squares):\n").bold = True
    p.add_run(
        "Mô hình tìm kiếm bộ trọng số tối ưu (w, w₀) bằng cách cực tiểu hóa hàm tổn thất bình phương trung bình:"
    )

    # CÔNG THỨC 3: OLS LOSS
    math_ols = """
    <m:r><m:t>J(w,</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>0</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>)=</m:t></m:r>
    <m:f>
      <m:num><m:r><m:t>1</m:t></m:r></m:num>
      <m:den><m:r><m:t>2N</m:t></m:r></m:den>
    </m:f>
    <m:nary>
      <m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>
      <m:sub><m:r><m:t>i=1</m:t></m:r></m:sub>
      <m:sup><m:r><m:t>N</m:t></m:r></m:sup>
      <m:e>
        <m:sSup>
          <m:e>
            <m:d>
              <m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>
              <m:e>
                <m:sSup>
                  <m:e><m:r><m:t>y</m:t></m:r></m:e>
                  <m:sup><m:r><m:t>^</m:t></m:r></m:sup>
                </m:sSup>
                <m:sSub><m:e></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
                <m:r><m:t>-</m:t></m:r>
                <m:sSub><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
              </m:e>
            </m:d>
          </m:e>
          <m:sup><m:r><m:t>2</m:t></m:r></m:sup>
        </m:sSup>
      </m:e>
    </m:nary>
    <m:r><m:t>=</m:t></m:r>
    <m:f>
      <m:num><m:r><m:t>1</m:t></m:r></m:num>
      <m:den><m:r><m:t>2N</m:t></m:r></m:den>
    </m:f>
    <m:nary>
      <m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>
      <m:sub><m:r><m:t>i=1</m:t></m:r></m:sub>
      <m:sup><m:r><m:t>N</m:t></m:r></m:sup>
      <m:e>
        <m:sSup>
          <m:e>
            <m:d>
              <m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>
              <m:e>
                <m:sSup><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sup><m:r><m:t>T</m:t></m:r></m:sup></m:sSup>
                <m:sSub><m:e><m:r><m:t>z</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
                <m:r><m:t>+</m:t></m:r>
                <m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>0</m:t></m:r></m:sub></m:sSub>
                <m:r><m:t>-</m:t></m:r>
                <m:sSub><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
              </m:e>
            </m:d>
          </m:e>
          <m:sup><m:r><m:t>2</m:t></m:r></m:sup>
        </m:sSup>
      </m:e>
    </m:nary>
    """
    add_equation_box(doc, math_ols, "Công thức 3", "Hàm Mất mát Bình phương Tối thiểu (OLS Loss Function)", [
        ("J(w, w₀)", "Giá trị hàm mất mát cần tối thiểu hóa"),
        ("yᵢ", "Giá bán thực tế của laptop thứ i trong tập dữ liệu"),
        ("ŷᵢ", "Giá dự đoán tương ứng do mô hình tuyến tính ước tính"),
        ("N", "Số lượng mẫu trong tập huấn luyện (N = 180)")
    ])

    p = doc.add_paragraph()
    p.add_run("2.5. Mô hình Rừng Ngẫu nhiên (Random Forest Regressor):\n").bold = True
    p.add_run(
        "Mô hình Random Forest kết hợp 100 cây quyết định độc lập (B = 100). Giá trị dự đoán cuối cùng là trung bình cộng "
        "dự đoán từ toàn bộ quần thể cây để giảm thiểu tối đa phương sai (Variance Reduction):"
    )

    # CÔNG THỨC 4: RANDOM FOREST
    math_rf = """
    <m:sSubSup>
      <m:e><m:r><m:t>y</m:t></m:r></m:e>
      <m:sub><m:r><m:t>RF</m:t></m:r></m:sub>
      <m:sup><m:r><m:t>^</m:t></m:r></m:sup>
    </m:sSubSup>
    <m:r><m:t>=</m:t></m:r>
    <m:f>
      <m:num><m:r><m:t>1</m:t></m:r></m:num>
      <m:den><m:r><m:t>B</m:t></m:r></m:den>
    </m:f>
    <m:nary>
      <m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>
      <m:sub><m:r><m:t>b=1</m:t></m:r></m:sub>
      <m:sup><m:r><m:t>B</m:t></m:r></m:sup>
      <m:e>
        <m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>b</m:t></m:r></m:sub></m:sSub>
        <m:d>
          <m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>
          <m:e><m:r><m:t>x</m:t></m:r></m:e>
        </m:d>
      </m:e>
    </m:nary>
    """
    add_equation_box(doc, math_rf, "Công thức 4", "Dự đoán Quần thể Rừng Ngẫu nhiên (Ensemble Averaging)", [
        ("ŷ_RF", "Giá dự đoán tổng hợp từ mô hình Random Forest"),
        ("B", "Tổng số cây quyết định trong mô hình (B = 100 cây, n_estimators=100)"),
        ("T_b(x)", "Giá dự đoán từ cây quyết định thứ b xây dựng trên tập mẫu con Bootstrap"),
        ("x", "Vector 9 thông số kỹ thuật gốc của laptop")
    ])

    # ==================== CHƯƠNG 3 ====================
    doc.add_heading("CHƯƠNG 3: ĐÁNH GIÁ, SO SÁNH HIỆU NĂNG & ĐÓNG GÓI", level=1)
    
    p = doc.add_paragraph()
    p.add_run("3.1. Các Thang đo Đánh giá Hiệu năng Mô hình Hồi quy:\n").bold = True
    p.add_run(
        "Để đánh giá toàn diện và khách quan, hệ thống thiết lập 3 tiêu chuẩn đo lường sai số chuẩn mực quốc tế:"
    )

    # CÔNG THỨC 5: MAE
    math_mae = """
    <m:r><m:t>MAE = </m:t></m:r>
    <m:f>
      <m:num><m:r><m:t>1</m:t></m:r></m:num>
      <m:den><m:r><m:t>n</m:t></m:r></m:den>
    </m:f>
    <m:nary>
      <m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>
      <m:sub><m:r><m:t>i=1</m:t></m:r></m:sub>
      <m:sup><m:r><m:t>n</m:t></m:r></m:sup>
      <m:e>
        <m:d>
          <m:dPr><m:begChr m:val="|"/><m:endChr m:val="|"/></m:dPr>
          <m:e>
            <m:sSub><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
            <m:r><m:t>-</m:t></m:r>
            <m:sSubSup>
              <m:e><m:r><m:t>y</m:t></m:r></m:e>
              <m:sub><m:r><m:t>i</m:t></m:r></m:sub>
              <m:sup><m:r><m:t>^</m:t></m:r></m:sup>
            </m:sSubSup>
          </m:e>
        </m:d>
      </m:e>
    </m:nary>
    """
    add_equation_box(doc, math_mae, "Công thức 5", "Sai số Tuyệt đối Trung bình (Mean Absolute Error - MAE)", [
        ("MAE", "Độ lệch tuyệt đối trung bình giữa giá dự đoán và giá niêm yết thực tế (đơn vị: VNĐ)"),
        ("n", "Số lượng mẫu trong tập kiểm thử (n = 45 mẫu Test)"),
        ("yᵢ", "Giá bán niêm yết thực tế của laptop thứ i"),
        ("ŷᵢ", "Giá ước tính do mô hình tính toán cho laptop thứ i")
    ])

    # CÔNG THỨC 6: RMSE
    math_rmse = """
    <m:r><m:t>RMSE = </m:t></m:r>
    <m:rad>
      <m:radPr><m:degHide m:val="1"/></m:radPr>
      <m:e>
        <m:f>
          <m:num><m:r><m:t>1</m:t></m:r></m:num>
          <m:den><m:r><m:t>n</m:t></m:r></m:den>
        </m:f>
        <m:nary>
          <m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>
          <m:sub><m:r><m:t>i=1</m:t></m:r></m:sub>
          <m:sup><m:r><m:t>n</m:t></m:r></m:sup>
          <m:e>
            <m:sSup>
              <m:e>
                <m:d>
                  <m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>
                  <m:e>
                    <m:sSub><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
                    <m:r><m:t>-</m:t></m:r>
                    <m:sSubSup>
                      <m:e><m:r><m:t>y</m:t></m:r></m:e>
                      <m:sub><m:r><m:t>i</m:t></m:r></m:sub>
                      <m:sup><m:r><m:t>^</m:t></m:r></m:sup>
                    </m:sSubSup>
                  </m:e>
                </m:d>
              </m:e>
              <m:sup><m:r><m:t>2</m:t></m:r></m:sup>
            </m:sSup>
          </m:e>
        </m:nary>
      </m:e>
    </m:rad>
    """
    add_equation_box(doc, math_rmse, "Công thức 6", "Căn bậc hai Sai số Bình phương Trung bình (RMSE)", [
        ("RMSE", "Căn bậc hai của sai số bình phương trung bình (đơn vị: VNĐ)"),
        ("Đặc tính", "Phạt nặng hơn đối với các dự đoán có sai số lớn nhờ bước bình phương sai số trước khi lấy căn")
    ])

    # CÔNG THỨC 7: R2 SCORE
    math_r2 = """
    <m:sSup><m:e><m:r><m:t>R</m:t></m:r></m:e><m:sup><m:r><m:t>2</m:t></m:r></m:sup></m:sSup>
    <m:r><m:t> = 1 - </m:t></m:r>
    <m:f>
      <m:num>
        <m:sSub><m:e><m:r><m:t>SS</m:t></m:r></m:e><m:sub><m:r><m:t>res</m:t></m:r></m:sub></m:sSub>
      </m:num>
      <m:den>
        <m:sSub><m:e><m:r><m:t>SS</m:t></m:r></m:e><m:sub><m:r><m:t>tot</m:t></m:r></m:sub></m:sSub>
      </m:den>
    </m:f>
    <m:r><m:t> = 1 - </m:t></m:r>
    <m:f>
      <m:num>
        <m:nary>
          <m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>
          <m:sub><m:r><m:t>i=1</m:t></m:r></m:sub>
          <m:sup><m:r><m:t>n</m:t></m:r></m:sup>
          <m:e>
            <m:sSup>
              <m:e>
                <m:d>
                  <m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>
                  <m:e>
                    <m:sSub><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
                    <m:r><m:t>-</m:t></m:r>
                    <m:sSubSup>
                      <m:e><m:r><m:t>y</m:t></m:r></m:e>
                      <m:sub><m:r><m:t>i</m:t></m:r></m:sub>
                      <m:sup><m:r><m:t>^</m:t></m:r></m:sup>
                    </m:sSubSup>
                  </m:e>
                </m:d>
              </m:e>
              <m:sup><m:r><m:t>2</m:t></m:r></m:sup>
            </m:sSup>
          </m:e>
        </m:nary>
      </m:num>
      <m:den>
        <m:nary>
          <m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>
          <m:sub><m:r><m:t>i=1</m:t></m:r></m:sub>
          <m:sup><m:r><m:t>n</m:t></m:r></m:sup>
          <m:e>
            <m:sSup>
              <m:e>
                <m:d>
                  <m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>
                  <m:e>
                    <m:sSub><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>
                    <m:r><m:t>-</m:t></m:r>
                    <m:r><m:t>ȳ</m:t></m:r>
                  </m:e>
                </m:d>
              </m:e>
              <m:sup><m:r><m:t>2</m:t></m:r></m:sup>
            </m:sSup>
          </m:e>
        </m:nary>
      </m:den>
    </m:f>
    """
    add_equation_box(doc, math_r2, "Công thức 7", "Hệ số Xác định (Coefficient of Determination - R² Score)", [
        ("R²", "Tỷ lệ phương sai của giá bán laptop được mô hình giải thích (càng gần 1.0 thì mô hình càng chính xác)"),
        ("SS_res", "Tổng bình phương phần dư sai số (Residual Sum of Squares)"),
        ("SS_tot", "Tổng bình phương sai số toàn phần so với giá trị trung bình (Total Sum of Squares)"),
        ("ȳ (y-bar)", "Mức giá bán trung bình thực tế của toàn bộ 45 laptop trong tập kiểm thử")
    ])

    p = doc.add_paragraph()
    p.add_run("3.2. Bảng So sánh Hiệu năng Thực nghiệm trên Tập Test (45 mẫu):\n").bold = True

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
        ("Random Forest Regressor (100 Trees)", "Ensemble Learning (Không cần scale)", "4,106,067 VNĐ", "6,133,598 VNĐ", "0.8821 (88.21%)")
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
    p.add_run("3.3. Đánh giá Kết quả & Đóng gói Mô hình Thành phẩm:\n").bold = True
    p.add_run(
        "• Random Forest Regressor áp đảo toàn diện: Sai số trung bình MAE giảm mạnh từ 6.06 triệu xuống 4.10 triệu VNĐ "
        "(độ chính xác tăng thêm 32.2%), hệ số giải thích biến thiên R² đạt tới 88.21%.\n"
        "• Hệ thống tự động chọn mô hình có R² lớn nhất và đóng gói vào models/laptop_price_model.pkl bằng Joblib. "
        "File model nhị phân kích thước ~1.4 MB chứa trọn vẹn trọng số cây và siêu dữ liệu đánh giá, sẵn sàng phục vụ tức thì mà không cần train lại."
    )

    # ==================== CHƯƠNG 4 ====================
    doc.add_heading("CHƯƠNG 4: THUẬT TOÁN GỢI Ý TOP 5 LAPTOP TƯƠNG ĐỒNG", level=1)
    
    p = doc.add_paragraph()
    p.add_run("4.1. Bài toán Gợi ý Sản phẩm Tối ưu theo Tầm giá:\n").bold = True
    p.add_run(
        "Sau khi ước tính được giá, hệ thống thực hiện thuật toán tìm kiếm 5 laptop thực tế có cấu hình tương đương "
        "và mức giá chênh lệch trong khoảng ±1 đến 2 triệu đồng so với giá ước tính."
    )

    p = doc.add_paragraph()
    p.add_run("4.2. Khoảng cách Cấu hình Chuẩn hóa có Trọng số (Weighted Normalized Distance):\n").bold = True
    p.add_run(
        "Để so sánh hai cấu hình máy tính gồm nhiều thuộc tính có đơn vị đo khác nhau (Điểm PassMark, GB RAM, Inch màn hình...), "
        "mỗi đặc trưng được chuẩn hóa theo độ lệch chuẩn toàn thể (Z-score Scaling) và nhân với trọng số linh kiện tương ứng:"
    )

    # CÔNG THỨC 8: WEIGHTED DISTANCE
    math_dist = """
    <m:sSub><m:e><m:r><m:t>d</m:t></m:r></m:e><m:sub><m:r><m:t>config</m:t></m:r></m:sub></m:sSub>
    <m:d>
      <m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>
      <m:e>
        <m:r><m:t>x, </m:t></m:r>
        <m:sSub><m:e><m:r><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:t>user</m:t></m:r></m:sub></m:sSub>
      </m:e>
    </m:d>
    <m:r><m:t> = </m:t></m:r>
    <m:rad>
      <m:radPr><m:degHide m:val="1"/></m:radPr>
      <m:e>
        <m:f>
          <m:num>
            <m:nary>
              <m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>
              <m:sub><m:r><m:t>k=1</m:t></m:r></m:sub>
              <m:sup><m:r><m:t>K</m:t></m:r></m:sup>
              <m:e>
                <m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>k</m:t></m:r></m:sub></m:sSub>
                <m:r><m:t>·</m:t></m:r>
                <m:sSup>
                  <m:e>
                    <m:d>
                      <m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>
                      <m:e>
                        <m:f>
                          <m:num>
                            <m:sSub><m:e><m:r><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:t>k</m:t></m:r></m:sub></m:sSub>
                            <m:r><m:t>-</m:t></m:r>
                            <m:sSub><m:e><m:r><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:t>user,k</m:t></m:r></m:sub></m:sSub>
                          </m:num>
                          <m:den>
                            <m:sSub><m:e><m:r><m:t>σ</m:t></m:r></m:e><m:sub><m:r><m:t>k</m:t></m:r></m:sub></m:sSub>
                          </m:den>
                        </m:f>
                      </m:e>
                    </m:d>
                  </m:e>
                  <m:sup><m:r><m:t>2</m:t></m:r></m:sup>
                </m:sSup>
              </m:e>
            </m:nary>
          </m:num>
          <m:den>
            <m:nary>
              <m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>
              <m:sub><m:r><m:t>k=1</m:t></m:r></m:sub>
              <m:sup><m:r><m:t>K</m:t></m:r></m:sup>
              <m:e>
                <m:sSub><m:e><m:r><m:t>w</m:t></m:r></m:e><m:sub><m:r><m:t>k</m:t></m:r></m:sub></m:sSub>
              </m:e>
            </m:nary>
          </m:den>
        </m:f>
      </m:e>
    </m:rad>
    """
    add_equation_box(doc, math_dist, "Công thức 8", "Khoảng cách Cấu hình Chuẩn hóa có Trọng số (Weighted Normalized Distance)", [
        ("d_config", "Chỉ số khoảng cách hình học đo mức độ khác biệt cấu hình giữa 2 mẫu máy (giá trị càng nhỏ càng giống nhau)"),
        ("w_k", "Trọng số ưu tiên của linh kiện k (CPU: 2.5, GPU: 2.5, RAM: 2.0, Ổ cứng: 1.5, Màn hình: 1.0, Tần số quét: 1.0, Pin: 1.0, Cân nặng: 1.0)"),
        ("x_k", "Giá trị linh kiện k của laptop ứng viên trong kho dữ liệu 225 máy"),
        ("x_user,k", "Giá trị linh kiện k do người dùng mong muốn nhập trên form"),
        ("σ_k", "Độ lệch chuẩn của thuộc tính thứ k trên toàn bộ tập dữ liệu (loại bỏ ảnh hưởng bởi đơn vị đo)")
    ])

    p = doc.add_paragraph()
    p.add_run("4.3. Công thức Tính Tỷ lệ Phần trăm Tương đồng (% Similarity):\n").bold = True
    p.add_run(
        "Khoảng cách hình học d_config được chuyển đổi sang tỷ lệ phần trăm trực quan thông qua hàm suy giảm hàm mũ (Exponential Decay):"
    )

    # CÔNG THỨC 9: SIMILARITY
    math_sim = """
    <m:r><m:t>Similarity (%) = Clip</m:t></m:r>
    <m:d>
      <m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>
      <m:e>
        <m:r><m:t>100 · </m:t></m:r>
        <m:sSup>
          <m:e><m:r><m:t>e</m:t></m:r></m:e>
          <m:sup>
            <m:r><m:t>-0.25 · </m:t></m:r>
            <m:sSub><m:e><m:r><m:t>d</m:t></m:r></m:e><m:sub><m:r><m:t>config</m:t></m:r></m:sub></m:sSub>
          </m:sup>
        </m:sSup>
        <m:r><m:t>,  35.0,  99.5</m:t></m:r>
      </m:e>
    </m:d>
    """
    add_equation_box(doc, math_sim, "Công thức 9", "Tỷ lệ Phần trăm Tương đồng Cấu hình (Similarity Percentage)", [
        ("Similarity (%)", "Độ tương đồng cấu hình (%) hiển thị trực tiếp trên thanh tiến trình Progress Bar của từng sản phẩm gợi ý"),
        ("e^(-0.25 · d_config)", "Hàm nhân suy giảm tiệm cận tự nhiên, phản ánh chính xác cảm nhận thực tế của người dùng"),
        ("Clip(v, 35.0, 99.5)", "Hàm giới hạn giá trị trong khoảng từ 35.0% đến tối đa 99.5% (tránh giá trị phi lý)")
    ])

    p = doc.add_paragraph()
    p.add_run("4.4. Hàm Xếp hạng Ứng viên kèm Điểm phạt Giá (Ranking Score with Price Penalty):\n").bold = True
    p.add_run(
        "Để ưu tiên tối đa các mẫu laptop rơi đúng vào dải chênh lệch giá mục tiêu (±2 triệu VNĐ), hệ thống bổ sung hàm phạt phụ trội:"
    )

    # CÔNG THỨC 10: RANK SCORE
    math_rank = """
    <m:r><m:t>Score = </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>d</m:t></m:r></m:e><m:sub><m:r><m:t>config</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> + 2.5 · max</m:t></m:r>
    <m:d>
      <m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>
      <m:e>
        <m:r><m:t>0,  </m:t></m:r>
        <m:f>
          <m:num>
            <m:d>
              <m:dPr><m:begChr m:val="|"/><m:endChr m:val="|"/></m:dPr>
              <m:e>
                <m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>actual</m:t></m:r></m:sub></m:sSub>
                <m:r><m:t>-</m:t></m:r>
                <m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>pred</m:t></m:r></m:sub></m:sSub>
              </m:e>
            </m:d>
            <m:r><m:t>- 2,000,000</m:t></m:r>
          </m:num>
          <m:den>
            <m:r><m:t>1,000,000</m:t></m:r>
          </m:den>
        </m:f>
      </m:e>
    </m:d>
    """
    add_equation_box(doc, math_rank, "Công thức 10", "Hàm Xếp hạng Ứng viên Đề xuất (Ranking Score)", [
        ("Score", "Chỉ số xếp hạng tổng hợp (máy có điểm Score nhỏ nhất sẽ được xếp vị trí #1 - Tương đồng nhất)"),
        ("|P_actual - P_pred|", "Khoảng cách chênh lệch tuyệt đối giữa giá bán niêm yết thực tế và giá dự đoán (VNĐ)"),
        ("2,000,000 VNĐ", "Ngưỡng chênh lệch giá mục tiêu ban đầu"),
        ("2.5", "Hệ số phạt phụ trội đối với các mẫu vượt ngoài dải 2 triệu đồng để bảo vệ tiêu chí giá cả")
    ])

    # ==================== CHƯƠNG 5 ====================
    doc.add_heading("CHƯƠNG 5: THIẾT KẾ GIAO DIỆN & REST API ENDPOINTS", level=1)
    
    p = doc.add_paragraph()
    p.add_run("5.1. Khung Form Trải nghiệm 2 Lớp (predict.html):\n").bold = True
    p.add_run(
        "• Lớp 1 (1-Click Preset theo Ngành học): 3 khối thẻ ngành học (Kinh tế / Văn phòng, CNTT / Lập trình, Đồ họa & Gaming) "
        "kèm script JavaScript tự động điền các thông số kỹ thuật chuẩn và hiệu ứng highlight viền xanh tức thì.\n"
        "• Lớp 2 (Form Tinh chỉnh 9 Thông số): Form nhập liệu có validation kiểm tra giá trị âm, rỗng, giới hạn logic màn hình và trọng lượng.\n"
        "• Thẻ Kết quả Định giá: Hiển thị giá ước tính định dạng tiền tệ VNĐ nổi bật kèm huy hiệu so sánh chênh lệch (tiết kiệm hơn / cao hơn).\n"
        "• Bảng Top 5 Laptop Đề xuất: Danh sách 5 mẫu kèm thanh tiến trình % tương đồng cấu hình và nút liên kết trực tiếp vào kho máy."
    )

    p = doc.add_paragraph()
    p.add_run("5.2. Danh mục URL Endpoints & REST API:\n").bold = True

    # Bảng 3: Endpoints
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
        ("GET", "/predict", "HTML Web Page", "Hiển thị form định giá, 3 preset mẫu ngành học và chỉ số MAE/RMSE/R² của mô hình."),
        ("POST", "/predict", "HTML Form Body", "Xác thực dữ liệu đầu vào, ước tính giá bán bằng ML và hiển thị Top 5 gợi ý."),
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
        "Bước 3: (Tùy chọn) Chạy kiểm thử độc lập module Học máy:\n"
        "    python -m src.price_prediction\n\n"
        "Bước 4: Khởi động máy chủ Web Flask:\n"
        "    python app.py\n\n"
        "Bước 5: Trải nghiệm trên trình duyệt web tại địa chỉ:\n"
        "    http://127.0.0.1:5000/predict"
    )

    p = doc.add_paragraph()
    p.add_run("6.2. Kết quả Kiểm thử Tự động (Automated Test Report):\n").bold = True
    p.add_run(
        "Toàn bộ các ca kiểm thử tự động đã được thực thi và vượt qua 100%:\n"
        "• Test 1 (GET /): HTTP 200 OK, hiển thị đầy đủ 225 mẫu laptop và Banner giới thiệu Phần 4.\n"
        "• Test 2 (GET /predict): HTTP 200 OK, tải mô hình Joblib thành công, nạp đủ 3 preset ngành học.\n"
        "• Test 3 (POST /predict): HTTP 200 OK, form validation chính xác, hiển thị giá ước tính và Top 5 laptop tương đồng.\n"
        "• Test 4 (POST /api/predict): HTTP 200 OK, trả về JSON chuẩn gồm status: 'success', predicted_price_formatted và mảng recommendations."
    )

    # ==================== CHƯƠNG 7 ====================
    doc.add_heading("CHƯƠNG 7: KẾT LUẬN & HƯỚNG PHÁT TRIỂN TIẾP THEO", level=1)
    p = doc.add_paragraph()
    p.add_run(
        "Phần 4: Xây dựng Mô hình Học máy Dự đoán Giá Laptop đã được hoàn thành xuất sắc, tích hợp trọn vẹn từ tầng thuật toán hồi quy, "
        "đóng gói mô hình bằng Joblib cho đến tầng giao diện web và dịch vụ REST API. "
        "Mô hình đạt độ chính xác ấn tượng (R² đạt 88.21%), các công thức toán học được chuẩn hóa bài bản và chặt chẽ. "
        "Hệ thống không chỉ hoàn thành xuất sắc các mục tiêu học thuật của môn Khoa học Dữ liệu mà còn trở thành công cụ tư vấn mua sắm "
        "công nghệ hữu ích, trực quan và đáng tin cậy cho sinh viên."
    )

    out_path = r"c:\Users\chaut\Documents\Laptops\Bao_Cao_Phan_4_Du_Doan_Gia_Laptop.docx"
    alt_path = r"c:\Users\chaut\Documents\Laptops\Bao_Cao_Phan_4_Du_Doan_Gia_Laptop_Cong_Thuc_Chuan.docx"
    try:
        doc.save(out_path)
        print(f"Đã tạo thành công báo cáo Word: {out_path}")
    except PermissionError:
        doc.save(alt_path)
        print(f"LƯU Ý: Do bạn đang mở file '{os.path.basename(out_path)}' trong Microsoft Word nên hệ thống đã lưu bản cập nhật công thức chuẩn vào:")
        print(f"--> {alt_path}")

if __name__ == '__main__':
    create_report()
