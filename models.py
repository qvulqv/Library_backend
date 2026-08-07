
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, NVARCHAR
from sqlalchemy.orm import relationship
from database import Base
import datetime



# 1. Mô hình đại diện cho bảng BanDoc
class BanDoc(Base):
    __tablename__ = "BanDoc" 

    MaBanDoc = Column(String(20), primary_key=True, index=True)
    HoTenDem = Column(NVARCHAR(100), nullable=False)
    Ten = Column(NVARCHAR(50), nullable=False)
    SDT = Column(String(15))
    Email = Column(String(100))

# 2. Mô hình đại diện cho bảng NXB (Nhà xuất bản)
class NXB(Base):
    __tablename__ = "NXB"

    MaNXB = Column(Integer, primary_key=True, index=True, autoincrement=True)
    TenNXB = Column(NVARCHAR(255), nullable=False)
    DiaChi = Column(NVARCHAR(500))
    Email = Column(String(100))

# 3. Mô hình đại diện cho bảng DauSach
class DauSach(Base):
    __tablename__ = "DauSach"

    MaDauSach = Column(Integer, primary_key=True, index=True, autoincrement=True)
    TenSach = Column(NVARCHAR(255), nullable=False)
    TacGia = Column(NVARCHAR(255))
    LinhVuc = Column(NVARCHAR(100))
    MaNXB = Column(Integer, ForeignKey("NXB.MaNXB"))

# 4. Mô hình đại diện cho bảng Sach
class Sach(Base):
    __tablename__ = "Sach"

    MaSach = Column(String(50), primary_key=True, index=True)
    TrangThai = Column(NVARCHAR(50), default="Sẵn sàng")
    MaDauSach = Column(Integer, ForeignKey("DauSach.MaDauSach"))
    MaKe = Column(Integer, nullable=True)

# 5. Bảng Phiếu Mượn (Thông tin chung)
class PhieuMuon(Base):
    __tablename__ = "PhieuMuon"

    MaPhieu = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Liên kết với người dùng mượn sách
    MaBanDoc = Column(String(20), ForeignKey("BanDoc.MaBanDoc"), nullable=False)
    
    # Liên kết với thủ thư xử lý yêu cầu mượn
    NguoiLapPhieu = Column(String(50), ForeignKey("TaiKhoan.TenDangNhap"), nullable=False)
    
    # Mốc thời gian
    NgayMuon = Column(DateTime, default=datetime.datetime.now)
    HanTra = Column(DateTime, nullable=False) 
    
    # Trạng thái tổng quát của cả phiếu: "Đang mượn", "Đã trả đủ", "Trễ hạn"
    TrangThai = Column(NVARCHAR(50), default="Đang mượn")

# 6. Bảng Chi Tiết Phiếu Mượn (Thông tin từng cuốn sách)
class ChiTietPhieuMuon(Base):
    __tablename__ = "ChiTietPhieuMuon"

    # Khóa chính của bảng này là sự kết hợp giữa MaPhieu và MaSach
    MaPhieu = Column(Integer, ForeignKey("PhieuMuon.MaPhieu"), primary_key=True)
    MaSach = Column(String(50), ForeignKey("Sach.MaSach"), primary_key=True)
    
    # Trạng thái của riêng cuốn sách này: "Chưa trả", "Đã trả", "Làm mất"
    TrangThaiSach = Column(NVARCHAR(50), default="Chưa trả")
    NgayTraThucTe = Column(DateTime, nullable=True)
# ==========================================
# 7. MÔ HÌNH BẢNG TÀI KHOẢN (PHỤC VỤ ĐĂNG NHẬP VÀ PHÂN QUYỀN)
# ==========================================
class TaiKhoan(Base):
    __tablename__ = "TaiKhoan"

    # Tên đăng nhập là duy nhất (Ví dụ: 'admin', 'thuthu01', 'SV001')
    TenDangNhap = Column(String(50), primary_key=True, index=True)
    
    # Mật khẩu (Sau này chúng ta sẽ viết mã hóa mật khẩu chứ không lưu chữ thường để bảo mật)
    MatKhau = Column(String(255), nullable=False) 
    
    # Cột VaiTro sẽ chứa 1 trong 3 giá trị: 'GiamDoc', 'ThuThu', 'BanDoc'
    VaiTro = Column(String(20), nullable=False) 
    
    # Mã người dùng để liên kết với bảng BanDoc hoặc thông tin Nhân viên
    MaNguoiDung = Column(String(50), nullable=False)