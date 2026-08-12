from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

import models
from database import get_db

router = APIRouter(
    prefix="/sach",
    tags=["Quản lý Cuốn sách vật lý"]
)

# ==========================================
# CẤU TRÚC NHẬN DỮ LIỆU TỪ FRONTEND
# ==========================================
class ThongTinSach(BaseModel):
    MaSach: str
    MaDauSach: int
    MaKeSach: Optional[str] = None
    TinhTrang: Optional[str] = "Mới"
    TrangThai: Optional[str] = "Sẵn sàng"

# ==========================================
# 1. API LẤY DANH SÁCH SÁCH
# ==========================================
@router.get("")
def lay_danh_sach_cuon_sach(db: Session = Depends(get_db)):
    danh_sach = db.query(models.Sach).all()
    ket_qua = []
    for s in danh_sach:
        ket_qua.append({
            "MaSach": s.MaSach,
            "MaDauSach": s.MaDauSach,
            # Tự động lấy Tên sách từ bảng DauSach thông qua relationship
            "TenSach": s.dau_sach.TenSach if s.dau_sach else "Không xác định",
            "MaKeSach": s.MaKeSach,
            # Tự động lấy Tên kệ từ bảng KeSach thông qua relationship
            "TenKeSach": s.ke_sach.TenKeSach if s.ke_sach else "Chưa xếp kệ",
            "TinhTrang": s.TinhTrang,
            "TrangThai": s.TrangThai
        })
    return ket_qua

# ==========================================
# 2. API THÊM 1 CUỐN SÁCH
# ==========================================
@router.post("")
def them_cuon_sach(du_lieu: ThongTinSach, db: Session = Depends(get_db)):
    try:
        ton_tai = db.query(models.Sach).filter(models.Sach.MaSach == du_lieu.MaSach).first()
        if ton_tai:
            raise HTTPException(status_code=400, detail="Mã cuốn sách này đã tồn tại trong kho!")

        sach_moi = models.Sach(
            MaSach=du_lieu.MaSach,
            MaDauSach=du_lieu.MaDauSach,
            MaKeSach=du_lieu.MaKeSach,
            TinhTrang=du_lieu.TinhTrang,
            TrangThai=du_lieu.TrangThai
        )
        db.add(sach_moi)
        db.commit()
        return {"thong_bao": "Đã thêm Cuốn sách vào kho thành công!"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# ==========================================
# 3. API CẬP NHẬT (SỬA) CUỐN SÁCH
# ==========================================
@router.put("/{ma_sach}")
def cap_nhat_cuon_sach(ma_sach: str, du_lieu: ThongTinSach, db: Session = Depends(get_db)):
    try:
        sach = db.query(models.Sach).filter(models.Sach.MaSach == ma_sach).first()
        if not sach:
            raise HTTPException(status_code=404, detail="Không tìm thấy cuốn sách này!")

        sach.MaDauSach = du_lieu.MaDauSach
        sach.MaKeSach = du_lieu.MaKeSach
        sach.TinhTrang = du_lieu.TinhTrang
        sach.TrangThai = du_lieu.TrangThai
        
        db.commit()
        return {"thong_bao": "Cập nhật thông tin sách thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# ==========================================
# 4. API THÊM HÀNG LOẠT
# ==========================================
@router.post("/hang-loat")
def them_hang_loat_sach(danh_sach: List[ThongTinSach], db: Session = Depends(get_db)):
    try:
        so_luong_them = 0
        for du_lieu in danh_sach:
            ton_tai = db.query(models.Sach).filter(models.Sach.MaSach == du_lieu.MaSach).first()
            if not ton_tai:
                sach_moi = models.Sach(
                    MaSach=du_lieu.MaSach,
                    MaDauSach=du_lieu.MaDauSach,
                    MaKeSach=du_lieu.MaKeSach,
                    TinhTrang=du_lieu.TinhTrang,
                    TrangThai=du_lieu.TrangThai
                )
                db.add(sach_moi)
                so_luong_them += 1
        db.commit()
        return {"thong_bao": f"Đã thêm thành công {so_luong_them} Cuốn sách vào kho!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

# ==========================================
# 5. API XÓA CUỐN SÁCH
# ==========================================
@router.delete("/{ma_sach}")
def xoa_cuon_sach(ma_sach: str, db: Session = Depends(get_db)):
    try:
        sach = db.query(models.Sach).filter(models.Sach.MaSach == ma_sach).first()
        if not sach:
            raise HTTPException(status_code=404, detail="Không tìm thấy cuốn sách này!")
            
        db.delete(sach)
        db.commit()
        return {"thong_bao": "Đã xóa cuốn sách khỏi kho!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")