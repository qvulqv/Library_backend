from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

import models
from database import get_db

router = APIRouter(
    prefix="/bandoc",
    tags=["Quản lý Bạn đọc"]
)

class CapNhatTrangThai(BaseModel):
    TrangThaiMoi: str

class ThongTinBanDocMoi(BaseModel):
    MaBanDoc: str
    HoTenDem: str
    Ten: str
    SDT: str
    Email: str

# 1. Lấy danh sách bạn đọc
@router.get("/")
def lay_danh_sach_ban_doc(db: Session = Depends(get_db)):
    danh_sach_db = db.query(models.BanDoc).all()
    ket_qua = []
    for bandoc in danh_sach_db:
        ho_ten_day_du = f"{bandoc.HoTenDem} {bandoc.Ten}" if bandoc.HoTenDem else bandoc.Ten
        ket_qua.append({
            "ma_bd": bandoc.MaBanDoc,
            "ho_ten": ho_ten_day_du,
            "email": bandoc.Email,
            "trang_thai": bandoc.TrangThai 
        })
    return ket_qua

# 2. Thêm bạn đọc mới
@router.post("/")
def them_ban_doc_moi(du_lieu: ThongTinBanDocMoi, db: Session = Depends(get_db)):
    try:
        ban_doc_cu = db.query(models.BanDoc).filter(models.BanDoc.MaBanDoc == du_lieu.MaBanDoc).first()
        if ban_doc_cu:
            raise HTTPException(status_code=400, detail="Mã sinh viên này đã tồn tại trong hệ thống!")
            
        ban_doc_moi = models.BanDoc(
            MaBanDoc=du_lieu.MaBanDoc,
            HoTenDem=du_lieu.HoTenDem,
            Ten=du_lieu.Ten,
            SDT=du_lieu.SDT,
            Email=du_lieu.Email,
            TrangThai="Hoạt động"
        )
        db.add(ban_doc_moi)
        db.commit()
        return {"thong_bao": "Thêm bạn đọc mới thành công!"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# 3. Thêm bạn đọc hàng loạt
@router.post("/hang-loat")
def them_ban_doc_hang_loat(danh_sach_du_lieu: List[ThongTinBanDocMoi], db: Session = Depends(get_db)):
    so_luong_thanh_cong = 0
    loi_chi_tiet = []
    try:
        for du_lieu in danh_sach_du_lieu:
            ban_doc_cu = db.query(models.BanDoc).filter(models.BanDoc.MaBanDoc == du_lieu.MaBanDoc).first()
            if ban_doc_cu:
                loi_chi_tiet.append(f"Mã {du_lieu.MaBanDoc} đã tồn tại.")
                continue 

            ban_doc_moi = models.BanDoc(
                MaBanDoc=du_lieu.MaBanDoc,
                HoTenDem=du_lieu.HoTenDem,
                Ten=du_lieu.Ten,
                SDT=du_lieu.SDT,
                Email=du_lieu.Email,
                TrangThai="Hoạt động"
            )
            db.add(ban_doc_moi)
            so_luong_thanh_cong += 1

        db.commit()
        return {
            "thong_bao": f"Đã thêm thành công {so_luong_thanh_cong} bạn đọc.",
            "loi": loi_chi_tiet
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# 4. Cập nhật trạng thái
@router.put("/{ma_bd}/trangthai")
def cap_nhat_trang_thai(ma_bd: str, du_lieu: CapNhatTrangThai, db: Session = Depends(get_db)):
    try:
        ban_doc = db.query(models.BanDoc).filter(models.BanDoc.MaBanDoc == ma_bd).first()
        if not ban_doc:
            raise HTTPException(status_code=404, detail="Không tìm thấy bạn đọc")
            
        ban_doc.TrangThai = du_lieu.TrangThaiMoi
        db.commit()
        return {"thong_bao": "Đã cập nhật trạng thái thành công"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# 5. Xóa bạn đọc
@router.delete("/{ma_bd}")
def xoa_ban_doc(ma_bd: str, db: Session = Depends(get_db)):
    try:
        ban_doc = db.query(models.BanDoc).filter(models.BanDoc.MaBanDoc == ma_bd).first()
        if not ban_doc:
            raise HTTPException(status_code=404, detail="Không tìm thấy bạn đọc này trong hệ thống!")
            
        db.delete(ban_doc)
        db.commit()
        return {"thong_bao": "Đã xóa bạn đọc thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")