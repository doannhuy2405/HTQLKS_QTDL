import bcrypt
import re
import pymysql # type: ignore
from flask import Flask, request, jsonify, render_template # type: ignore
from flask_cors import CORS  # Import flask-cors


app = Flask(__name__)

CORS(app)  # Cho phép frontend gọi API

# Kết nối MySQL
def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='', 
        database='QuanLyKhachSan',
        cursorclass=pymysql.cursors.DictCursor
        )

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

# API trả dữ liệu JSON
@app.route('/api/thongke', methods=['GET'])
def api_thong_ke():
    loai_thong_ke = request.args.get('loai', 'thang')  # Mặc định là theo tháng
    data = thong_ke_doanh_thu(loai_thong_ke)
    return jsonify(data)

# @app.route('/', methods=['GET'])
# def trangchu_page():
#     return render_template('trangchu.html')

@app.route('/thongke', methods=['GET'])
def thongke_page():
    return render_template('thongke.html')

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

    

# # API Đăng Ký
# @app.route("/api/auth/register", methods=["POST"])
# def register():
#     try:
#         data = request.json
#         fullname = data.get("fullname", "").strip()
#         email = data.get("email", "").strip()
#         username = data.get("username", "").strip()
#         password = data.get("password", "").strip()
#         confirm_password = data.get("confirmPassword", "").strip()

#         # ⚠ Kiểm tra dữ liệu đầu vào
#         if not fullname or not email or not username or not password or not confirm_password:
#             return jsonify({"success": False, "message": "⚠️ Vui lòng nhập đầy đủ thông tin!"}), 400

#         if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
#             return jsonify({"success": False, "message": "⚠️ Email không hợp lệ!"}), 400

#         if len(password) < 6:
#             return jsonify({"success": False, "message": "⚠️ Mật khẩu phải có ít nhất 6 ký tự!"}), 400

#         if password != confirm_password:
#             return jsonify({"success": False, "message": "⚠️ Mật khẩu xác nhận không khớp!"}), 400

#         # ✅ Mã hóa mật khẩu SHA-256
#         hashed_password = hashlib.sha256(password.encode()).hexdigest()

#         # 🔗 Kết nối DB
#         conn = get_db_connection()
#         with conn.cursor() as cursor:
#             # ❌ Check username hoặc email có tồn tại không
#             cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
#             if cursor.fetchone():
#                 return jsonify({"success": False, "message": "⚠️ Tên đăng nhập hoặc email đã tồn tại!"}), 400

#             # ✅ Lưu vào DB
#             cursor.execute(
#                 "INSERT INTO users (fullname, email, username, password) VALUES (%s, %s, %s, %s)",
#                 (fullname, email, username, hashed_password)
#             )
#             conn.commit()

#         return jsonify({"success": True, "message": "🎉 Đăng ký thành công!"}), 201

#     except Exception as e:
#         return jsonify({"success": False, "message": f"❌ Lỗi server: {str(e)}"}), 500
#     finally:
#         if 'conn' in locals():
#             conn.close()



if __name__ == '__main__':
    app.run(debug=True)
