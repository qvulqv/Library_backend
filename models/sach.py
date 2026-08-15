from sqlalchemy import Column, Integer, String, Unicode, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Sach(Base):
    __tablename__ = "Sach"
    
    MaSach = Column(String(50), primary_key=True, index=True)
    TrangThai = Column(Unicode(50), default="Sẵn sàng")
    TinhTrang = Column(Unicode(100)) 
    
    MaDauSach = Column(Integer, ForeignKey("DauSach.MaDauSach"))
    MaKeSach = Column(String(20), ForeignKey("KeSach.MaKeSach")) 

    dau_sach = relationship("DauSach", backref="cac_cuon_sach")
    ke_sach = relationship("KeSach", backref="cac_cuon_sach")

    __table_args__ = {'extend_existing': True}