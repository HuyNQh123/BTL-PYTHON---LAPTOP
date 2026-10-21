from flask import Flask, render_template, request, jsonify
import sys
import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Tránh lỗi GUI thread trong Flask
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Cho phép Python tìm thấy thư mục src
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from src.data_cleaning import load_data, clean_data

app = Flask(__name__)


# --------------------------------------------------------------------------------------
# TRANG CHỦ & DANH SÁCH LAPTOP (PHẦN 1 & 2)
# --------------------------------------------------------------------------------------
@app.route('/')
def index():
    df_raw = load_data('data/laptops.csv')
    total_laptops = 0
    total_brands = 0
    avg_price = 0
    max_price = 0
    
    if df_raw is not None:
        df_clean = clean_data(df_raw)
        total_laptops = len(df_clean)
        total_brands = df_clean['brand'].nunique()
        avg_price = df_clean['price'].mean()
        max_price = df_clean['price'].max()
        
    return render_template('index.html', 
                           total_laptops=total_laptops,
                           total_brands=total_brands,
                           avg_price=avg_price,
                           max_price=max_price)

@app.route('/laptops')
def laptops():
    df_raw = load_data('data/laptops.csv')
    if df_raw is not None:
        df_clean = clean_data(df_raw)
        laptops_data = df_clean.to_dict(orient='records')
    else:
        laptops_data = []
        
    return render_template('laptops.html', laptops=laptops_data)

@app.route('/api/laptops')
def api_laptops():
    df_raw = load_data('data/laptops.csv')
    if df_raw is not None:
        df_clean = clean_data(df_raw)
        return jsonify({
            'status': 'success',
            'total': len(df_clean),
            'data': df_clean.to_dict(orient='records')
        })
    return jsonify({'status': 'error', 'message': 'Dataset not found'}), 404


# --------------------------------------------------------------------------------------
# PHẦN 3: PHÂN CỤM LAPTOP K-MEANS & TRỰC QUAN HÓA PCA
# --------------------------------------------------------------------------------------
@app.route('/clustering')
def clustering():
    # Đọc dữ liệu phân cụm
    csv_file = 'results_clustered.csv' if os.path.exists('results_clustered.csv') else 'results.csv'
    if not os.path.exists(csv_file):
        return "Vui lòng chạy 'python part3_clustering.py' trước để sinh kết quả phân cụm!", 404

    df = pd.read_csv(csv_file)
    if 'Cluster' not in df.columns:
        # Nếu chưa phân cụm, gán mặc định
        df['Cluster'] = 0
        df['Cluster_Name'] = 'Phân khúc chung'

    feature_cols = ['DiemCPU', 'DiemGPU', 'RAM', 'DungLuongLuuTru', 'KichThuocManHinh', 'TanSoQuet', 'KhoiLuong', 'Pin', 'GiaBan']
    colors = ['primary', 'danger', 'success', 'warning', 'info']

    cluster_stats = []
    for c_id in sorted(df['Cluster'].unique()):
        sub = df[df['Cluster'] == c_id]
        c_name = sub['Cluster_Name'].iloc[0] if 'Cluster_Name' in sub.columns else f"Cụm {c_id}"
        stats = {
            'id': c_id,
            'name': c_name,
            'badge_color': colors[c_id % len(colors)],
            'count': len(sub),
            'GiaBan': sub['GiaBan'].mean(),
            'DiemCPU': sub['DiemCPU'].mean(),
            'DiemGPU': sub['DiemGPU'].mean(),
            'RAM': sub['RAM'].mean(),
            'DungLuongLuuTru': sub['DungLuongLuuTru'].mean(),
            'KhoiLuong': sub['KhoiLuong'].mean(),
            'samples': sub['TenLaptop'].head(2).tolist(),
            'laptops': sub.to_dict(orient='records')
        }
        cluster_stats.append(stats)

    # Sắp xếp toàn bộ 225 máy theo từng Cụm (hết Cụm 0 đến Cụm 1 rồi Cụm 2)
    df_sorted = df.sort_values(by=['Cluster', 'GiaBan'], ascending=[True, True])
    df_sorted['badge_color'] = df_sorted['Cluster'].apply(lambda x: colors[int(x) % len(colors)])
    all_clustered_laptops = df_sorted.to_dict(orient='records')

    return render_template(
        'clustering.html',
        cluster_stats=cluster_stats,
        all_clustered_laptops=all_clustered_laptops,
        total_count=len(all_clustered_laptops),
        cache_id=int(time.time())
    )


