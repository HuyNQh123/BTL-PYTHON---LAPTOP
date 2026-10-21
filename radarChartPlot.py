# -*- coding: utf-8 -*-
"""
========================================================================================
BÀI TẬP LỚN: PHÂN TÍCH VÀ PHÂN CỤM DỮ LIỆU LAPTOP
PHẦN 3: SO SÁNH TRỰC QUAN HAI LAPTOP BẰNG BIỂU ĐỒ RADAR (RADAR CHART / SPIDER PLOT)
File: radarChartPlot.py
Cú pháp thực thi từ Terminal / Dòng lệnh:
  python radarChartPlot.py --p1 "Ten Laptop 1" --p2 "Ten Laptop 2" --Attribute "DiemCPU,DiemGPU,RAM,Pin,GiaBan"

Mục tiêu kỹ thuật:
  1. Phân tích tham số dòng lệnh bằng thư viện argparse.
  2. Đọc dữ liệu từ 'results.csv' (hoặc dữ liệu từ Phần 1).
  3. Chuẩn hóa dữ liệu các thuộc tính chỉ định về thang đo [0, 1] bằng MinMaxScaler.
  4. Tìm kiếm 2 mẫu laptop chỉ định, hỗ trợ tìm kiếm gần đúng và báo lỗi chi tiết nếu không tìm thấy.
  5. Dựng biểu đồ Radar đa trục (phép chiếu Polar trong Matplotlib), tô màu mờ trực quan.
  6. Xuất đồ thị ra file ảnh 'radar_comparison.png' và hiển thị cho người dùng.
========================================================================================
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Cấu hình encoding UTF-8 cho terminal trên Windows tránh lỗi UnicodeEncodeError
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Cấu hình font chữ hiển thị chuẩn
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.unicode_minus'] = False


def parse_arguments():
    """
    HÀM CẤU HÌNH VÀ TIẾP NHẬN THAM SỐ DÒNG LỆNH (CLI)
    --------------------------------------------------
    Sử dụng module argparse của Python chuẩn để nhận diện:
      --p1: Tên mẫu laptop thứ nhất cần so sánh.
      --p2: Tên mẫu laptop thứ hai cần so sánh.
      --Attribute: Chuỗi danh sách các cột thuộc tính, phân cách bởi dấu phẩy ','.
      --file: Đường dẫn file CSV (mặc định là 'results.csv').
      --output: Tên file ảnh xuất ra (mặc định là 'radar_comparison.png').
    """
    parser = argparse.ArgumentParser(
        description="So sánh trực quan hai laptop bằng biểu đồ Radar (Spider Plot)."
    )
    parser.add_argument(
        '--p1',
        type=str,
        required=False,
        default=None,
        help='Tên chính xác hoặc từ khóa tên của Laptop 1.'
    )
    parser.add_argument(
        '--p2',
        type=str,
        required=False,
        default=None,
        help='Tên chính xác hoặc từ khóa tên của Laptop 2.'
    )
    parser.add_argument(
        '--Attribute',
        type=str,
        required=False,
        default='DiemCPU,DiemGPU,RAM,Pin,GiaBan',
        help='Danh sách các thuộc tính so sánh, cách nhau bằng dấu phẩy (Ví dụ: DiemCPU,DiemGPU,RAM,Pin,GiaBan).'
    )
    parser.add_argument(
        '--file',
        type=str,
        default='results.csv',
        help='Đường dẫn file dữ liệu CSV (mặc định: results.csv).'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='radar_comparison.png',
        help='Đường dẫn file ảnh đầu ra (mặc định: radar_comparison.png).'
    )
    parser.add_argument(
        '--no-show',
        action='store_true',
        help='Chỉ lưu file ảnh mà không hiển thị cửa sổ đồ thị (thích hợp khi chạy batch hoặc môi trường không màn hình).'
    )

    return parser.parse_args()


def load_dataset_safely(file_path):
    """
    HÀM ĐỌC DỮ LIỆU ĐẢM BẢO CHẠY ĐƯỢC MỌI TÌNH HUỐNG
    -----------------------------------------------
    Nếu chưa có results.csv, tự động chuyển đổi từ data/laptops.csv hoặc gọi part3_clustering.
    """
    if os.path.exists(file_path):
        return pd.read_csv(file_path)

    # Nếu chưa có file results.csv, thử tìm data/laptops.csv
    if os.path.exists('data/laptops.csv'):
        print(f"[!] File '{file_path}' chưa có sẵn. Đang trích xuất tự động từ 'data/laptops.csv'...")
        df_raw = pd.read_csv('data/laptops.csv')
        column_mapping = {
            'name': 'TenLaptop',
            'brand': 'Hang',
            'cpu_score': 'DiemCPU',
            'gpu_score': 'DiemGPU',
            'ram': 'RAM',
            'storage': 'DungLuongLuuTru',
            'screen_size': 'KichThuocManHinh',
            'refresh_rate': 'TanSoQuet',
            'weight': 'KhoiLuong',
            'battery': 'Pin',
            'price': 'GiaBan'
        }
        df = df_raw.rename(columns=column_mapping)
        available_cols = [c for c in column_mapping.values() if c in df.columns]
        df = df[available_cols].dropna()
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        return df

    # Nếu không có bất kỳ file nào, gọi hàm sinh dữ liệu mẫu
    try:
        from part3_clustering import create_mock_data
        return create_mock_data(file_path, n_samples=100)
    except Exception:
        raise FileNotFoundError(f"Không thể tìm thấy hoặc tạo file dữ liệu '{file_path}'!")


def find_laptop_by_name(df, name_query, arg_name="--p"):
    """
    HÀM TÌM KIẾM LAPTOP VỚI CƠ CHẾ XỬ LÝ NGOẠI LỆ LINH HOẠT
    -------------------------------------------------------
    1. So khớp chính xác 100% (Exact match).
    2. Nếu không có, tìm kiếm chứa từ khóa không phân biệt hoa thường (Case-insensitive substring match).
    3. Nếu không tìm thấy, báo lỗi và in ra danh sách 5 laptop mẫu trong tập dữ liệu để gợi ý.
    """
    # 1. So khớp chính xác
    match = df[df['TenLaptop'].str.strip() == name_query.strip()]
    if len(match) > 0:
        return match.iloc[0]

    # 2. Tìm kiếm chứa chuỗi (contains)
    match_fuzzy = df[df['TenLaptop'].str.lower().str.contains(name_query.strip().lower(), regex=False)]
    if len(match_fuzzy) > 0:
        selected = match_fuzzy.iloc[0]
        print(f"[i] Tìm thấy máy phù hợp với từ khóa '{name_query}': \"{selected['TenLaptop']}\"")
        return selected

    # 3. Ngoại lệ: Không tìm thấy máy
    print("\n" + "!" * 75)
    print(f"[LỖI] Không tìm thấy laptop nào khớp với tham số {arg_name} = '{name_query}'!")
    print("Dưới đây là một số gợi ý tên laptop có trong tập dữ liệu để bạn lựa chọn:")
    sample_names = df['TenLaptop'].dropna().unique()[:6]
    for i, s_name in enumerate(sample_names, 1):
        print(f"  {i}. {s_name}")
    print("!" * 75 + "\n")
    sys.exit(1)


def draw_radar_chart(laptop1, laptop2, attributes, original_vals1, original_vals2, output_file, show_plot=True):
    """
    HÀM VẼ BIỂU ĐỒ RADAR (SPIDER PLOT) TRÊN HỆ TRỤC TỌA ĐỘ CỰC (POLAR PROJECTION)
    ----------------------------------------------------------------------------
    Ý nghĩa:
      - Hệ tọa độ cực (polar): Các thuộc tính được sắp xếp xung quanh vòng tròn từ góc 0 đến 2*pi.
      - Các giá trị đã được chuẩn hóa trong thang [0, 1] giúp các cạnh biểu đồ đồng đều.
      - Đóng kín vòng tròn (wrap around): Nối điểm cuối cùng quay lại điểm đầu tiên.
      - Phủ màu mờ (fill with alpha) để so sánh diện tích thế mạnh của từng mẫu laptop.
    """
    num_vars = len(attributes)

    # 1. Tính toán các góc theta cho từng trục thuộc tính
    # Chia đều vòng tròn 2*pi thành num_vars phần
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Để khép kín hình đa giác radar, ta cần lặp lại điểm đầu tiên ở cuối danh sách
    angles += angles[:1]
    values1 = laptop1[attributes].tolist()
    values1 += values1[:1]

    values2 = laptop2[attributes].tolist()
    values2 += values2[:1]

    # Nhãn hiển thị cho từng đỉnh
    labels = list(attributes)

    # 2. Khởi tạo đồ thị Polar
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    # Đặt góc bắt đầu ở đỉnh (12 giờ) và quay theo chiều kim đồng hồ
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Đặt nhãn cho các trục thuộc tính
    plt.xticks(angles[:-1], labels, size=11, fontweight='bold', color='#333333')

    # Thiết lập thang đo đồng tâm từ 0 đến 1.0
    ax.set_rlabel_position(0)
    plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0 (Max)"], color="grey", size=9)
    plt.ylim(0, 1.1)

    # 3. Vẽ Laptop 1 (Màu Xanh Dương)
    name1 = laptop1['TenLaptop']
    ax.plot(angles, values1, color='#1f77b4', linewidth=2.5, linestyle='solid', label=f"1. {name1}")
    ax.fill(angles, values1, color='#1f77b4', alpha=0.25)
    ax.scatter(angles[:-1], values1[:-1], color='#1f77b4', s=60, zorder=5)

    # 4. Vẽ Laptop 2 (Màu Đỏ Cam)
    name2 = laptop2['TenLaptop']
    ax.plot(angles, values2, color='#d62728', linewidth=2.5, linestyle='solid', label=f"2. {name2}")
    ax.fill(angles, values2, color='#d62728', alpha=0.25)
    ax.scatter(angles[:-1], values2[:-1], color='#d62728', s=60, zorder=5)

    # 5. Tiêu đề và chú giải
    plt.title(
        f"SO SÁNH CẤU HÌNH CHI TIẾT BẰNG BIỂU ĐỒ RADAR\n(Thang đo chuẩn hóa MinMaxScaler [0, 1])",
        size=14,
        fontweight='bold',
        pad=25,
        color='#111111'
    )

    # Đặt Legend ở vị trí dưới cùng
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=1, frameon=True, fontsize=10)

    # Thêm bảng thông số thực tế để tiện đối chiếu
    table_text = "THÔNG SỐ THỰC TẾ:\n"
    for attr in attributes:
        v1 = original_vals1[attr]
        v2 = original_vals2[attr]
        if 'Gia' in attr:
            table_text += f"• {attr}: {v1:,.0f} đ  VS  {v2:,.0f} đ\n"
        else:
            table_text += f"• {attr}: {v1}  VS  {v2}\n"

    # Đặt ghi chú số liệu góc trái bên dưới
    fig.text(
        0.05, 0.02, table_text.strip(),
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#cccccc", alpha=0.9)
    )

    plt.tight_layout()

    # 6. Lưu file và hiển thị
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n[✓] Đã xuất thành công biểu đồ so sánh Radar ra file: '{output_file}'")

    # Hiển thị cửa sổ đồ thị (nếu có môi trường GUI và show_plot=True)
    if show_plot:
        try:
            plt.show()
        except Exception:
            pass
    plt.close()


def main():
    print("=" * 80)
    print(" CÔNG CỤ SO SÁNH LAPTOP BẰNG BIỂU ĐỒ RADAR (CLI RADAR CHART)")
    print("=" * 80)

    args = parse_arguments()

    # ----------------------------------------------------------------------------------
    # BƯỚC 1: ĐỌC FILE DỮ LIỆU
    # ----------------------------------------------------------------------------------
    df = load_dataset_safely(args.file)

    # ----------------------------------------------------------------------------------
    # BƯỚC 2: XỬ LÝ DANH SÁCH THUỘC TÍNH (ATTRIBUTES)
    # ----------------------------------------------------------------------------------
    raw_attrs = [attr.strip() for attr in args.Attribute.split(',') if attr.strip()]
    if not raw_attrs:
        raw_attrs = ['DiemCPU', 'DiemGPU', 'RAM', 'Pin', 'GiaBan']

    # Kiểm tra tính hợp lệ của thuộc tính trong tập dữ liệu
    invalid_attrs = [a for a in raw_attrs if a not in df.columns]
    if invalid_attrs:
        print(f"[LỖI] Các thuộc tính sau không tồn tại trong file: {invalid_attrs}")
        print(f"Các thuộc tính có sẵn: {list(df.columns)}")
        sys.exit(1)

    print(f"\n[+] Các thuộc tính được chọn để so sánh ({len(raw_attrs)} tiêu chí):")
    for i, a in enumerate(raw_attrs, 1):
        print(f"    {i}. {a}")

    # ----------------------------------------------------------------------------------
    # BƯỚC 3: TÌM 2 LAPTOP CẦN SO SÁNH
    # ----------------------------------------------------------------------------------
    # Nếu người dùng không nhập tham số --p1 hoặc --p2, lấy mặc định 2 dòng đầu để demo chạy ngay
    p1_name = args.p1
    p2_name = args.p2

    if not p1_name:
        p1_name = df.iloc[0]['TenLaptop']
        print(f"[i] Không chỉ định --p1. Tự động chọn máy 1: \"{p1_name}\"")
    if not p2_name:
        p2_name = df.iloc[1]['TenLaptop']
        print(f"[i] Không chỉ định --p2. Tự động chọn máy 2: \"{p2_name}\"")

    laptop1_orig = find_laptop_by_name(df, p1_name, arg_name="--p1")
    laptop2_orig = find_laptop_by_name(df, p2_name, arg_name="--p2")

    print(f"\n[+] Đã xác định 2 laptop cần so sánh:")
    print(f"    Máy 1: {laptop1_orig['TenLaptop']}")
    print(f"    Máy 2: {laptop2_orig['TenLaptop']}")

    # ----------------------------------------------------------------------------------
    # BƯỚC 4: CHUẨN HÓA DỮ LIỆU BẰNG MINMAXSCALER ([0, 1])
    # ----------------------------------------------------------------------------------
    """
    GIẢI THÍCH LÝ THUYẾT:
      - Biểu đồ Radar có các trục xuất phát từ cùng một gốc tâm O và hướng ra ngoài.
      - Để hình đa giác không bị méo lệch dị thường (ví dụ: Giá bán 30,000,000 sẽ dài gấp
        triệu lần Trọng lượng 1.5kg hay RAM 16GB), ta bắt buộc phải đưa mọi thuộc tính
        về cùng khoảng giá trị [0, 1] bằng MinMaxScaler:
            x_norm = (x - x_min) / (x_max - x_min)
      - Giá trị 1.0 đại diện cho laptop có thông số cao nhất trong toàn bộ tập dữ liệu,
        và 0.0 là mức thấp nhất trong thị trường khảo sát.
    """
    scaler = MinMaxScaler()
    df_normalized = df.copy()
    df_normalized[raw_attrs] = scaler.fit_transform(df[raw_attrs])

    laptop1_norm = df_normalized.loc[laptop1_orig.name]
    laptop2_norm = df_normalized.loc[laptop2_orig.name]

    # In bảng so sánh chi tiết
    print("\n" + "=" * 80)
    print(f"{'Thuộc tính':<20} | {'Giá trị Máy 1 (Thực / [0-1])':<30} | {'Giá trị Máy 2 (Thực / [0-1])':<30}")
    print("-" * 80)
    for attr in raw_attrs:
        v1_real = laptop1_orig[attr]
        v2_real = laptop2_orig[attr]
        v1_norm = laptop1_norm[attr]
        v2_norm = laptop2_norm[attr]
        if 'Gia' in attr:
            str1 = f"{v1_real:,.0f} đ ({v1_norm:.2f})"
            str2 = f"{v2_real:,.0f} đ ({v2_norm:.2f})"
        else:
            str1 = f"{v1_real} ({v1_norm:.2f})"
            str2 = f"{v2_real} ({v2_norm:.2f})"
        print(f"{attr:<20} | {str1:<30} | {str2:<30}")
    print("=" * 80)

    # ----------------------------------------------------------------------------------
    # BƯỚC 5 & 6: VẼ VÀ XUẤT BIỂU ĐỒ RADAR
    # ----------------------------------------------------------------------------------
    draw_radar_chart(
        laptop1=laptop1_norm,
        laptop2=laptop2_norm,
        attributes=raw_attrs,
        original_vals1=laptop1_orig,
        original_vals2=laptop2_orig,
        output_file=args.output,
        show_plot=(not args.no_show)
    )


if __name__ == '__main__':
    main()
