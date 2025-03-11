import bcrypt
import re
import pymysql # type: ignore
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_file # type: ignore
from flask_cors import CORS  # Import flask-cors


app = Flask(__name__)

CORS(app)  # Cho phép frontend gọi API

# Kết nối MySQL
def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='', # Nhập password MySQL vào đây
        database='QuanLyKhachSan',
        cursorclass=pymysql.cursors.DictCursor
        )
    
# API lấy danh sách hóa đơn
@app.route('/api/invoices', methods=['GET'])
def get_invoices():
     conn = get_db_connection()
     cursor = conn.cursor()
     cursor.execute("SELECT * FROM HoaDon")
     invoices = cursor.fetchall()
     conn.close()
     return jsonify(invoices)
 
 
 # API thêm hóa đơn
@app.route('/api/invoices', methods=['POST'])
def add_invoice():
     data = request.json
     conn = get_db_connection()
     cursor = conn.cursor()
     sql = ("INSERT INTO HoaDon (MaHoaDon, MaSDDV, NgayLapHoaDon, TongTien) VALUES (%s, %s, %s, %s)")
     cursor.execute(sql, (data['MaHoaDon'], data['MaSDDV'], data['NgayLapHoaDon'], data['TongTien']))
     conn.commit()
     conn.close()
     return jsonify({'message': 'Thêm hóa đơn thành công'})
 
 # # API sửa hóa đơn
@app.route("/api/invoices/<id>", methods=["PUT"])
def update_invoice(id):
     try:
         data = request.get_json()
         conn = get_db_connection()  # Lấy kết nối MySQL
         cursor = conn.cursor()
 
         sql = """
             UPDATE HoaDon 
             SET MaSDDV = %s, NgayLapHoaDon = %s, TongTien = %s 
             WHERE MaHoaDon = %s
         """
         cursor.execute(sql, (data["MaSDDV"], data["NgayLapHoaDon"], data["TongTien"], id))
         conn.commit()
         conn.close()
 
         return jsonify({"message": "Cập nhật thành công!"}), 200
     except Exception as e:
         return jsonify({"error": str(e)}), 500
 
 # API xóa hóa đơn
@app.route('/api/invoices/<string:MaHoaDon>', methods=['DELETE'])
def delete_invoice(MaHoaDon):
     conn = get_db_connection()
     cursor = conn.cursor()
     sql = "DELETE FROM HoaDon WHERE MaHoaDon=%s"
     cursor.execute(sql, (MaHoaDon,))
     conn.commit()
     conn.close()
     return jsonify({'message': 'Xóa hóa đơn thành công'})
 
 # API xuất Excel
@app.route('/api/export-excel', methods=['GET'])
def export_excel():
     conn = get_db_connection()
     df = pd.read_sql("SELECT * FROM HoaDon", conn)
     conn.close()
     excel_path = "hoa_don.xlsx"
     df.to_excel(excel_path, index=False)
     return send_file(excel_path, as_attachment=True)
 
 # Giao diện trang hóa đơn
@app.route('/hoadon')
def hoadon():
    return render_template('../frontend/hoadon.html')

# API thống kê doanh thu
def thong_ke_doanh_thu(loai_thong_ke):
    query = """
        SELECT 
            CASE 
                WHEN %s = 'ngay' THEN DATE(NgayLapHoaDon)
                WHEN %s = 'tuan' THEN YEARWEEK(NgayLapHoaDon)
                WHEN %s = 'thang' THEN DATE_FORMAT(NgayLapHoaDon, '%%Y-%%m')
            END AS ThoiGian,
            SUM(TongTien) AS TongDoanhThu
        FROM HoaDon
        GROUP BY ThoiGian;
    """
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, (loai_thong_ke, loai_thong_ke, loai_thong_ke))
        result = cursor.fetchall()
    conn.close()
    return result

# API lấy danh sách khách hàng
@app.route('/api/customers', methods=['GET'])
def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM KhachHang")
    customers = cursor.fetchall()
    conn.close()
    return jsonify(customers)