# --------------------------------------------------------------------------------------
# PHẦN 3: SO SÁNH TRỰC QUAN HAI LAPTOP BẰNG BIỂU ĐỒ RADAR
# --------------------------------------------------------------------------------------
@app.route('/radar')
def radar():
    csv_file = 'results.csv' if os.path.exists('results.csv') else 'data/laptops.csv'
    if not os.path.exists(csv_file):
        return "Không tìm thấy file results.csv!", 404

    df = pd.read_csv(csv_file)
    if 'TenLaptop' not in df.columns and 'name' in df.columns:
        df = df.rename(columns={'name': 'TenLaptop', 'price': 'GiaBan', 'cpu_score': 'DiemCPU', 'gpu_score': 'DiemGPU', 'ram': 'RAM', 'battery': 'Pin', 'weight': 'KhoiLuong'})

    all_laptops = df['TenLaptop'].dropna().unique().tolist()
    available_attributes = ['DiemCPU', 'DiemGPU', 'RAM', 'DungLuongLuuTru', 'KichThuocManHinh', 'TanSoQuet', 'KhoiLuong', 'Pin', 'GiaBan']

    # Lấy tham số truy vấn từ Web form
    selected_p1 = request.args.get('p1') or (all_laptops[0] if all_laptops else "")
    selected_p2 = request.args.get('p2') or (all_laptops[10] if len(all_laptops) > 10 else (all_laptops[1] if len(all_laptops) > 1 else ""))
    
    selected_attrs = request.args.getlist('attrs')
    if not selected_attrs:
        selected_attrs = ['DiemCPU', 'DiemGPU', 'RAM', 'Pin', 'GiaBan']
    # Giữ lại các thuộc tính hợp lệ
    selected_attrs = [a for a in selected_attrs if a in available_attributes]
    if len(selected_attrs) < 3:
        selected_attrs = ['DiemCPU', 'DiemGPU', 'RAM', 'Pin', 'GiaBan']

    # Lọc 2 máy
    row1 = df[df['TenLaptop'] == selected_p1]
    row2 = df[df['TenLaptop'] == selected_p2]

    if len(row1) == 0:
        row1 = df.iloc[[0]]
        selected_p1 = row1.iloc[0]['TenLaptop']
    if len(row2) == 0:
        row2 = df.iloc[[1]]
        selected_p2 = row2.iloc[0]['TenLaptop']

    lap1_data = row1.iloc[0]
    lap2_data = row2.iloc[0]

    # Chuẩn hóa MinMaxScaler trên toàn bộ tập dữ liệu đối với các thuộc tính chọn
    scaler = MinMaxScaler()
    df_norm = df.copy()
    df_norm[selected_attrs] = scaler.fit_transform(df[selected_attrs])

    norm1 = df_norm.loc[row1.index[0], selected_attrs].tolist()
    norm2 = df_norm.loc[row2.index[0], selected_attrs].tolist()

    # Vẽ biểu đồ Radar bằng matplotlib
    num_vars = len(selected_attrs)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles_plot = angles + angles[:1]
    norm1_plot = norm1 + norm1[:1]
    norm2_plot = norm2 + norm2[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    plt.xticks(angles, selected_attrs, size=11, fontweight='bold', color='#222')
    plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0 (Max)"], color="grey", size=8)
    plt.ylim(0, 1.1)

    # Đường máy 1
    ax.plot(angles_plot, norm1_plot, color='#1f77b4', linewidth=2.5, label=f"1. {selected_p1}")
    ax.fill(angles_plot, norm1_plot, color='#1f77b4', alpha=0.25)
    ax.scatter(angles, norm1, color='#1f77b4', s=50)

    # Đường máy 2
    ax.plot(angles_plot, norm2_plot, color='#d62728', linewidth=2.5, label=f"2. {selected_p2}")
    ax.fill(angles_plot, norm2_plot, color='#d62728', alpha=0.25)
    ax.scatter(angles, norm2, color='#d62728', s=50)

    plt.title(f"SO SÁNH CẤU HÌNH BIỂU ĐỒ RADAR (MINMAXSCALER [0, 1])", size=13, fontweight='bold', pad=20)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.06), ncol=1, frameon=True, fontsize=9)
    plt.tight_layout()

    # Lưu ra static/images/radar_comparison.png
    os.makedirs('static/images', exist_ok=True)
    img_path = 'static/images/radar_comparison.png'
    plt.savefig(img_path, dpi=200, bbox_inches='tight')
    plt.close()

    # Bảng đối chiếu số liệu
    unit_map = {
        'DiemCPU': 'Điểm PassMark',
        'DiemGPU': 'Điểm G3D Mark',
        'RAM': 'GB',
        'DungLuongLuuTru': 'GB SSD',
        'KichThuocManHinh': 'Inch',
        'TanSoQuet': 'Hz',
        'KhoiLuong': 'kg',
        'Pin': 'Wh',
        'GiaBan': 'VNĐ'
    }

    comparison_rows = []
    for i, attr in enumerate(selected_attrs):
        v1 = lap1_data[attr]
        v2 = lap2_data[attr]
        display1 = f"{v1:,.0f} đ" if 'Gia' in attr else f"{v1}"
        display2 = f"{v2:,.0f} đ" if 'Gia' in attr else f"{v2}"
        comparison_rows.append({
            'attr': attr,
            'val1_display': display1,
            'val1_norm': f"{norm1[i]:.2f}",
            'val2_display': display2,
            'val2_norm': f"{norm2[i]:.2f}",
            'unit': unit_map.get(attr, '')
        })

    return render_template(
        'radar.html',
        all_laptops=all_laptops,
        selected_p1=selected_p1,
        selected_p2=selected_p2,
        available_attributes=available_attributes,
        selected_attrs=selected_attrs,
        comparison_rows=comparison_rows,
        cache_id=int(time.time())
    )


if __name__ == '__main__':
    # Chạy Web Server ở debug mode
    print("Khởi động server Laptops tại http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)
