CREATE DATABASE QuanLyKhachSan;
USE QuanLyKhachSan;


-- Bảng Loại phòng
CREATE TABLE LoaiPhong (
    MaLoai INT PRIMARY KEY AUTO_INCREMENT,
    TenLoai VARCHAR(50) NOT NULL,
    GiaPhong DECIMAL(10,2) NOT NULL
);

-- Bảng Phòng
CREATE TABLE Phong (
    MaPhong INT PRIMARY KEY AUTO_INCREMENT,
    MaLoai INT,
    SoPhong VARCHAR(10) UNIQUE,
    TrangThai ENUM('Trống', 'Đang sử dụng') NOT NULL,
    FOREIGN KEY (MaLoai) REFERENCES LoaiPhong(MaLoai)
);

-- Bảng Nhân viên
CREATE TABLE NhanVien (
    MaNhanVien INT PRIMARY KEY AUTO_INCREMENT,
    HoTen VARCHAR(100) NOT NULL,
    NgaySinh DATE NOT NULL,
    SoDienThoai VARCHAR(15) UNIQUE NOT NULL
);

-- Bảng Khách hàng
CREATE TABLE KhachHang (
    MaKhachHang INT PRIMARY KEY AUTO_INCREMENT,
    TenKhachHang VARCHAR(100) NOT NULL,
    DiaChi VARCHAR(255),
    SoDienThoai VARCHAR(15) UNIQUE NOT NULL
);

-- Bảng Dịch vụ
CREATE TABLE DichVu (
    MaDichVu INT PRIMARY KEY AUTO_INCREMENT,
    TenDichVu VARCHAR(100) NOT NULL,
    GiaDichVu DECIMAL(10,2) NOT NULL
);

-- Bảng Thuê phòng
CREATE TABLE ThuePhong (
    MaThue INT PRIMARY KEY AUTO_INCREMENT,
    MaKhachHang INT,
    MaPhong INT,
    NgayThue DATE NOT NULL,
    NgayNhan DATE NOT NULL,
    NgayTra DATE NOT NULL,
    TrangThai ENUM('Đã đặt', 'Đang ở', 'Đã trả') NOT NULL,
    FOREIGN KEY (MaKhachHang) REFERENCES KhachHang(MaKhachHang),
    FOREIGN KEY (MaPhong) REFERENCES Phong(MaPhong)
);

-- Bảng Sử dụng dịch vụ
CREATE TABLE SuDungDichVu (
    MaSDDV INT PRIMARY KEY AUTO_INCREMENT,
    MaThue INT,
    MaDichVu INT,
    SoLuong INT NOT NULL,
    NgaySuDung DATE NOT NULL,
    FOREIGN KEY (MaThue) REFERENCES ThuePhong(MaThue),
    FOREIGN KEY (MaDichVu) REFERENCES DichVu(MaDichVu)
);

-- Bảng Hóa đơn
CREATE TABLE HoaDon (
    MaHoaDon INT PRIMARY KEY AUTO_INCREMENT,
    MaSDDV INT,
    NgayLapHoaDon DATE NOT NULL,
    TongTien DECIMAL(15,2) NOT NULL,
    FOREIGN KEY (MaSDDV) REFERENCES SuDungDichVu(MaSDDV)
);

DELIMITER $$
CREATE FUNCTION TinhSoNgayLuuTru(maThue INT) RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE soNgay INT;
    SELECT DATEDIFF(NgayTra, NgayNhan) INTO soNgay
    FROM ThuePhong WHERE MaThue = maThue;
    RETURN soNgay;
END $$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER CapNhatTrangThaiPhong
AFTER INSERT ON ThuePhong
FOR EACH ROW
BEGIN
    UPDATE Phong 
    SET TrangThai = CASE 
        WHEN NEW.TrangThai = 'Đang ở' THEN 'Đang sử dụng'
        ELSE 'Trống'
    END
    WHERE MaPhong = NEW.MaPhong;
