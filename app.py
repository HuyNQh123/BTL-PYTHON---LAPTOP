from flask import Flask, render_template, request, jsonify, send_file
import sys
import os
import math
import numpy as np
import pandas as pd

# Cho phép Python tìm thấy thư mục src
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from src.data_cleaning import (
    load_data, clean_data, compute_split_apply_combine,
    find_best_value_laptops, export_to_csv
)
from src.database import init_db, search_laptops_db

app = Flask(__name__)

# Các thông số định lượng cần phân tích
NUM_COLS = [
    'price', 'ram', 'storage', 'cpu_score',
    'gpu_score', 'screen_size', 'refresh_rate',
    'weight', 'battery'
]

# Nhãn tiếng Việt cho mỗi thông số
COL_LABELS = {
    'price': 'Giá bán (VND)',
    'ram': 'RAM (GB)',
    'storage': 'Ổ cứng (GB)',
    'cpu_score': 'Điểm CPU',
    'gpu_score': 'Điểm GPU',
    'screen_size': 'Màn hình (inch)',
    'refresh_rate': 'Tần số quét (Hz)',
    'weight': 'Trọng lượng (kg)',
    'battery': 'Pin (Wh)'
}


def _safe_float(val):
    """Chuyển numpy float/int sang Python float, NaN -> None."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    try:
        f = float(val)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None


def compute_eda(df):
    """
    Tính toán toàn bộ EDA kết hợp các kỹ thuật nâng cao:
    - Kỹ thuật 1: Split-Apply-Combine với Pandas (thay thế vòng lặp thủ công).
    - Kỹ thuật 2: Thuật toán Z-Score tìm Laptop Món Hời.
    - Kỹ thuật 3: Phân cụm K-Means & Silhouette Score.
    """
    # Đảm bảo các cột là kiểu số
    for col in NUM_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- TOP 3 cao nhất / thấp nhất ---
    top_bottom = {}
    for col in NUM_COLS:
        valid = df.dropna(subset=[col])
        top3 = valid.nlargest(3, col)[['name', 'brand', col]].to_dict('records')
        bottom3 = valid.nsmallest(3, col)[['name', 'brand', col]].to_dict('records')
        for item in top3 + bottom3:
            item[col] = _safe_float(item[col])
        top_bottom[col] = {'top3': top3, 'bottom3': bottom3}

    # =========================================================================
    # KỸ THUẬT 1: Tối ưu hóa tính toán bằng Split-Apply-Combine (Pandas)
    # Không dùng vòng lặp for lồng nhau.
    # =========================================================================
    stats_rows = compute_split_apply_combine(df, NUM_COLS)

    # Đảm bảo các giá trị trong stats_rows là an toàn (Python native float)
    for r in stats_rows:
        r['mean'] = _safe_float(r['mean'])
        r['median'] = _safe_float(r['median'])
        r['std'] = _safe_float(r['std'])
        r['count'] = int(r['count']) if r['count'] is not None and not math.isnan(r['count']) else 0

    brands = sorted([b for b in df['brand'].dropna().unique()])

    # --- Hãng dẫn đầu từng thông số ---
    leaders = {}
    brand_only = [r for r in stats_rows if r['brand'] != 'Toàn bộ']
    for col in NUM_COLS:
        col_rows = [r for r in brand_only if r['feature'] == col and r['mean'] is not None]
        if col_rows:
            best = max(col_rows, key=lambda x: x['mean'])
            leaders[col] = {
                'brand': best['brand'],
                'mean': best['mean'],
                'median': best['median']
            }

    # --- Đánh giá & nhận xét tổng hợp ---
    brand_lead_count = {}
    for col, info in leaders.items():
        b = info['brand']
        brand_lead_count[b] = brand_lead_count.get(b, 0) + 1
    brand_lead_sorted = sorted(brand_lead_count.items(), key=lambda x: -x[1])

    price_stats_by_brand = {}
    for r in brand_only:
        if r['feature'] == 'price' and r['mean'] is not None:
            price_stats_by_brand[r['brand']] = {
                'mean': r['mean'], 'median': r['median'], 'std': r['std']
            }

    sorted_by_price_mean = sorted(price_stats_by_brand.items(), key=lambda x: x[1]['mean'])
    sorted_by_price_std = sorted(
        [(b, v) for b, v in price_stats_by_brand.items() if v['std'] is not None],
        key=lambda x: x[1]['std'], reverse=True
    )

    evaluation = {
        'brand_lead_count': brand_lead_sorted,
        'total_criteria': len(NUM_COLS),
        'price_ranking': [
            {'brand': b, 'mean': v['mean'], 'median': v['median'], 'std': v['std']}
            for b, v in sorted_by_price_mean
        ],
        'most_diverse': sorted_by_price_std[0] if sorted_by_price_std else None,
        'premium_brands': [b for b, v in sorted_by_price_mean if v['mean'] and v['mean'] >= 35_000_000],
        'budget_brands': [b for b, v in sorted_by_price_mean if v['mean'] and v['mean'] <= 20_000_000],
    }

    # =========================================================================
    # KỸ THUẬT 2: Thuật toán Z-Score tìm "Laptop Món Hời" (Best Price/Performance)
    # =========================================================================
    best_value_laptops = find_best_value_laptops(df, top_n=3)

    return top_bottom, stats_rows, leaders, evaluation, brands, best_value_laptops


# Tự động nạp dữ liệu vào SQLite khi khởi động server
def setup_database_on_start():
    df_raw = load_data('data/laptops.csv')
    if df_raw is not None:
        df_clean = clean_data(df_raw)
        init_db(df_clean)

# Khởi tạo DB
setup_database_on_start()


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
        (
            top_bottom, stats, leaders, evaluation, brands,
            best_value_laptops
        ) = compute_eda(df_clean)
    else:
        laptops_data = []
        top_bottom, stats, leaders, evaluation, brands = {}, [], {}, {}, []
        best_value_laptops = []

    return render_template('laptops.html',
                           laptops=laptops_data,
                           top_bottom=top_bottom,
                           stats=stats,
                           leaders=leaders,
                           evaluation=evaluation,
                           num_cols=NUM_COLS,
                           col_labels=COL_LABELS,
                           brands=brands,
                           best_value_laptops=best_value_laptops)


@app.route('/download/results')
def download_results():
    """KỸ THUẬT 5: Tải file laptop_results.csv đã được xuất chuẩn hóa utf-8-sig."""
    filepath = os.path.join(os.path.dirname(__file__), 'laptop_results.csv')
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name='laptop_results.csv')
    return "File not found", 404


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


@app.route('/api/best-value')
def api_best_value():
    """API trả về Top Laptop Món Hời tính theo Z-Score."""
    df_raw = load_data('data/laptops.csv')
    if df_raw is not None:
        df_clean = clean_data(df_raw)
        best_value = find_best_value_laptops(df_clean, top_n=3)
        return jsonify({'status': 'success', 'data': best_value})
    return jsonify({'status': 'error', 'message': 'Dataset not found'}), 404


# ==============================================================================
# KỸ THUẬT 4: API tìm kiếm Laptop bảo mật chống SQL Injection
# ==============================================================================
@app.route('/api/search')
def api_search():
    """
    Tìm kiếm laptop từ SQLite Database sử dụng Parameterized Query an toàn 100%.
    Tham số: q (từ khóa), brand (hãng), min_price, max_price.
    """
    keyword = request.args.get('q', default='', type=str)
    brand = request.args.get('brand', default='', type=str)
    min_price = request.args.get('min_price', default=None, type=float)
    max_price = request.args.get('max_price', default=None, type=float)

    results = search_laptops_db(
        keyword=keyword,
        brand=brand,
        min_price=min_price,
        max_price=max_price
    )
    return jsonify({
        'status': 'success',
        'query': {
            'q': keyword,
            'brand': brand,
            'min_price': min_price,
            'max_price': max_price
        },
        'total': len(results),
        'data': results
    })


if __name__ == '__main__':
    print("Khởi động server Laptops tại http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)
