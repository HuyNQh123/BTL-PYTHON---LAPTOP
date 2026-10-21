import sys
import os
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def load_data(filepath='data/laptops.csv'):
    """Đọc dữ liệu từ file CSV."""
    try:
        df = pd.read_csv(filepath)
        return df
    except FileNotFoundError:
        print(f"Error: File '{filepath}' không tồn tại.")
        return None


def remove_duplicates(df):
    """Xóa các dòng dữ liệu trùng lặp."""
    initial_rows = len(df)
    df = df.drop_duplicates(keep='first')
    df = df.reset_index(drop=True)
    removed_rows = initial_rows - len(df)
    return df, removed_rows


def normalize_brand(df):
    """Chuẩn hóa tên hãng (Viết hoa chữ cái đầu hoặc viết hoa toàn bộ tùy hãng)."""
    if 'brand' in df.columns:
        df['brand'] = df['brand'].str.strip().str.title()
        df['brand'] = df['brand'].replace({'Hp': 'HP', 'Msi': 'MSI', 'Asus': 'ASUS'})
    return df


def convert_numeric_columns(df):
    """Chuyển đổi các cột có chứa chữ thành số hợp lệ."""
    if 'ram' in df.columns:
        df['ram'] = df['ram'].astype(str).str.replace('GB', '', regex=False).str.strip()
        df['ram'] = pd.to_numeric(df['ram'], errors='coerce')
        
    numeric_cols = [
        'cpu_score', 'gpu_score', 'storage', 'screen_size', 
        'refresh_rate', 'weight', 'battery', 'rating', 'price', 'units_sold'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df


def handle_missing_values(df):
    """Xử lý các giá trị bị thiếu."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())
    
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        df[col] = df[col].fillna("N/a")
        
    return df


def clean_data(df):
    """Hàm tổng hợp để chạy toàn bộ quy trình làm sạch dữ liệu."""
    df, _ = remove_duplicates(df)
    df = normalize_brand(df)
    df = convert_numeric_columns(df)
    df = handle_missing_values(df)
    return df


# ==============================================================================
# KỸ THUẬT 1: Tối ưu hóa tính toán bằng Split-Apply-Combine (Pandas)
# ==============================================================================
def compute_split_apply_combine(df, num_cols):
    """
    Xóa bỏ hoàn toàn vòng lặp lồng thủ công.
    Dùng Split-Apply-Combine (groupby + agg) tính Mean, Median, StdDev, Count trong 1-2 dòng code.
    """
    # 1. Split-Apply-Combine theo từng hãng
    brand_stats_df = df.groupby('brand')[num_cols].agg(['mean', 'median', 'std', 'count']).round(2)
    
    # 2. Thống kê toàn bộ thị trường
    overall_stats_df = df[num_cols].agg(['mean', 'median', 'std', 'count']).round(2).T.reset_index()
    overall_stats_df.rename(columns={'index': 'feature'}, inplace=True)
    overall_stats_df['brand'] = 'Toàn bộ'
    
    # Chuyển đổi DataFrame phân cấp sang dạng bảng phẳng để truyền lên Web & xuất CSV
    brand_flat = brand_stats_df.stack(level=0, future_stack=True).reset_index()
    brand_flat.rename(columns={'level_1': 'feature'}, inplace=True)
    
    full_stats_df = pd.concat([overall_stats_df, brand_flat], ignore_index=True)
    
    # Lưu file kết quả chuẩn hóa (Kỹ thuật 5)
    export_to_csv(full_stats_df, 'laptop_results.csv')
    
    return full_stats_df.to_dict(orient='records')


# ==============================================================================
# KỸ THUẬT 2: Triển khai Z-Score để tìm "Laptop Món Hời" (Best Price/Performance)
# ==============================================================================
def find_best_value_laptops(df, top_n=3):
    """
    Tính Z-Score cho giá (price_z) và hiệu năng (cpu_score_z).
    Công thức: Z = (X - mu) / sigma
    Value_Score = cpu_score_z - price_z (Hiệu năng càng cao, giá càng rẻ thì điểm càng lớn)
    Lọc ra Top N chiếc laptop có Value_Score cao nhất toàn thị trường.
    """
    df_eval = df.dropna(subset=['price', 'cpu_score']).copy()
    
    # Tính mu (mean) và sigma (std)
    p_mean = df_eval['price'].mean()
    p_std = df_eval['price'].std()
    c_mean = df_eval['cpu_score'].mean()
    c_std = df_eval['cpu_score'].std()
    
    # Z-Score
    df_eval['price_z'] = ((df_eval['price'] - p_mean) / (p_std if p_std else 1.0)).round(2)
    df_eval['cpu_score_z'] = ((df_eval['cpu_score'] - c_mean) / (c_std if c_std else 1.0)).round(2)
    
    # Điểm món hời Value_Score
    df_eval['value_score'] = (df_eval['cpu_score_z'] - df_eval['price_z']).round(2)
    
    # Lấy Top N chiếc laptop có Value_Score cao nhất
    top_value = df_eval.sort_values(by='value_score', ascending=False).head(top_n)
    
    return top_value.to_dict(orient='records')





# ==============================================================================
# KỸ THUẬT 5: Chuẩn hóa Export CSV (Chống lỗi Font trên Excel Windows)
# ==============================================================================
def export_to_csv(df, filepath):
    """
    Bảo đảm mọi lệnh xuất CSV đều có:
    - encoding='utf-8-sig' để mở file trên Microsoft Excel Windows không bị lỗi font Tiếng Việt.
    - index=False để không sinh cột số thứ tự thừa.
    """
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    return filepath