# API thêm khách hàng
@app.route('/api/customers', methods=['POST'])
def add_customers():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = ("INSERT INTO KhachHang (MaKhachHang, TenKhachHang, DiaChi, SoDienThoai) VALUES (%s, %s, %s, %s)")
    cursor.execute(sql, (data['MaKhachHang'], data['TenKhachHang'], data['DiaChi'], data['SoDienThoai']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Thêm khách hànghàng thành công'})

# # API sửa khách hàng
@app.route("/api/customers/<id>", methods=["PUT"])
def update_customers(id):
    try:
        data = request.get_json()
        conn = get_db_connection()  # Lấy kết nối MySQL
        cursor = conn.cursor()

        sql = """
            UPDATE KhachHang
            SET TenKhachHang = %s, DiaChi = %s, SoDienThoai = %s 
            WHERE MaKhachHang = %s
        """
        cursor.execute(sql, (data["TenKhachHang"], data["DiaChi"], data["SoDienThoai"], id))
        conn.commit()
        conn.close()

        return jsonify({"message": "Cập nhật thành công!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API xóa khách hàng
@app.route('/api/customers/<string:MaKhachHang>', methods=['DELETE'])
def delete_customers(MaKhachHang):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM KhachHang WHERE MaKhachHang=%s"
    cursor.execute(sql, (MaKhachHang,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Xóa khách hànghàng thành công'})

# API xuất Excel
@app.route('/api/export_customers_excel', methods=['GET'])
def export_customers_excel():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM KhachHang", conn)
    conn.close()
    excel_path = "khach_hang.xlsx"
    df.to_excel(excel_path, index=False)
    return send_file(excel_path, as_attachment=True)

# Giao diện trang khách hàng
@app.route('/khachhang')
def khachhang():
    return render_template('../frontend/khachhang.html')


# API trả dữ liệu JSON
@app.route('/api/thongke', methods=['GET'])
def api_thong_ke():
    loai_thong_ke = request.args.get('loai', 'thang')  # Mặc định là theo tháng
    data = thong_ke_doanh_thu(loai_thong_ke)
    return jsonify(data)

@app.route('/', methods=['GET'])
def trangchu_page():
    return render_template('../frontend/trangchu.html')

# API lấy danh sách nhân viên
@app.route('/api/staffs', methods=['GET'])
def get_staffs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM NhanVien")
    staffs = cursor.fetchall()
    conn.close()
    return jsonify(staffs)


# API thêm nhân viên
@app.route('/api/staffs', methods=['POST'])
def add_staffs():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = ("INSERT INTO NhanVien (MaNhanVien, HoTen, NgaySinh, SoDienThoai) VALUES (%s, %s, %s, %s)")
    cursor.execute(sql, (data['MaNhanVien'], data['HoTen'], data['NgaySinh'], data['SoDienThoai']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Thêm nhân viên thành công'})

# # API sửa nhân viên
@app.route("/api/staffs/<id>", methods=["PUT"])
def update_staffs(id):
    try:
        data = request.get_json()
        conn = get_db_connection()  # Lấy kết nối MySQL
        cursor = conn.cursor()

        sql = """
            UPDATE NhanVien
            SET HoTen = %s, NgaySinh = %s, SoDienThoai = %s 
            WHERE MaNhanVien = %s
        """
        cursor.execute(sql, (data["HoTen"], data["NgaySinh"], data["SoDienThoai"], id))
        conn.commit()
        conn.close()

        return jsonify({"message": "Cập nhật thành công!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API xóa nhân viên
@app.route('/api/staffs/<string:MaNhanVien>', methods=['DELETE'])
def delete_staffs(MaNhanVien):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM NhanVien WHERE MaNhanVien=%s"
    cursor.execute(sql, (MaNhanVien,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Xóa nhân viên thành công'})

# API xuất Excel
@app.route('/api/export_staffs_excel', methods=['GET'])
def export_staffs_excel():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM NhanVien", conn)
    conn.close()
    excel_path = "nhan_vien.xlsx"
    df.to_excel(excel_path, index=False)
    return send_file(excel_path, as_attachment=True)

# Giao diện trang nhân viên
@app.route('/nhanvien')
def nhanvien():
    return render_template('../frontend/nhanvien.html')

@app.route('/thongke', methods=['GET'])
def thongke_page():
    return render_template('../frontend/thongke.html')

# Hàm hash mật khẩu
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Hàm kiểm tra mật khẩu
def check_password(input_password, hashed_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password.encode('utf-8'))

# API đăng nhập 
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Vui lòng nhập đủ thông tin!"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            user_id, db_username, db_password = user["id"], user["username"], user["password"]

            # 🛠 FIX: Chuyển password về bytes trước khi check
            if check_password(password, db_password):
                return jsonify({"success": True, "message": "Đăng nhập thành công!", "user": {"id": user_id, "username": db_username}})
            else:
                return jsonify({"success": False, "message": "Sai mật khẩu!"}), 401

        return jsonify({"success": False, "message": "Sai tên đăng nhập hoặc mật khẩu!"}), 401

    except pymysql.MySQLError as err:
        return jsonify({"success": False, "message": str(err)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

            
            
# API Đăng Ký
@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.json
        fullname = data.get("fullname", "").strip()
        email = data.get("email", "").strip()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        confirm_password = data.get("confirmPassword", "").strip()

        if not fullname or not email or not username or not password or not confirm_password:
            return jsonify({"success": False, "message": "⚠️ Vui lòng nhập đầy đủ thông tin!"}), 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"success": False, "message": "⚠️ Email không hợp lệ!"}), 400

        if len(password) < 6:
            return jsonify({"success": False, "message": "⚠️ Mật khẩu phải có ít nhất 6 ký tự!"}), 400

        if password != confirm_password:
            return jsonify({"success": False, "message": "⚠️ Mật khẩu xác nhận không khớp!"}), 400

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                return jsonify({"success": False, "message": "⚠️ Tên đăng nhập hoặc email đã tồn tại!"}), 400

            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO users (fullname, email, username, password) VALUES (%s, %s, %s, %s)",
                (fullname, email, username, hashed_password)
            )
            conn.commit()

        return jsonify({"success": True, "message": "🎉 Đăng ký thành công!"}), 201

    except Exception as e:
        return jsonify({"success": False, "message": f"❌ Lỗi server: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)
