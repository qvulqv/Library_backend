from sqlalchemy import Column, Integer, String, Unicode
from database import Base

class NXB(Base):
    __tablename__ = "NXB"
    
    MaNXB = Column(Integer, primary_key=True, index=True) 
    TenNXB = Column(Unicode)
    DiaChi = Column(Unicode)
    Email = Column(String)