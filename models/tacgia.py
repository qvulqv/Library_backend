from sqlalchemy import Column, String, Unicode
from database import Base

class TacGia(Base):
    __tablename__ = "TacGia"
    
    MaTacGia = Column(String, primary_key=True, index=True)
    TenTacGia = Column(Unicode)