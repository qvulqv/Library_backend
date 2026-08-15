from sqlalchemy import Column, String, Unicode
from database import Base

class BanDoc(Base):
    __tablename__ = "BanDoc"
    
    MaBanDoc = Column(String, primary_key=True, index=True) 
    HoTenDem = Column(Unicode) 
    Ten = Column(Unicode)      
    SDT = Column(String)       
    Email = Column(String)     
    TrangThai = Column(Unicode)