import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Đảm bảo mã hóa UTF-8 cho stdout trên Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from src.data_cleaning import load_data, clean_data

# Danh sách thuộc tính đầu vào và mục tiêu dự đoán
FEATURE_COLS = [
    'cpu_score',
    'gpu_score',
    'ram',
    'storage',
    'screen_size',
    'refresh_rate',
    'weight',
    'battery',
    'rating'
]
TARGET_COL = 'price'
MODEL_PATH = 'models/laptop_price_model.pkl'

def prepare_data(df):
    """Chuẩn bị tập X (features) và y (target)."""
    X = df[FEATURE_COLS].copy()
    y = df[TARGET_COL].copy()
    return X, y

def train_and_evaluate_models():
    """Huấn luyện và so sánh Linear Regression và Random Forest."""
    df_raw = load_data('data/laptops.csv')
    if df_raw is None:
        raise FileNotFoundError("Không tìm thấy file dataset data/laptops.csv")
        
    df_clean = clean_data(df_raw)
    X, y = prepare_data(df_clean)
    
    # Chia tập train (80%) và test (20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 1. Model Linear Regression (sử dụng Pipeline với StandardScaler)
    lr_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', LinearRegression())
    ])
    lr_pipeline.fit(X_train, y_train)
    lr_pred = lr_pipeline.predict(X_test)
    
    lr_mae = mean_absolute_error(y_test, lr_pred)
    lr_rmse = np.sqrt(mean_squared_error(y_test, lr_pred))
    lr_r2 = r2_score(y_test, lr_pred)
    
    # 2. Model Random Forest Regressor
    rf_pipeline = Pipeline([
        ('model', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    rf_pipeline.fit(X_train, y_train)
    rf_pred = rf_pipeline.predict(X_test)
    
    rf_mae = mean_absolute_error(y_test, rf_pred)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
    rf_r2 = r2_score(y_test, rf_pred)
    
    # Chọn model có R² cao hơn để lưu và phục vụ dự đoán
    if rf_r2 >= lr_r2:
        best_model_name = "Random Forest Regressor"
        best_model = rf_pipeline
    else:
        best_model_name = "Linear Regression"
        best_model = lr_pipeline
        
    # Tạo thư mục models nếu chưa có
    os.makedirs('models', exist_ok=True)
    
    model_payload = {
        'model': best_model,
        'model_name': best_model_name,
        'features': FEATURE_COLS,
        'metrics': {
            'lr': {'mae': lr_mae, 'rmse': lr_rmse, 'r2': lr_r2},
            'rf': {'mae': rf_mae, 'rmse': rf_rmse, 'r2': rf_r2}
        },
        'train_size': len(X_train),
        'test_size': len(X_test),
        'total_size': len(df_clean)
    }
    
    joblib.dump(model_payload, MODEL_PATH)
    print(f"Đã lưu model tốt nhất ({best_model_name}) vào {MODEL_PATH}")
    
    return model_payload

def get_trained_model():
    """Tải model đã huấn luyện từ file .pkl hoặc tự động train nếu chưa có."""
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"Lỗi khi load model ({e}), tiến hành train lại...")
    return train_and_evaluate_models()

def predict_laptop_price(features_dict):
    """
    Dự đoán giá laptop từ dictionary chứa các thông số kỹ thuật.
    Trả về giá dự đoán dạng số float.
    """
    payload = get_trained_model()
    model = payload['model']
    
    # Tạo DataFrame đúng thứ tự các cột features
    input_df = pd.DataFrame([features_dict])[FEATURE_COLS]
    predicted_price = model.predict(input_df)[0]
    return max(0.0, float(predicted_price))

_cached_df_clean = None

def get_cleaned_laptops_data():
    """Lấy dữ liệu laptop đã làm sạch, có lưu cache để tối ưu tốc độ phản hồi web."""
    global _cached_df_clean
    if _cached_df_clean is None:
        df_raw = load_data('data/laptops.csv')
        if df_raw is not None:
            _cached_df_clean = clean_data(df_raw)
    return _cached_df_clean

def recommend_similar_laptops(features_dict, predicted_price, top_n=5, max_price_diff=2_000_000):
    """
    Tìm top_n laptop trong dataset có mức giá chênh lệch trong khoảng +/- 1-2 triệu VND
    so với giá dự đoán, và có cấu hình phần cứng tương đồng nhất với cấu hình người dùng nhập.
    
    Thuật toán:
    1. Tính khoảng cách chênh lệch giá thực tế so với giá dự đoán.
    2. Chuẩn hóa các thông số phần cứng theo độ lệch chuẩn toàn bộ tập dữ liệu (Z-score).
    3. Trọng số hóa các thành phần cốt lõi: CPU (2.5), GPU (2.5), RAM (2.0), Ổ cứng (1.5),
       Màn hình (1.0), Tần số quét (1.0), Trọng lượng (1.0), Dung lượng Pin (1.0).
    4. Ưu tiên các dòng máy trong dải chênh lệch <= max_price_diff (2,000,000 VND).
       Nếu số lượng ứng viên < top_n, mở rộng dần dải chênh lệch để luôn có đủ 5 gợi ý.
    5. Tính tỷ lệ % tương đồng cấu hình (% similarity) và sắp xếp đề xuất theo độ tương đồng.
    """
    df = get_cleaned_laptops_data()
    if df is None or len(df) == 0:
        return []
        
    df = df.copy()
    
    # 1. Tính khoảng cách chênh lệch giá
    df['price_diff'] = df['price'] - predicted_price
    df['abs_price_diff'] = df['price_diff'].abs()
    
    # 2. Trọng số thuộc tính cấu hình
    weights = {
        'cpu_score': 2.5,
        'gpu_score': 2.5,
        'ram': 2.0,
        'storage': 1.5,
        'screen_size': 1.0,
        'refresh_rate': 1.0,
        'weight': 1.0,
        'battery': 1.0
    }
    
    stds = {col: df[col].std() if df[col].std() > 0 else 1.0 for col in weights}
    weighted_sq_diff = 0
    total_w = sum(weights.values())
    for col, w in weights.items():
        user_val = float(features_dict.get(col, 0))
        diff_norm = (df[col] - user_val) / stds[col]
        weighted_sq_diff += w * (diff_norm ** 2)
        
    df['config_dist'] = np.sqrt(weighted_sq_diff / total_w)
    # Quy đổi khoảng cách sang % tương đồng (tiệm cận tự nhiên)
    df['similarity_pct'] = np.clip(100.0 * np.exp(-0.25 * df['config_dist']), 35.0, 99.5).round(1)
    
    # 3. Lọc ứng viên: ưu tiên các mẫu trong dải chênh lệch <= 2,000,000 VND
    candidates = df[df['abs_price_diff'] <= max_price_diff].copy()
    
    # Nếu không đủ top_n mẫu, mở rộng dải giá dần để luôn đảm bảo có đủ gợi ý chất lượng
    if len(candidates) < top_n:
        for ext_diff in [3_000_000, 5_000_000, 8_000_000, 15_000_000]:
            candidates = df[df['abs_price_diff'] <= ext_diff].copy()
            if len(candidates) >= top_n:
                break
                
    if len(candidates) < top_n:
        candidates = df.copy()
        
    # Xếp hạng ứng viên:
    # Điểm phạt phụ trội nếu giá nằm ngoài dải 2 triệu để ưu tiên tối đa các mẫu trong dải +/- 2 triệu
    def rank_score(row):
        price_penalty = max(0.0, (row['abs_price_diff'] - max_price_diff) / 1_000_000.0)
        return row['config_dist'] + price_penalty * 2.5
        
    candidates['rank_score'] = candidates.apply(rank_score, axis=1)
    selected = candidates.sort_values(by='rank_score').head(top_n)
    
    results = []
    for _, row in selected.iterrows():
        diff = float(row['price_diff'])
        diff_str = f"+{diff:,.0f} đ" if diff >= 0 else f"{diff:,.0f} đ"
        
        results.append({
            'name': row['name'],
            'brand': row['brand'],
            'price': float(row['price']),
            'price_diff': diff,
            'price_diff_str': diff_str,
            'abs_price_diff': float(row['abs_price_diff']),
            'cpu': row['cpu'],
            'cpu_score': int(row['cpu_score']),
            'gpu': row['gpu'],
            'gpu_score': int(row['gpu_score']),
            'ram': int(row['ram']),
            'storage': int(row['storage']),
            'screen_size': float(row['screen_size']),
            'resolution': str(row.get('resolution', '')),
            'refresh_rate': int(row['refresh_rate']),
            'weight': float(row['weight']),
            'battery': float(row['battery']),
            'rating': float(row['rating']),
            'similarity_pct': float(row['similarity_pct'])
        })
    return results

if __name__ == '__main__':
    print("--- BẮT ĐẦU TRAINING & ĐÁNH GIÁ MÔ HÌNH DỰ ĐOÁN GIÁ ---")
    results = train_and_evaluate_models()
    
    print("\n--- KẾT QUẢ ĐÁNH GIÁ TRÊN TẬP TEST (20%) ---")
    print(f"Số mẫu Train: {results['train_size']} | Số mẫu Test: {results['test_size']}")
    print("-" * 55)
    print(f"1. Linear Regression:")
    print(f"   - MAE:  {results['metrics']['lr']['mae']:,.2f} VND")
    print(f"   - RMSE: {results['metrics']['lr']['rmse']:,.2f} VND")
    print(f"   - R²:   {results['metrics']['lr']['r2']:.4f}")
    print("-" * 55)
    print(f"2. Random Forest Regressor:")
    print(f"   - MAE:  {results['metrics']['rf']['mae']:,.2f} VND")
    print(f"   - RMSE: {results['metrics']['rf']['rmse']:,.2f} VND")
    print(f"   - R²:   {results['metrics']['rf']['r2']:.4f}")
    print("-" * 55)
    print(f"--> Model được chọn để dự đoán: {results['model_name']}")
    
    # Test thử dự đoán với 1 mẫu
    sample_input = {
        'cpu_score': 18000,
        'gpu_score': 12000,
        'ram': 16,
        'storage': 512,
        'screen_size': 15.6,
        'refresh_rate': 144,
        'weight': 2.1,
        'battery': 70,
        'rating': 4.5
    }
    sample_price = predict_laptop_price(sample_input)
    print(f"\nTest dự đoán cấu hình mẫu: {sample_price:,.0f} VND")
