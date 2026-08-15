from sqlalchemy import Column, String, Unicode
from database import Base

class KeSach(Base):
    __tablename__ = "KeSach"
    
    MaKeSach = Column(String, primary_key=True, index=True)
    TenKeSach = Column(Unicode)
    ViTri = Column(Unicode)