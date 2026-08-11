from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

import models
from database import get_db

router = APIRouter(
    prefix="/theloai",
    tags=["Quản lý Thể loại"]
)

class ThongTinTheLoai(BaseModel):
    MaTheLoai: str
    TenTheLoai: str
    MoTa: str = None # Mô tả có thể để trống

# 1. API Lấy danh sách thể loại
@router.get("/")
def lay_danh_sach_the_loai(db: Session = Depends(get_db)):
    return db.query(models.TheLoai).all()

# 2. API Thêm mới một thể loại
@router.post("/")
def them_the_loai(du_lieu: ThongTinTheLoai, db: Session = Depends(get_db)):
    try:
        ton_tai = db.query(models.TheLoai).filter(models.TheLoai.MaTheLoai == du_lieu.MaTheLoai).first()
        if ton_tai:
            raise HTTPException(status_code=400, detail="Mã thể loại này đã tồn tại trong hệ thống!")
            
        the_loai_moi = models.TheLoai(
            MaTheLoai=du_lieu.MaTheLoai,
            TenTheLoai=du_lieu.TenTheLoai,
            MoTa=du_lieu.MoTa
        )
        db.add(the_loai_moi)
        db.commit()
        return {"thong_bao": "Thêm thể loại thành công!"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# 3. API Thêm hàng loạt thể loại
@router.post("/hang-loat")
def them_the_loai_hang_loat(danh_sach: List[ThongTinTheLoai], db: Session = Depends(get_db)):
    so_luong_thanh_cong = 0
    loi_chi_tiet = []
    
    try:
        for item in danh_sach:
            ton_tai = db.query(models.TheLoai).filter(models.TheLoai.MaTheLoai == item.MaTheLoai).first()
            if ton_tai:
                loi_chi_tiet.append(f"Mã {item.MaTheLoai} đã tồn tại.")
                continue
                
            the_loai_moi = models.TheLoai(
                MaTheLoai=item.MaTheLoai,
                TenTheLoai=item.TenTheLoai,
                MoTa=item.MoTa
            )
            db.add(the_loai_moi)
            so_luong_thanh_cong += 1
            
        db.commit()
        return {
            "thong_bao": f"Đã thêm thành công {so_luong_thanh_cong} thể loại.",
            "loi": loi_chi_tiet
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# 4. API Xóa thể loại
@router.delete("/{ma_tl}")
def xoa_the_loai(ma_tl: str, db: Session = Depends(get_db)):
    try:
        the_loai = db.query(models.TheLoai).filter(models.TheLoai.MaTheLoai == ma_tl).first()
        if not the_loai:
            raise HTTPException(status_code=404, detail="Không tìm thấy thể loại này!")
            
        db.delete(the_loai)
        db.commit()
        return {"thong_bao": "Đã xóa thể loại thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Không thể xóa thể loại này vì đang có đầu sách liên kết!")