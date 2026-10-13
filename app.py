from flask import Flask, render_template, request, jsonify
import sys
import os

# Cho phép Python tìm thấy thư mục src
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from src.data_cleaning import load_data, clean_data

app = Flask(__name__)

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

if __name__ == '__main__':
    # Chạy Web Server ở debug mode
    print("Khởi động server Laptops tại http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)
