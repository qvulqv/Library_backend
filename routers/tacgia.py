from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

import models
from database import get_db

router = APIRouter(
    prefix="/tacgia",
    tags=["Quản lý Tác giả"]
)

# ==========================================
# CẤU TRÚC DỮ LIỆU (PYDANTIC) PHẢI ĐẶT Ở ĐÂY
# ==========================================
class ThongTinTacGia(BaseModel):
    MaTacGia: str
    TenTacGia: str

# ==========================================
# 1. API LẤY DANH SÁCH TÁC GIẢ
# ==========================================
@router.get("")
def lay_danh_sach_tac_gia(db: Session = Depends(get_db)):
    return db.query(models.TacGia).all()

# ==========================================
# 2. API THÊM 1 TÁC GIẢ
# ==========================================
@router.post("")
def them_tac_gia(du_lieu: ThongTinTacGia, db: Session = Depends(get_db)):
    try:
        ton_tai = db.query(models.TacGia).filter(models.TacGia.MaTacGia == du_lieu.MaTacGia).first()
        if ton_tai:
            raise HTTPException(status_code=400, detail="Mã tác giả đã tồn tại!")

        tac_gia_moi = models.TacGia(
            MaTacGia=du_lieu.MaTacGia,
            TenTacGia=du_lieu.TenTacGia
        )
        db.add(tac_gia_moi)
        db.commit()
        return {"thong_bao": "Đã thêm tác giả thành công!"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

# ==========================================
# 3. API SỬA TÁC GIẢ
# ==========================================
@router.put("/{ma_tac_gia}")
def sua_tac_gia(ma_tac_gia: str, du_lieu: ThongTinTacGia, db: Session = Depends(get_db)):
    try:
        tac_gia = db.query(models.TacGia).filter(models.TacGia.MaTacGia == ma_tac_gia).first()
        if not tac_gia:
            raise HTTPException(status_code=404, detail="Không tìm thấy tác giả này!")
            
        tac_gia.TenTacGia = du_lieu.TenTacGia
        db.commit()
        return {"thong_bao": "Đã cập nhật tác giả thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

# ==========================================
# 4. API THÊM HÀNG LOẠT (Nơi từng xảy ra lỗi)
# ==========================================
@router.post("/hang-loat")
def them_tac_gia_hang_loat(danh_sach: List[ThongTinTacGia], db: Session = Depends(get_db)):
    try:
        so_luong = 0
        for du_lieu in danh_sach:
            ton_tai = db.query(models.TacGia).filter(models.TacGia.MaTacGia == du_lieu.MaTacGia).first()
            if not ton_tai:
                tac_gia_moi = models.TacGia(
                    MaTacGia=du_lieu.MaTacGia,
                    TenTacGia=du_lieu.TenTacGia
                )
                db.add(tac_gia_moi)
                so_luong += 1
        db.commit()
        return {"thong_bao": f"Đã thêm thành công {so_luong} tác giả!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

# ==========================================
# 5. API XÓA TÁC GIẢ
# ==========================================
@router.delete("/{ma_tac_gia}")
def xoa_tac_gia(ma_tac_gia: str, db: Session = Depends(get_db)):
    try:
        tac_gia = db.query(models.TacGia).filter(models.TacGia.MaTacGia == ma_tac_gia).first()
        if not tac_gia:
            raise HTTPException(status_code=404, detail="Không tìm thấy tác giả!")
            
        db.delete(tac_gia)
        db.commit()
        return {"thong_bao": "Đã xóa tác giả thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")