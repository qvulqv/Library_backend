from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

import models
from database import get_db

router = APIRouter(
    prefix="/kesach",
    tags=["Quản lý Kệ sách"]
)

# Cấu trúc dữ liệu cho Kệ sách
class ThongTinKeSach(BaseModel):
    MaKeSach: str
    TenKeSach: str
    ViTri: str = None # Vị trí có thể để trống

# 1. API Lấy danh sách kệ sách
@router.get("")
def lay_danh_sach_ke_sach(db: Session = Depends(get_db)):
    return db.query(models.KeSach).all()

# 2. API Thêm kệ sách mới
@router.post("")
def them_ke_sach(du_lieu: ThongTinKeSach, db: Session = Depends(get_db)):
    try:
        ton_tai = db.query(models.KeSach).filter(models.KeSach.MaKeSach == du_lieu.MaKeSach).first()
        if ton_tai:
            raise HTTPException(status_code=400, detail="Mã kệ sách này đã tồn tại trong hệ thống!")
            
        ke_sach_moi = models.KeSach(
            MaKeSach=du_lieu.MaKeSach,
            TenKeSach=du_lieu.TenKeSach,
            ViTri=du_lieu.ViTri
        )
        db.add(ke_sach_moi)
        db.commit()
        return {"thong_bao": "Thêm kệ sách thành công!"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# 3. API Thêm kệ sách hàng loạt
@router.post("/hang-loat")
def them_ke_sach_hang_loat(danh_sach: List[ThongTinKeSach], db: Session = Depends(get_db)):
    so_luong_thanh_cong = 0
    loi_chi_tiet = []
    
    try:
        for item in danh_sach:
            ton_tai = db.query(models.KeSach).filter(models.KeSach.MaKeSach == item.MaKeSach).first()
            if ton_tai:
                loi_chi_tiet.append(f"Mã {item.MaKeSach} đã tồn tại.")
                continue
                
            ke_sach_moi = models.KeSach(
                MaKeSach=item.MaKeSach,
                TenKeSach=item.TenKeSach,
                ViTri=item.ViTri
            )
            db.add(ke_sach_moi)
            so_luong_thanh_cong += 1
            
        db.commit()
        return {
            "thong_bao": f"Đã thêm thành công {so_luong_thanh_cong} kệ sách.",
            "loi": loi_chi_tiet
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# 4. API Xóa kệ sách
@router.delete("/{ma_ks}")
def xoa_ke_sach(ma_ks: str, db: Session = Depends(get_db)):
    try:
        ke_sach = db.query(models.KeSach).filter(models.KeSach.MaKeSach == ma_ks).first()
        if not ke_sach:
            raise HTTPException(status_code=404, detail="Không tìm thấy kệ sách này!")
            
        db.delete(ke_sach)
        db.commit()
        return {"thong_bao": "Đã xóa kệ sách thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Không thể xóa kệ sách này vì đang chứa đầu sách!")