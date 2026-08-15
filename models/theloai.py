from sqlalchemy import Column, String, Unicode
from database import Base

class TheLoai(Base):
    __tablename__ = "TheLoai"
    
    MaTheLoai = Column(String, primary_key=True, index=True)
    TenTheLoai = Column(Unicode)
    MoTa = Column(Unicode)