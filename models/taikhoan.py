from sqlalchemy import Column, String
from database import Base

class TaiKhoan(Base):
    __tablename__ = "TaiKhoan"

    TenDangNhap = Column(String(50), primary_key=True, index=True)
    MatKhau = Column(String(255), nullable=False) 
    VaiTro = Column(String(20), nullable=False) 
    MaNguoiDung = Column(String(50), nullable=False)