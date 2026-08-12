from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

import models
from database import get_db

router = APIRouter(
    prefix="/nxb",
    tags=["Quản lý Nhà xuất bản"]
)

# Cấu trúc dữ liệu NXB - Lưu ý MaNXB là số nguyên (int)
class ThongTinNXB(BaseModel):
    MaNXB: int
    TenNXB: str
    DiaChi: str = None
    Email: str = None

# 1. API Lấy danh sách
@router.get("")
def lay_danh_sach_nxb(db: Session = Depends(get_db)):
    return db.query(models.NXB).all()

# 2. API Thêm NXB đơn lẻ
@router.post("")
def them_nxb(du_lieu: ThongTinNXB, db: Session = Depends(get_db)):
    try:
        ton_tai = db.query(models.NXB).filter(models.NXB.MaNXB == du_lieu.MaNXB).first()
        if ton_tai:
            raise HTTPException(status_code=400, detail="Mã nhà xuất bản này đã tồn tại!")
            
        nxb_moi = models.NXB(
            MaNXB=du_lieu.MaNXB,
            TenNXB=du_lieu.TenNXB,
            DiaChi=du_lieu.DiaChi,
            Email=du_lieu.Email
        )
        db.add(nxb_moi)
        db.commit()
        return {"thong_bao": "Thêm nhà xuất bản thành công!"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# 3. API Thêm NXB hàng loạt
@router.post("/hang-loat")
def them_nxb_hang_loat(danh_sach: List[ThongTinNXB], db: Session = Depends(get_db)):
    so_luong_thanh_cong = 0
    loi_chi_tiet = []
    
    try:
        for item in danh_sach:
            ton_tai = db.query(models.NXB).filter(models.NXB.MaNXB == item.MaNXB).first()
            if ton_tai:
                loi_chi_tiet.append(f"Mã {item.MaNXB} đã tồn tại.")
                continue
                
            nxb_moi = models.NXB(
                MaNXB=item.MaNXB,
                TenNXB=item.TenNXB,
                DiaChi=item.DiaChi,
                Email=item.Email
            )
            db.add(nxb_moi)
            so_luong_thanh_cong += 1
            
        db.commit()
        return {
            "thong_bao": f"Đã thêm thành công {so_luong_thanh_cong} nhà xuất bản.",
            "loi": loi_chi_tiet
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# 4. API Xóa NXB
@router.delete("/{ma_nxb}")
def xoa_nxb(ma_nxb: int, db: Session = Depends(get_db)):
    try:
        nxb = db.query(models.NXB).filter(models.NXB.MaNXB == ma_nxb).first()
        if not nxb:
            raise HTTPException(status_code=404, detail="Không tìm thấy nhà xuất bản này!")
            
        db.delete(nxb)
        db.commit()
        return {"thong_bao": "Đã xóa nhà xuất bản thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Không thể xóa vì đang có sách liên kết với NXB này!")
    # 5. API Cập nhật (Sửa) NXB
@router.put("/{ma_nxb}")
def cap_nhat_nxb(ma_nxb: int, du_lieu: ThongTinNXB, db: Session = Depends(get_db)):
    try:
        # Tìm NXB dựa vào mã số nguyên
        nxb = db.query(models.NXB).filter(models.NXB.MaNXB == ma_nxb).first()
        if not nxb:
            raise HTTPException(status_code=404, detail="Không tìm thấy nhà xuất bản này!")
            
        # Ghi đè các thông tin mới (Bỏ qua MaNXB vì là Khóa chính)
        nxb.TenNXB = du_lieu.TenNXB
        nxb.DiaChi = du_lieu.DiaChi
        nxb.Email = du_lieu.Email
        
        db.commit()
        return {"thong_bao": "Đã cập nhật thông tin Nhà xuất bản thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")