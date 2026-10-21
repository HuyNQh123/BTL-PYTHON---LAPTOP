import os
import sys
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Thiết lập thư mục và font cho biểu đồ
os.makedirs('charts', exist_ok=True)
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False

# 1. Đọc dữ liệu
df = pd.read_csv('data/laptops.csv')

# Các thông số định lượng cần phân tích
num_cols = [
    'price', 'ram', 'storage', 'cpu_score', 
    'gpu_score', 'screen_size', 'refresh_rate', 
    'weight', 'battery'
]

# Chuyển đổi sang số, N/a hoặc chuỗi lỗi sẽ thành NaN
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# --- 2. Tìm Top 3 cao nhất và thấp nhất theo từng thông số ---
print("=== TOP 3 CAO NHẤT VÀ THẤP NHẤT THEO TỪNG THÔNG SỐ ===")
top_bottom_results = {}
for col in num_cols:
    valid_df = df.dropna(subset=[col])
    top3 = valid_df.nlargest(3, col)[['name', 'brand', col]]
    bottom3 = valid_df.nsmallest(3, col)[['name', 'brand', col]]
    top_bottom_results[col] = {'top3': top3, 'bottom3': bottom3}
    print(f"\n--- {col.upper()} ---")
    print("Top 3 cao nhất:")
    for idx, row in top3.iterrows():
        print(f"  + {row['name']} ({row['brand']}): {row[col]}")
    print("Top 3 thấp nhất:")
    for idx, row in bottom3.iterrows():
        print(f"  + {row['name']} ({row['brand']}): {row[col]}")

# --- 3. Tính toán Trung bình, Trung vị, Độ lệch chuẩn bằng Split-Apply-Combine (Pandas) ---
from src.data_cleaning import compute_split_apply_combine, find_best_value_laptops, export_to_csv

# Split-Apply-Combine thay thế toàn bộ vòng lặp for lồng nhau
stats_records = compute_split_apply_combine(df, num_cols)
results_df = pd.DataFrame(stats_records)
print("\n[V] Đã tính toán thống kê bằng Split-Apply-Combine và lưu vào laptop_results.csv")

# Kỹ thuật 2: Tìm Laptop Món Hời (Best Value by Z-Score)
best_value_top3 = find_best_value_laptops(df, top_n=3)
print("\n=== TOP 3 LAPTOP MÓN HỜI NHẤT (BEST VALUE / Z-SCORE) ===")
for i, item in enumerate(best_value_top3, 1):
    print(f"  {i}. {item['name']} ({item['brand']}) - Giá: {item['price']:,.0f} VND - Điểm CPU: {item['cpu_score']} - Value Score: {item['value_score']}")

# --- 4. Vẽ biểu đồ Phân tích Trực quan ---
print("\n[V] Đang vẽ biểu đồ trực quan...")
os.makedirs('charts', exist_ok=True)
os.makedirs('static/charts', exist_ok=True)

# Cấu hình chi tiết nhãn và đơn vị đo cho từng thông số
COL_META = {
    'price': {'label': 'Giá bán (triệu VNĐ)', 'unit': 'triệu VNĐ', 'scale': 1e-6, 'decimals': 1},
    'ram': {'label': 'Dung lượng RAM (GB)', 'unit': 'GB', 'scale': 1, 'decimals': 0},
    'storage': {'label': 'Dung lượng ổ cứng (GB)', 'unit': 'GB', 'scale': 1, 'decimals': 0},
    'cpu_score': {'label': 'Điểm hiệu năng CPU', 'unit': 'điểm', 'scale': 1, 'decimals': 0},
    'gpu_score': {'label': 'Điểm hiệu năng GPU', 'unit': 'điểm', 'scale': 1, 'decimals': 0},
    'screen_size': {'label': 'Kích thước màn hình (inch)', 'unit': 'inch', 'scale': 1, 'decimals': 1},
    'refresh_rate': {'label': 'Tần số quét (Hz)', 'unit': 'Hz', 'scale': 1, 'decimals': 0},
    'weight': {'label': 'Trọng lượng (kg)', 'unit': 'kg', 'scale': 1, 'decimals': 2},
    'battery': {'label': 'Dung lượng pin (Wh)', 'unit': 'Wh', 'scale': 1, 'decimals': 0}
}

