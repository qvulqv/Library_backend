from sqlalchemy import Column, Integer, String, Unicode, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Bảng trung gian
dausach_tacgia = Table('DauSach_TacGia', Base.metadata,
    Column('MaDauSach', Integer, ForeignKey('DauSach.MaDauSach'), primary_key=True),
    Column('MaTacGia', String(50), ForeignKey('TacGia.MaTacGia'), primary_key=True)
)

dausach_theloai = Table('DauSach_TheLoai', Base.metadata,
    Column('MaDauSach', Integer, ForeignKey('DauSach.MaDauSach'), primary_key=True),
    Column('MaTheLoai', String(50), ForeignKey('TheLoai.MaTheLoai'), primary_key=True)
)

dausach_nxb = Table('DauSach_NXB', Base.metadata,
    Column('MaDauSach', Integer, ForeignKey('DauSach.MaDauSach'), primary_key=True),
    Column('MaNXB', Integer, ForeignKey('NXB.MaNXB'), primary_key=True)
)

# Lớp Đầu Sách
class DauSach(Base):
    __tablename__ = "DauSach"
    
    MaDauSach = Column(Integer, primary_key=True, index=True)
    TenSach = Column(Unicode(255), nullable=False) 

    tac_gia = relationship("TacGia", secondary=dausach_tacgia, backref="cac_dau_sach")
    the_loai = relationship("TheLoai", secondary=dausach_theloai, backref="cac_dau_sach")
    nha_xuat_ban = relationship("NXB", secondary=dausach_nxb, backref="cac_dau_sach")

    __table_args__ = {'extend_existing': True}