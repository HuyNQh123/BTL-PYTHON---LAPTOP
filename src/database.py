import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'laptops.db')

def get_db_connection(db_path=DB_PATH):
    """Tạo kết nối tới SQLite Database."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(df=None, db_path=DB_PATH):
    """
    Khởi tạo bảng laptops và chèn dữ liệu nếu chưa tồn tại.
    Sử dụng Parameterized Query an toàn khi chèn.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS laptops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            cpu TEXT,
            cpu_score INTEGER,
            gpu TEXT,
            gpu_score INTEGER,
            ram INTEGER,
            storage INTEGER,
            screen_size REAL,
            resolution TEXT,
            refresh_rate INTEGER,
            weight REAL,
            battery REAL,
            operating_system TEXT,
            rating REAL,
            price REAL,
            units_sold REAL
        )
    """)
    conn.commit()

    # Kiểm tra nếu bảng chưa có dữ liệu thì chèn từ DataFrame
    cursor.execute("SELECT COUNT(*) FROM laptops")
    count = cursor.fetchone()[0]
    
    if count == 0 and df is not None and not df.empty:
        cols = [
            'name', 'brand', 'cpu', 'cpu_score', 'gpu', 'gpu_score',
            'ram', 'storage', 'screen_size', 'resolution', 'refresh_rate',
            'weight', 'battery', 'operating_system', 'rating', 'price', 'units_sold'
        ]
        # Lọc các cột có sẵn trong DataFrame
        valid_cols = [c for c in cols if c in df.columns]
        placeholders = ', '.join(['?'] * len(valid_cols))
        col_names = ', '.join(valid_cols)
        
        insert_sql = f"INSERT INTO laptops ({col_names}) VALUES ({placeholders})"
        
        # Chuyển đổi dữ liệu và thực thi bằng executemany có tham số hóa
        records = [tuple(row[c] for c in valid_cols) for _, row in df.iterrows()]
        cursor.executemany(insert_sql, records)
        conn.commit()
        
    conn.close()

def search_laptops_db(keyword=None, brand=None, min_price=None, max_price=None, db_path=DB_PATH):
    """
    KỸ THUẬT 4: Bảo mật SQL Injection tuyệt đối bằng Parameterized Query.
    Không nối chuỗi hoặc f-string vào câu lệnh SQL.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    query = "SELECT * FROM laptops WHERE 1=1"
    params = []
    
    # 1. Tìm kiếm theo từ khóa (tên hoặc CPU hoặc GPU)
    if keyword and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query += " AND (name LIKE ? OR brand LIKE ? OR cpu LIKE ? OR gpu LIKE ?)"
        params.extend([kw, kw, kw, kw])
        
    # 2. Lọc theo hãng sản xuất
    if brand and brand.strip() and brand.lower() != 'all':
        query += " AND brand = ?"
        params.append(brand.strip())
        
    # 3. Lọc theo khoảng giá
    if min_price is not None:
        try:
            query += " AND price >= ?"
            params.append(float(min_price))
        except (ValueError, TypeError):
            pass
            
    if max_price is not None:
        try:
            query += " AND price <= ?"
            params.append(float(max_price))
        except (ValueError, TypeError):
            pass
            
    query += " ORDER BY price ASC"
    
    # Thực thi truy vấn với tuple tham số
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    
    # Chuyển đổi sqlite3.Row sang list of dicts
    return [dict(row) for row in rows]
