
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, NVARCHAR, Unicode, Table
from sqlalchemy.orm import relationship
from database import Base
import datetime



class BanDoc(Base):
    __tablename__ = "BanDoc"
    
    MaBanDoc = Column(String, primary_key=True, index=True) # Mã SV không có tiếng Việt, để String
    HoTenDem = Column(Unicode) # Thay String thành Unicode
    Ten = Column(Unicode)      # Thay String thành Unicode
    SDT = Column(String)       # Số điện thoại không có tiếng Việt
    Email = Column(String)     # Email không có tiếng Việt
    TrangThai = Column(Unicode) # Trạng thái có tiếng Việt (ví dụ: "Hoạt động")
# 2. Mô hình đại diện cho bảng NXB (Nhà xuất bản)

class NXB(Base):
    __tablename__ = "NXB"
    MaNXB = Column(Integer, primary_key=True, index=True) # Kiểu số nguyên (INT)
    TenNXB = Column(Unicode)
    DiaChi = Column(Unicode)
    Email = Column(String)
# 3. Mô hình đại diện cho bảng DauSach
# ==========================================
# KHAI BÁO CÁC BẢNG TRUNG GIAN (CẦU NỐI)
# ==========================================

# Cầu nối: Đầu sách - Tác giả
dausach_tacgia = Table('DauSach_TacGia', Base.metadata,
    Column('MaDauSach', String(50), ForeignKey('DauSach.MaDauSach'), primary_key=True),
    Column('MaTacGia', String(50), ForeignKey('TacGia.MaTacGia'), primary_key=True)
)

# Cầu nối: Đầu sách - Thể loại
dausach_theloai = Table('DauSach_TheLoai', Base.metadata,
    Column('MaDauSach', String(50), ForeignKey('DauSach.MaDauSach'), primary_key=True),
    Column('MaTheLoai', String(50), ForeignKey('TheLoai.MaTheLoai'), primary_key=True)
)

# Cầu nối: Đầu sách - Nhà xuất bản (Lưu ý: MaNXB là Integer thì giữ nguyên)
dausach_nxb = Table('DauSach_NXB', Base.metadata,
    Column('MaDauSach', String(50), ForeignKey('DauSach.MaDauSach'), primary_key=True),
    Column('MaNXB', Integer, ForeignKey('NXB.MaNXB'), primary_key=True)
)

# 3. ĐỊNH NGHĨA LỚP ĐẦU SÁCH
class DauSach(Base):
    __tablename__ = "DauSach"
    
    MaDauSach = Column(Integer, primary_key=True, index=True)
    TenSach = Column(Unicode(255), nullable=False) # Phải là TenSach

    # Các relationship bên dưới giữ nguyên...
    tac_gia = relationship("TacGia", secondary=dausach_tacgia, backref="cac_dau_sach")
    the_loai = relationship("TheLoai", secondary=dausach_theloai, backref="cac_dau_sach")
    nha_xuat_ban = relationship("NXB", secondary=dausach_nxb, backref="cac_dau_sach")

    __table_args__ = {'extend_existing': True}
# 4. Mô hình đại diện cho bảng Sach
class Sach(Base):
    __tablename__ = "Sach"
    
    MaSach = Column(String(50), primary_key=True, index=True)
    TrangThai = Column(Unicode(50), default="Sẵn sàng")
    TinhTrang = Column(Unicode(100)) 
    
    MaDauSach = Column(Integer, ForeignKey("DauSach.MaDauSach"))
    
    # CHÚ Ý CHỖ NÀY: Phải là MaKeSach (không phải MaKe)
    MaKeSach = Column(String(20), ForeignKey("KeSach.MaKeSach")) 

    # Mối quan hệ (relationship)
    dau_sach = relationship("DauSach", backref="cac_cuon_sach")
    ke_sach = relationship("KeSach", backref="cac_cuon_sach")

    __table_args__ = {'extend_existing': True}

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
class TacGia(Base):
    __tablename__ = "TacGia"
    MaTacGia = Column(String, primary_key=True, index=True)
    TenTacGia = Column(Unicode)

class TheLoai(Base):
    __tablename__ = "TheLoai"
    MaTheLoai = Column(String, primary_key=True, index=True)
    TenTheLoai = Column(Unicode)
    MoTa = Column(Unicode)

class KeSach(Base):
    __tablename__ = "KeSach"
    MaKeSach = Column(String, primary_key=True, index=True)
    TenKeSach = Column(Unicode)
    ViTri = Column(Unicode)



