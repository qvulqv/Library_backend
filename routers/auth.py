from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import get_db

router = APIRouter(tags=["Quản lý Sách"])

@router.get("/sach")
def lay_danh_sach_sach(db: Session = Depends(get_db)):
    try:
        danh_sach_sach = db.query(
            models.Sach.MaSach,
            models.Sach.TrangThai,
            models.DauSach.TenSach,
            models.DauSach.MaTacGia
        ).join(
            models.DauSach, 
            models.Sach.MaDauSach == models.DauSach.MaDauSach
        ).all()
        
        ket_qua = []
        for sach in danh_sach_sach:
            ket_qua.append({
                "ma_sach": sach.MaSach,
                "ten_sach": sach.TenSach,
                "tac_gia": sach.MaTacGia,
                "trang_thai": sach.TrangThai
            })
        return ket_qua
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")