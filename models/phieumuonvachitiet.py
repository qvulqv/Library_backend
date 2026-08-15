from sqlalchemy import Column, Integer, String, NVARCHAR, DateTime, ForeignKey
import datetime
from database import Base

class PhieuMuon(Base):
    __tablename__ = "PhieuMuon"

    MaPhieu = Column(Integer, primary_key=True, index=True, autoincrement=True)
    MaBanDoc = Column(String(20), ForeignKey("BanDoc.MaBanDoc"), nullable=False)
    NguoiLapPhieu = Column(String(50), ForeignKey("TaiKhoan.TenDangNhap"), nullable=False)
    NgayMuon = Column(DateTime, default=datetime.datetime.now)
    HanTra = Column(DateTime, nullable=False) 
    TrangThai = Column(NVARCHAR(50), default="Đang mượn")

class ChiTietPhieuMuon(Base):
    __tablename__ = "ChiTietPhieuMuon"

    MaPhieu = Column(Integer, ForeignKey("PhieuMuon.MaPhieu"), primary_key=True)
    MaSach = Column(String(50), ForeignKey("Sach.MaSach"), primary_key=True)
    TrangThaiSach = Column(NVARCHAR(50), default="Chưa trả")
    NgayTraThucTe = Column(DateTime, nullable=True)