# -*- coding: utf-8 -*-
"""
========================================================================================
BÀI TẬP LỚN: PHÂN TÍCH VÀ PHÂN CỤM DỮ LIỆU LAPTOP
PHẦN 3: PHÂN CỤM DỮ LIỆU (K-MEANS), GIẢM CHIỀU (PCA) VÀ TRỰC QUAN HÓA
File: part3_clustering.py
Mục tiêu:
  1. Đọc và tiền xử lý dữ liệu Laptop từ file 'results.csv'.
  2. Chuẩn hóa dữ liệu (Feature Scaling) bằng StandardScaler.
  3. Tìm số cụm tối ưu k bằng phương pháp Elbow (Inertia) và Silhouette Score.
  4. Phân cụm laptop bằng thuật toán K-Means và gán nhãn thực tế cho từng phân khúc.
  5. Giảm chiều dữ liệu từ 9 chiều xuống 2 chiều bằng PCA để trực quan hóa trên đồ thị 2D.
========================================================================================
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

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

# Cấu hình font tiếng Việt và giao diện cho Matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", palette="deep")


def create_mock_data(output_file='results.csv', n_samples=100):
    """
    HÀM SINH DỮ LIỆU GIẢ ĐỊNH (MOCK DATA)
    --------------------------------------
    Ý nghĩa:
      Khi người dùng chạy code mà chưa có sẵn file 'results.csv', hàm này sẽ tự động
      tạo ra 100 dòng dữ liệu laptop mẫu với các thông số phân bố thực tế (CPU, GPU, RAM,
      Kích thước màn hình, Tần số quét, Khối lượng, Pin, Giá bán).
      Nhờ đó, mã nguồn luôn có thể chạy ngay lập tức (out-of-the-box) mà không gặp lỗi thiếu file.
    """
    print(f"[!] Không tìm thấy file '{output_file}'. Đang tự động sinh {n_samples} dòng dữ liệu mẫu...")
    np.random.seed(42)

    brands = ['ASUS', 'Lenovo', 'Dell', 'HP', 'Acer', 'Apple', 'MSI']
    mock_rows = []

    # Danh sách các phân khúc để tạo dữ liệu đa dạng và thực tế
    categories = ['VanPhong', 'Gaming', 'Ultrabook', 'DoHoaCaoCap']

    for i in range(1, n_samples + 1):
        brand = np.random.choice(brands)
        cat = np.random.choice(categories, p=[0.4, 0.3, 0.2, 0.1])

        if cat == 'VanPhong':
            ten = f"{brand} Vivobook/Ideapad Standard {i}"
            cpu_score = int(np.random.uniform(9000, 16000))
            gpu_score = int(np.random.uniform(1200, 3000))
            ram = int(np.random.choice([8, 16], p=[0.6, 0.4]))
            storage = int(np.random.choice([256, 512], p=[0.3, 0.7]))
            screen = round(float(np.random.choice([14.0, 15.6])), 1)
            refresh = 60
            weight = round(float(np.random.uniform(1.4, 1.8)), 2)
            battery = round(float(np.random.uniform(40, 50)), 1)
            price = round(float(np.random.uniform(10_000_000, 18_000_000)), -4)

        elif cat == 'Gaming':
            ten = f"{brand} Gaming/Legion Power {i}"
            cpu_score = int(np.random.uniform(22000, 36000))
            gpu_score = int(np.random.uniform(9000, 22000))
            ram = int(np.random.choice([16, 32], p=[0.7, 0.3]))
            storage = int(np.random.choice([512, 1024], p=[0.6, 0.4]))
            screen = round(float(np.random.choice([15.6, 16.0, 17.3])), 1)
            refresh = int(np.random.choice([120, 144, 165]))
            weight = round(float(np.random.uniform(2.1, 2.7)), 2)
            battery = round(float(np.random.uniform(55, 90)), 1)
            price = round(float(np.random.uniform(20_000_000, 48_000_000)), -4)

        elif cat == 'Ultrabook':
            ten = f"{brand} Zenbook/XPS Slim {i}"
            cpu_score = int(np.random.uniform(18000, 26000))
            gpu_score = int(np.random.uniform(3500, 5000))
            ram = int(np.random.choice([16, 32], p=[0.7, 0.3]))
            storage = int(np.random.choice([512, 1024], p=[0.5, 0.5]))
            screen = round(float(np.random.choice([13.3, 14.0])), 1)
            refresh = int(np.random.choice([60, 90, 120]))
            weight = round(float(np.random.uniform(1.0, 1.35)), 2)
            battery = round(float(np.random.uniform(60, 75)), 1)
            price = round(float(np.random.uniform(24_000_000, 38_000_000)), -4)

        else: # DoHoaCaoCap / Workstation
            ten = f"{brand} ProArt/Studio Extreme {i}"
            cpu_score = int(np.random.uniform(30000, 42000))
            gpu_score = int(np.random.uniform(16000, 28000))
            ram = int(np.random.choice([32, 64], p=[0.7, 0.3]))
            storage = int(np.random.choice([1024, 2048], p=[0.6, 0.4]))
            screen = round(float(np.random.choice([16.0, 17.0])), 1)
            refresh = int(np.random.choice([120, 165]))
            weight = round(float(np.random.uniform(1.9, 2.4)), 2)
            battery = round(float(np.random.uniform(75, 99)), 1)
            price = round(float(np.random.uniform(45_000_000, 85_000_000)), -4)

        mock_rows.append({
            'TenLaptop': ten,
            'Hang': brand,
            'DiemCPU': cpu_score,
            'DiemGPU': gpu_score,
            'RAM': ram,
            'DungLuongLuuTru': storage,
            'KichThuocManHinh': screen,
            'TanSoQuet': refresh,
            'KhoiLuong': weight,
            'Pin': battery,
            'GiaBan': price
        })

    df_mock = pd.DataFrame(mock_rows)
    df_mock.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"[✓] Đã tạo thành công file '{output_file}' gồm {len(df_mock)} mẫu laptop thực tế!")
    return df_mock


def load_dataset(csv_path='results.csv'):
    """
    HÀM ĐỌC DỮ LIỆU ĐẦU VÀO
    ------------------------
    Quy trình kiểm tra:
      1. Nếu file 'results.csv' đã tồn tại: Đọc trực tiếp.
      2. Nếu chưa có nhưng có file 'data/laptops.csv' trong dự án:
         Chuyển đổi các cột tiếng Anh sang cấu trúc tiếng Việt chuẩn của Phần 3 và lưu ra 'results.csv'.
      3. Nếu không có cả hai: Tự động gọi hàm `create_mock_data` để sinh dữ liệu.
    """
    if os.path.exists(csv_path):
        print(f"[+] Tìm thấy file dữ liệu: '{csv_path}'")
        df = pd.read_csv(csv_path)
    elif os.path.exists('data/laptops.csv'):
        print("[+] Phát hiện file 'data/laptops.csv'. Đang trích xuất và chuyển đổi sang 'results.csv'...")
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
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"[✓] Đã lưu {len(df)} dòng dữ liệu chuẩn hóa sang '{csv_path}'.")
    else:
        df = create_mock_data(csv_path, n_samples=100)

    print(f"-> Tổng số dòng dữ liệu: {len(df)} dòng, {df.shape[1]} cột.")
    return df


def main():
    parser = argparse.ArgumentParser(description="Phân cụm dữ liệu Laptop bằng K-Means và trực quan hóa PCA.")
    parser.add_argument('--file', type=str, default='results.csv', help="Đường dẫn file CSV dữ liệu (mặc định: results.csv)")
    parser.add_argument('--k', type=int, default=None, help="Số cụm k chỉ định (nếu bỏ qua, chương trình sẽ tự động chọn k theo Silhouette Score tối ưu)")
    args = parser.parse_args()

    print("=" * 80)
    print(" BÀI TẬP LỚN PYTHON: PHÂN TÍCH VÀ PHÂN CỤM DỮ LIỆU LAPTOP (PHẦN 3)")
    print("=" * 80)

    # ----------------------------------------------------------------------------------
    # BƯỚC 1: ĐỌC DỮ LIỆU
    # ----------------------------------------------------------------------------------
    df = load_dataset(args.file)

    # Danh sách 9 đặc trưng định lượng được sử dụng để phân cụm
    feature_cols = [
        'DiemCPU', 'DiemGPU', 'RAM', 'DungLuongLuuTru',
        'KichThuocManHinh', 'TanSoQuet', 'KhoiLuong', 'Pin', 'GiaBan'
    ]

    print("\n[BƯỚC 1] 9 thuộc tính số dùng cho phân cụm:")
    for i, col in enumerate(feature_cols, 1):
        print(f"  {i}. {col} (Min: {df[col].min()}, Max: {df[col].max()})")

    X = df[feature_cols].values

    # ----------------------------------------------------------------------------------
    # BƯỚC 2: CHUẨN HÓA DỮ LIỆU (FEATURE SCALING VỚI STANDARDSCALER)
    # ----------------------------------------------------------------------------------
    """
    GIẢI THÍCH LÝ THUYẾT:
      - Thuật toán K-Means phân cụm dựa trên khoảng cách hình học Euclid giữa các điểm:
            d(p, q) = sqrt( sum( (p_i - q_i)^2 ) )
      - Các thuộc tính có đơn vị đo và phạm vi cực kỳ chênh lệch:
          + Giá bán: 10,000,000 -> 80,000,000 VND
          + Điểm CPU/GPU: 1,000 -> 40,000
          + RAM: 8 -> 64 GB
          + Khối lượng: 1.0 -> 2.8 kg
      - Nếu không chuẩn hóa, 'GiaBan' và 'DiemCPU' sẽ áp đảo hoàn toàn các biến khác.
      - Giải pháp: Sử dụng StandardScaler để biến đổi mỗi thuộc tính về phân phối có
        Giá trị trung bình mean = 0 và Độ lệch chuẩn std = 1 (z = (x - mu) / sigma).
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print("\n[BƯỚC 2] Chuẩn hóa dữ liệu thành công với StandardScaler:")
    print(f"  -> Dữ liệu sau chuẩn hóa có shape: {X_scaled.shape}")
    print(f"  -> Trung bình mỗi cột ~ {np.mean(X_scaled, axis=0).round(2)}")
    print(f"  -> Độ lệch chuẩn mỗi cột ~ {np.std(X_scaled, axis=0).round(2)}")

    # ----------------------------------------------------------------------------------
    # BƯỚC 3: XÁC ĐỊNH SỐ CỤM TỐI ƯU k (ELBOW METHOD & SILHOUETTE SCORE)
    # ----------------------------------------------------------------------------------
    """
    GIẢI THÍCH LÝ THUYẾT:
      1. Phương pháp Elbow (Inertia - Tổng bình phương khoảng cách từ mỗi điểm đến tâm cụm):
         Khi k tăng, Inertia luôn giảm. Ta tìm điểm 'khuỷu tay' (Elbow) - nơi tốc độ giảm
         chậm lại đáng kể. Đó là số cụm cân bằng giữa độ phức tạp và độ chính xác.
      2. Điểm Silhouette Score:
         Đo lường mức độ tương đồng của một điểm với cụm của chính nó (độ gắn kết) so với
         các cụm khác (độ phân tách). Điểm nằm trong [-1, 1], giá trị càng cao thể hiện cụm
         càng rõ ràng và tách biệt tốt.
    """
    k_range = range(2, 9)
    inertias = []
    silhouette_scores = []

    print("\n[BƯỚC 3] Đánh giá chất lượng phân cụm với k từ 2 đến 8:")
    for k in k_range:
        kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans_temp.fit(X_scaled)
        inertias.append(kmeans_temp.inertia_)
        score = silhouette_score(X_scaled, kmeans_temp.labels_)
        silhouette_scores.append(score)
        print(f"  - k = {k:d} | Inertia = {kmeans_temp.inertia_:10.2f} | Silhouette Score = {score:.4f}")

    # Vẽ biểu đồ kép: Elbow và Silhouette Score
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Đồ thị 1: Elbow
    axes[0].plot(list(k_range), inertias, marker='o', linewidth=2.5, markersize=8, color='#1f77b4')
    axes[0].set_title('Phương Pháp Khuỷu Tay (Elbow Method)', fontsize=13, fontweight='bold', pad=12)
    axes[0].set_xlabel('Số lượng cụm (k)', fontsize=11)
    axes[0].set_ylabel('Inertia (Tổng bình phương sai số nội cụm)', fontsize=11)
    axes[0].grid(True, linestyle='--', alpha=0.6)
    axes[0].set_xticks(list(k_range))

    # Đồ thị 2: Silhouette Score
    axes[1].plot(list(k_range), silhouette_scores, marker='s', linewidth=2.5, markersize=8, color='#2ca02c')
    axes[1].set_title('Hệ Số Phân Tách (Silhouette Score)', fontsize=13, fontweight='bold', pad=12)
    axes[1].set_xlabel('Số lượng cụm (k)', fontsize=11)
    axes[1].set_ylabel('Điểm Silhouette trung bình', fontsize=11)
    axes[1].grid(True, linestyle='--', alpha=0.6)
    axes[1].set_xticks(list(k_range))

    # Đánh dấu đỉnh Silhouette cao nhất
    best_k_idx = int(np.argmax(silhouette_scores))
    auto_k = list(k_range)[best_k_idx]
    axes[1].axvline(auto_k, color='red', linestyle=':', label=f'k Silhouette tối ưu = {auto_k}')
    axes[1].legend()

    plt.tight_layout()
    plt.savefig('elbow_silhouette_analysis.png', dpi=300)
    print(f"\n[✓] Đã lưu biểu đồ đánh giá k vào file: 'elbow_silhouette_analysis.png'")
    plt.close()

    # Xác định k áp dụng: theo tham số dòng lệnh hoặc tự động
    if args.k is not None:
        optimal_k = args.k
        print(f"\n-> Áp dụng k = {optimal_k} do người dùng chỉ định qua tham số --k.")
    else:
        optimal_k = auto_k
        print(f"\n-> Tự động chọn k tối ưu = {optimal_k} (đạt Silhouette Score cao nhất: {silhouette_scores[best_k_idx]:.4f})")

    # Tiến hành phân cụm chính thức với k tối ưu
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=15)
    df['Cluster'] = kmeans.fit_predict(X_scaled)

    # ----------------------------------------------------------------------------------
    # PHÂN TÍCH VÀ ĐẶT TÊN CHO TỪNG CỤM (PROFILING)
    # ----------------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print(" BẢNG THỐNG KÊ GIÁ TRỊ TRUNG BÌNH THEO TỪNG CỤM (CLUSTER PROFILES)")
    print("=" * 80)

    # 1. Tính toán giá trị trung bình từng thuộc tính trong từng cụm
    cluster_summary = df.groupby('Cluster')[feature_cols].mean()

    # 2. Đặt tên định tính cho từng cụm dựa theo tương quan giá trị thực tế
    cluster_labels = {}
    for cluster_id in range(optimal_k):
        mean_price = cluster_summary.loc[cluster_id, 'GiaBan']
        mean_cpu = cluster_summary.loc[cluster_id, 'DiemCPU']
        mean_gpu = cluster_summary.loc[cluster_id, 'DiemGPU']
        mean_ram = cluster_summary.loc[cluster_id, 'RAM']
        mean_weight = cluster_summary.loc[cluster_id, 'KhoiLuong']
        mean_refresh = cluster_summary.loc[cluster_id, 'TanSoQuet']

        # 1. Phân khúc Gaming Siêu Cấp / Workstation Đồ Họa Nặng
        if (mean_gpu >= 16000 or mean_price >= 45_000_000) and mean_refresh >= 120:
            label = "Laptop Gaming Flagship / Workstation Cao Cấp"
        # 2. Phân khúc Gaming / Đồ Họa Tầm Trung - Phổ Thông
        elif mean_gpu >= 7000 and mean_refresh >= 120 and mean_weight >= 1.8:
            label = "Laptop Gaming / Đồ Họa Tầm Trung"
        # 3. Phân khúc Ultrabook Doanh Nhân Siêu Mỏng Nhẹ
        elif mean_price >= 25_000_000 and mean_weight < 1.55:
            label = "Ultrabook / Doanh Nhân Mỏng Nhẹ Cao Cấp"
        # 4. Phân khúc Laptop Học Tập / Văn Phòng Phổ Thông - Giá Rẻ
        elif mean_price < 18_000_000 and mean_gpu < 5000:
            label = "Laptop Học Tập / Văn Phòng Phổ Thông - Giá Rẻ"
        # 5. Phân khúc Văn Phòng Đa Nhiệm Tầm Trung Cận Cao Cấp
        elif mean_gpu < 7000 and mean_weight < 1.8:
            label = "Laptop Đa Nhiệm / Văn Phòng Tầm Trung"
        else:
            label = f"Laptop Cấu Hình Đặc Thù (Cụm {cluster_id})"

        cluster_labels[cluster_id] = label

    # Cơ chế kiểm tra an toàn: Nếu có 2 cụm bị trùng tên, tự động phân cấp theo mức giá bán
    label_counts = {}
    for cid, lbl in cluster_labels.items():
        label_counts[lbl] = label_counts.get(lbl, 0) + 1

    for duplicate_label, count in label_counts.items():
        if count > 1:
            duplicate_cids = [cid for cid, lbl in cluster_labels.items() if lbl == duplicate_label]
            # Sắp xếp các cụm bị trùng theo giá bán tăng dần
            duplicate_cids.sort(key=lambda x: cluster_summary.loc[x, 'GiaBan'])
            tier_suffixes = [" (Tiêu chuẩn / Tầm trung)", " (Cao cấp / Flagship)", " (Siêu cấp)"]
            for idx, cid in enumerate(duplicate_cids):
                suffix = tier_suffixes[idx] if idx < len(tier_suffixes) else f" (Nhóm {idx+1})"
                cluster_labels[cid] = f"{duplicate_label}{suffix}"

    # In kết quả phân tích chi tiết
    df['Cluster_Name'] = df['Cluster'].map(cluster_labels)
    for c_id in range(optimal_k):
        print(f"\n[+] CỤM {c_id}: {cluster_labels[c_id]}")
        print(f"    - Số lượng mẫu máy: {(df['Cluster'] == c_id).sum()} máy")
        print(f"    - Giá bán trung bình: {cluster_summary.loc[c_id, 'GiaBan']:,.0f} VND")
        print(f"    - Điểm CPU trung bình: {cluster_summary.loc[c_id, 'DiemCPU']:,.0f}")
        print(f"    - Điểm GPU trung bình: {cluster_summary.loc[c_id, 'DiemGPU']:,.0f}")
        print(f"    - RAM trung bình: {cluster_summary.loc[c_id, 'RAM']:.1f} GB")
        print(f"    - Bộ nhớ trong SSD: {cluster_summary.loc[c_id, 'DungLuongLuuTru']:.0f} GB")
        print(f"    - Màn hình: {cluster_summary.loc[c_id, 'KichThuocManHinh']:.1f} inch, {cluster_summary.loc[c_id, 'TanSoQuet']:.0f} Hz")
        print(f"    - Trọng lượng: {cluster_summary.loc[c_id, 'KhoiLuong']:.2f} kg | Pin: {cluster_summary.loc[c_id, 'Pin']:.1f} Wh")
        # In ví dụ 2 máy đại diện trong cụm
        samples = df[df['Cluster'] == c_id]['TenLaptop'].head(2).tolist()
        print(f"    - Ví dụ tiêu biểu: {', '.join(samples)}")

    # ----------------------------------------------------------------------------------
    # BƯỚC 4: GIẢM CHIỀU DỮ LIỆU BẰNG PCA & TRỰC QUAN HÓA 2D
    # ----------------------------------------------------------------------------------
    """
    GIẢI THÍCH LÝ THUYẾT:
      - Dữ liệu ban đầu có 9 chiều (9 thuộc tính), mắt người không thể quan sát được trong
        không gian nhiều hơn 3 chiều.
      - Thuật toán PCA (Principal Component Analysis - Phân tích thành phần chính):
        Tìm các trục trực giao (Principal Components) lưu giữ phương sai (thông tin) lớn nhất
        của tập dữ liệu.
      - Ta nén 9 chiều xuống 2 chiều chính: PC1 và PC2.
      - Sau đó chiếu các điểm dữ liệu và tâm cụm lên không gian 2D để quan sát trực quan
        mức độ gom cụm và phân tách giữa các nhóm laptop.
    """
    print("\n" + "=" * 80)
    print(" BƯỚC 4: GIẢM CHIỀU DỮ LIỆU (PCA) VÀ VẼ BIỂU ĐỒ SCATTER PLOT 2D")
    print("=" * 80)

    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    df['PC1'] = X_pca[:, 0]
    df['PC2'] = X_pca[:, 1]

    # Phương sai được giải thích bởi 2 thành phần chính
    var_pc1 = pca.explained_variance_ratio_[0] * 100
    var_pc2 = pca.explained_variance_ratio_[1] * 100
    total_var = var_pc1 + var_pc2

    print(f"-> PC1 giữ lại: {var_pc1:.2f}% thông tin phương sai.")
    print(f"-> PC2 giữ lại: {var_pc2:.2f}% thông tin phương sai.")
    print(f"-> Tổng phương sai được giữ lại trong không gian 2D: {total_var:.2f}%")

    # Chiếu các tâm cụm (Centroids) sang không gian PCA 2D
    centroids_scaled = kmeans.cluster_centers_
    centroids_pca = pca.transform(centroids_scaled)

    # Vẽ biểu đồ phân bố cụm 2D
    plt.figure(figsize=(12, 8))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']

    for c_id in range(optimal_k):
        sub_df = df[df['Cluster'] == c_id]
        plt.scatter(
            sub_df['PC1'],
            sub_df['PC2'],
            c=colors[c_id % len(colors)],
            label=f"Cụm {c_id}: {cluster_labels[c_id]} ({len(sub_df)} máy)",
            s=80,
            alpha=0.75,
            edgecolors='white',
            linewidth=0.8
        )

    # Đánh dấu tâm cụm
    plt.scatter(
        centroids_pca[:, 0],
        centroids_pca[:, 1],
        c='black',
        marker='X',
        s=220,
        linewidths=2,
        label='Tâm Cụm (Centroids)',
        zorder=10
    )

    plt.title(
        f'TRỰC QUAN HÓA CÁC CỤM LAPTOP BẰNG PCA (2D)\n'
        f'(Tổng phương sai giải thích: {total_var:.2f}% | k = {optimal_k})',
        fontsize=14,
        fontweight='bold',
        pad=15
    )
    plt.xlabel(f'Thành phần chính 1 - PC1 ({var_pc1:.2f}%)', fontsize=12)
    plt.ylabel(f'Thành phần chính 2 - PC2 ({var_pc2:.2f}%)', fontsize=12)
    plt.axhline(0, color='grey', linestyle='--', linewidth=0.8, alpha=0.5)
    plt.axvline(0, color='grey', linestyle='--', linewidth=0.8, alpha=0.5)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True, fontsize=10)
    plt.tight_layout()

    # Lưu biểu đồ
    output_image = 'pca_clusters.png'
    plt.savefig(output_image, dpi=300)
    print(f"[✓] Đã xuất thành công biểu đồ phân cụm PCA vào file: '{output_image}'")
    plt.close()

    # Sắp xếp toàn bộ dữ liệu theo thứ tự từng Cụm (hết cụm này mới đến cụm khác)
    df_sorted = df.sort_values(by=['Cluster', 'GiaBan'], ascending=[True, True])

    # Xuất file kết quả phân cụm có thêm cột Cluster và Cluster_Name
    output_clustered_csv = 'results_clustered.csv'
    df_sorted.to_csv(output_clustered_csv, index=False, encoding='utf-8-sig')
    print(f"[✓] Đã lưu dữ liệu sắp xếp theo từng cụm vào file: '{output_clustered_csv}'")
    print("=" * 80)
    print(" HOÀN THÀNH PHẦN 3: PHÂN CỤM & PCA TRỰC QUAN HÓA!")
    print("=" * 80)


if __name__ == '__main__':
    main()
