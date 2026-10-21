import sys
import pandas as pd
import numpy as np

# Đảm bảo mã hóa UTF-8 cho stdout trên Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
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
        # Chuyển tất cả về chữ thường trước, sau đó Title Case
        df['brand'] = df['brand'].str.strip().str.title()
        # Một số hãng có cách viết hoa đặc thù
        brand_map = {
            'Asus': 'ASUS',
            'Hp': 'HP',
            'Msi': 'MSI',
            'Lg': 'LG',
            'Dell': 'Dell',
            'Apple': 'Apple',
            'Lenovo': 'Lenovo',
            'Acer': 'Acer'
        }
        df['brand'] = df['brand'].replace(brand_map)
    return df

def convert_numeric_columns(df):
    """Chuyển đổi kiểu dữ liệu các cột số."""
    numeric_cols = [
        'cpu_score', 'gpu_score', 'ram', 'storage', 
        'screen_size', 'refresh_rate', 'weight', 
        'battery', 'rating', 'price'
    ]
    if 'units_sold' in df.columns:
        numeric_cols.append('units_sold')
        
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

def handle_missing_values(df):
    """Xử lý giá trị khuyết thiếu (NaN)."""
    # Với các cột số: điền bằng median (tránh ảnh hưởng bởi outlier)
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())
        
    # Với các cột dạng chuỗi (text): điền bằng "N/A"
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        df[col] = df[col].fillna("N/a")
        
    return df

def clean_data(df, verbose=False):
    """Hàm tổng hợp để chạy toàn bộ quy trình làm sạch dữ liệu."""
    if verbose:
        print("--- BẮT ĐẦU CLEANING ---")
        print(f"Số dòng ban đầu: {len(df)}")
    
    # 1. Xóa duplicate
    df, removed = remove_duplicates(df)
    if verbose:
        print(f"Đã xóa {removed} dòng duplicate.")
    
    # 2. Chuẩn hóa brand
    df = normalize_brand(df)
    
    # 3. Chuyển kiểu dữ liệu
    df = convert_numeric_columns(df)
    
    # 4. In ra missing values trước khi xử lý
    if verbose:
        print("\nMissing values của từng column (Trước khi xử lý):")
        print(df.isnull().sum())
    
    # 5. Xử lý missing values
    df = handle_missing_values(df)
    
    if verbose:
        print("\nSố dòng sau cleaning:", len(df))
        print("\nData Types:")
        print(df.dtypes)
        print("--- HOÀN THÀNH CLEANING ---")
    
    return df

if __name__ == '__main__':
    # Chạy thử
    df_raw = load_data('data/laptops.csv')
    if df_raw is not None:
        df_clean = clean_data(df_raw, verbose=True)
        print("\n5 laptop đầu tiên sau khi clean:")
        print(df_clean.head())