# A. Biểu đồ Phân bố toàn thị trường (Histogram + KDE + Vạch mốc Mean & Median)
for col in num_cols:
    meta = COL_META.get(col, {'label': col, 'unit': '', 'scale': 1, 'decimals': 1})
    s = df[col].dropna() * meta['scale']
    
    mean_val = s.mean()
    median_val = s.median()
    
    plt.figure(figsize=(9, 5.2))
    sns.histplot(s, kde=True, bins=15, color='#2563eb', edgecolor='black', alpha=0.55)
    
    # Đường tham chiếu Mean & Median
    plt.axvline(mean_val, color='#dc2626', linestyle='--', linewidth=2, 
                label=f'Trung bình (Mean): {mean_val:.{meta["decimals"]}f} {meta["unit"]}')
    plt.axvline(median_val, color='#16a34a', linestyle='-', linewidth=2, 
                label=f'Trung vị (Median): {median_val:.{meta["decimals"]}f} {meta["unit"]}')
    
    plt.title(f'Phân bố toàn thị trường: {meta["label"]}', fontsize=13, fontweight='bold', pad=12)
    plt.xlabel(meta['label'], fontsize=11, fontweight='600')
    plt.ylabel('Số lượng laptop', fontsize=11, fontweight='600')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper right', fontsize=10)
    plt.tight_layout()
    
    plt.savefig(f'charts/hist_overall_{col}.png', dpi=150)
    plt.savefig(f'static/charts/hist_overall_{col}.png', dpi=150)
    plt.close()

# B. Histogram phân bố theo từng hãng (Dạng lưới Subplots riêng biệt từng hãng - Chuẩn 100% đề bài)
for col in num_cols:
    meta = COL_META.get(col, {'label': col, 'unit': '', 'scale': 1, 'decimals': 1})
    plot_df = df.dropna(subset=[col, 'brand']).copy()
    plot_df[col] = plot_df[col] * meta['scale']
    
    # Lọc hãng có ít nhất 2 sản phẩm để vẽ phân bố
    brand_counts = plot_df['brand'].value_counts()
    valid_brands = brand_counts[brand_counts >= 2].index
    plot_df = plot_df[plot_df['brand'].isin(valid_brands)]
    
    # Sắp xếp các hãng theo Trung vị giảm dần
    brand_order = plot_df.groupby('brand')[col].median().sort_values(ascending=False).index.tolist()
    
    n_brands = len(brand_order)
    ncols = 3
    nrows = math.ceil(n_brands / ncols)
    
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, nrows * 3.2), sharex=True)
    axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
    
    palette = sns.color_palette('tab10', n_brands)
    
    for i, b in enumerate(brand_order):
        ax = axes[i]
        data_b = plot_df[plot_df['brand'] == b][col]
        mean_b = data_b.mean()
        median_b = data_b.median()
        
        # Vẽ Histogram kèm đường cong KDE cho từng hãng
        sns.histplot(data_b, kde=True, ax=ax, color=palette[i % len(palette)], edgecolor='black', alpha=0.55)
        ax.axvline(mean_b, color='#dc2626', linestyle='--', linewidth=1.5, label=f'Mean: {mean_b:.{meta["decimals"]}f}')
        ax.axvline(median_b, color='#16a34a', linestyle='-', linewidth=1.5, label=f'Median: {median_b:.{meta["decimals"]}f}')
        
        ax.set_title(f'Hãng: {b} ({len(data_b)} sản phẩm)', fontsize=11, fontweight='bold')
        ax.set_xlabel(meta['label'] if i >= n_brands - ncols else '', fontsize=10)
        ax.set_ylabel('Số máy', fontsize=9)
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Ẩn các ô trống thừa trong lưới
    for j in range(n_brands, len(axes)):
        fig.delaxes(axes[j])
        
    fig.suptitle(f'Phân bố Histogram theo từng hãng: {meta["label"]}', fontsize=14, fontweight='bold', y=1.002)
    plt.tight_layout()
    plt.savefig(f'charts/hist_by_brand_{col}.png', dpi=150, bbox_inches='tight')
    plt.savefig(f'static/charts/hist_by_brand_{col}.png', dpi=150, bbox_inches='tight')
    plt.close()

print("[V] Đã tạo xong toàn bộ biểu đồ tối ưu trong thư mục charts/ và static/charts/")

# --- 5. Xác định hãng đứng cao nhất theo từng thông số ---
print("\n=== HÃNG ĐỨNG CAO NHẤT THEO TỪNG THÔNG SỐ (XÉT THEO GIÁ TRỊ TRUNG BÌNH) ===")
brand_only_df = results_df[results_df['brand'] != 'Toàn bộ']
for col in num_cols:
    col_stat = brand_only_df[brand_only_df['feature'] == col].dropna(subset=['mean'])
    top_brand = col_stat.loc[col_stat['mean'].idxmax()]
    print(f"- {col}: {top_brand['brand']} (Mean: {top_brand['mean']:.2f}, Median: {top_brand['median']:.2f})")