END $$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE LayPhongDaDat(IN startDate DATE, IN endDate DATE)
BEGIN
    SELECT Phong.MaPhong, LoaiPhong.TenLoai, Phong.SoPhong, ThuePhong.NgayNhan, ThuePhong.NgayTra
    FROM Phong
    JOIN ThuePhong ON Phong.MaPhong = ThuePhong.MaPhong
    JOIN LoaiPhong ON Phong.MaLoai = LoaiPhong.MaLoai
    WHERE ThuePhong.NgayNhan BETWEEN startDate AND endDate;
END $$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE ThongKeDoanhThu(IN loaiThongKe VARCHAR(10))
BEGIN
SELECT 
        CASE 
            WHEN loaiThongKe = 'ngay' THEN DATE(NgayLapHoaDon)
            WHEN loaiThongKe = 'tuan' THEN YEARWEEK(NgayLapHoaDon)
            WHEN loaiThongKe = 'thang' THEN DATE_FORMAT(NgayLapHoaDon, '%Y-%m')
        END AS ThoiGian,
        SUM(TongTien) AS TongDoanhThu
    FROM HoaDon
    GROUP BY ThoiGian;
END $$
DELIMITER ;

-- Thông tin user đăng ký
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Thêm dữ liệu vào các bảng
INSERT INTO LoaiPhong (TenLoai, GiaPhong) VALUES 
('Phòng Đơn', 100000),
('Phòng Đôi', 200000),
('Phòng VIP', 300000);

INSERT INTO Phong (MaLoai, SoPhong, TrangThai) VALUES 
(1, '101', 'Trống'),
(1, '102', 'Trống'),
(2, '103', 'Đang sử dụng'),
(2, '104', 'Trống'),
(3, '105', 'Đang sử dụng');

INSERT INTO NhanVien (HoTen, NgaySinh, SoDienThoai) VALUES 
('Nguyễn Văn A', '1990-05-10', '0987654321'),
('Nguyễn Văn B', '1985-09-15', '0123456789'),
('Nguyễn Văn C', '1993-07-21', '0234567891');

INSERT INTO KhachHang (TenKhachHang, DiaChi, SoDienThoai) VALUES 
('Nguyễn Văn D', 'Cần Thơ', '0912345678'),
('Nguyễn Văn E', 'Hậu Giang', '0923456789'),
('Nguyễn Văn F', 'Cần Thơ', '0934567890');

INSERT INTO DichVu (TenDichVu, GiaDichVu) VALUES 
('Dịch vụ giặt là', 10000),
('Dịch vụ ăn sáng', 20000),
('Dịch vụ spa', 30000),
('Dịch vụ thuê xe', 20000),
('Dịch vụ massage', 40000);

INSERT INTO ThuePhong (MaKhachHang, MaPhong, NgayThue, NgayNhan, NgayTra, TrangThai) VALUES 
(1, 3, '2025-03-01', '2025-03-01', '2025-03-05', 'Đang ở'),
(2, 5, '2025-03-02', '2025-03-02', '2025-03-06', 'Đang ở'),
(3, 1, '2025-03-03', '2025-03-03', '2025-03-04', 'Đã đặt');

INSERT INTO SuDungDichVu (MaThue, MaDichVu, SoLuong, NgaySuDung) VALUES 
(1, 1, 2, '2025-03-02'),
(1, 3, 1, '2025-03-03'),
(2, 2, 1, '2025-03-04'),
(2, 5, 2, '2025-03-05'),
(3, 4, 1, '2025-03-06');

INSERT INTO HoaDon (MaSDDV, NgayLapHoaDon, TongTien) 
VALUES 
(1, '2025-03-02', 200000.00),
(2, '2025-03-03', 300000.00),
(3, '2025-03-04', 400000.00),
(4, '2025-03-05', 500000.00),
(5, '2025-03-06', 600000.00);

-- Xóa dữ liệu test
DELETE FROM users WHERE id IN (4);
SELECT * FROM KhachHang;

SHOW TABLES ;