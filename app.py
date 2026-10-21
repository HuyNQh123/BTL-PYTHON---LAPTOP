from flask import Flask, render_template, request, jsonify, flash
import sys
import os

# Cho phép Python tìm thấy thư mục src
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from src.data_cleaning import load_data, clean_data

app = Flask(__name__)
app.secret_key = 'lapinsight-laptops-secret-key-super-secure'

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

# =========================================================================
# PHẦN 4: DỰ ĐOÁN GIÁ LAPTOP & GỢI Ý CẤU HÌNH TƯƠNG ĐỒNG (MACHINE LEARNING)
# =========================================================================

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    Trang web dự đoán giá laptop và tư vấn cấu hình theo ngành học.
    Hỗ trợ cả GET (hiển thị form & chỉ số mô hình) và POST (tính toán giá & gợi ý tương đồng).
    """
    from src.price_prediction import get_trained_model, predict_laptop_price, recommend_similar_laptops
    
    model_payload = get_trained_model()
    model_name = model_payload['model_name']
    active_key = 'rf' if 'Random Forest' in model_name else 'lr'
    
    error = None
    predicted_price = None
    recommendations = []
    form_data = {}
    
    if request.method == 'POST':
        form_data = {
            'cpu_score': request.form.get('cpu_score', '').strip(),
            'gpu_score': request.form.get('gpu_score', '').strip(),
            'ram': request.form.get('ram', '').strip(),
            'storage': request.form.get('storage', '').strip(),
            'screen_size': request.form.get('screen_size', '').strip(),
            'refresh_rate': request.form.get('refresh_rate', '').strip(),
            'weight': request.form.get('weight', '').strip(),
            'battery': request.form.get('battery', '').strip(),
            'rating': request.form.get('rating', '').strip(),
        }
        
        field_names_vi = {
            'cpu_score': 'Điểm hiệu năng CPU',
            'gpu_score': 'Điểm hiệu năng GPU',
            'ram': 'Dung lượng RAM',
            'storage': 'Dung lượng Ổ cứng',
            'screen_size': 'Kích thước màn hình',
            'refresh_rate': 'Tần số quét',
            'weight': 'Trọng lượng',
            'battery': 'Dung lượng pin',
            'rating': 'Điểm đánh giá'
        }
        
        # Validation dữ liệu đầu vào
        try:
            # Kiểm tra xem có trường nào bị để trống không
            for key, val in form_data.items():
                if not val:
                    raise ValueError(f"Vui lòng không để trống trường '{field_names_vi.get(key, key)}'.")
            
            # Chuyển đổi kiểu dữ liệu sang float
            features = {
                'cpu_score': float(form_data['cpu_score']),
                'gpu_score': float(form_data['gpu_score']),
                'ram': float(form_data['ram']),
                'storage': float(form_data['storage']),
                'screen_size': float(form_data['screen_size']),
                'refresh_rate': float(form_data['refresh_rate']),
                'weight': float(form_data['weight']),
                'battery': float(form_data['battery']),
                'rating': float(form_data['rating'])
            }
            
            # Kiểm tra ràng buộc hợp lý
            for key, val in features.items():
                if val <= 0:
                    raise ValueError(f"Giá trị của '{field_names_vi.get(key, key)}' phải lớn hơn 0.")
            
            if features['rating'] > 5.0:
                raise ValueError("Điểm đánh giá (Rating) tối đa là 5.0.")
            if features['screen_size'] > 30.0:
                raise ValueError("Kích thước màn hình không hợp lý (> 30 inch).")
            if features['weight'] > 15.0:
                raise ValueError("Trọng lượng laptop không hợp lý (> 15 kg).")
                
            # Dự đoán giá bằng Machine Learning Pipeline
            predicted_price = predict_laptop_price(features)
            
            # Gợi ý Top 5 mẫu laptop có cấu hình tương tự và chênh lệch khoảng 1-2 triệu VNĐ
            recommendations = recommend_similar_laptops(features, predicted_price, top_n=5)
            
        except ValueError as e:
            error = str(e)
        except Exception as e:
            error = f"Đã xảy ra lỗi trong quá trình tính toán: {str(e)}"
            
    return render_template('predict.html', 
                           model_info=model_payload,
                           active_key=active_key,
                           predicted_price=predicted_price,
                           recommendations=recommendations,
                           form_data=form_data,
                           error=error)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    REST API dự đoán giá laptop từ JSON payload:
    {
        "cpu_score": 18000,
        "gpu_score": 12000,
        "ram": 16,
        "storage": 512,
        "screen_size": 15.6,
        "refresh_rate": 144,
        "weight": 2.1,
        "battery": 70,
        "rating": 4.5
    }
    """
    from src.price_prediction import predict_laptop_price, recommend_similar_laptops
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'status': 'error', 'message': 'Yêu cầu định dạng JSON body'}), 400
        
    required_fields = ['cpu_score', 'gpu_score', 'ram', 'storage', 'screen_size', 'refresh_rate', 'weight', 'battery', 'rating']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({'status': 'error', 'message': f'Thiếu các trường thông số: {", ".join(missing)}'}), 400
        
    try:
        features = {f: float(data[f]) for f in required_fields}
        predicted_price = predict_laptop_price(features)
        recommendations = recommend_similar_laptops(features, predicted_price, top_n=5)
        
        return jsonify({
            'status': 'success',
            'predicted_price': round(predicted_price, 2),
            'predicted_price_formatted': f"{predicted_price:,.0f} đ",
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Chạy Web Server ở debug mode
    print("Khởi động server Laptops tại http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)
