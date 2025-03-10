from flask import Flask, request, jsonify, render_template
import pymysql

app = Flask(__name__)

# Kết nối MySQL
def get_db_connection():
    return pymysql.connect(host='127.0.0.1', user='root', password='123456789', database='QuanLyKhachSan', cursorclass=pymysql.cursors.DictCursor)

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

@app.route('/', methods=['GET'])
def trangchu_page():
    return render_template('trangchu.html')

@app.route('/thongke', methods=['GET'])
def thongke_page():
    return render_template('thongke.html')

if __name__ == '__main__':
    app.run(debug=True)
