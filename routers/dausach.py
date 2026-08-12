from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

import models
from database import get_db

router = APIRouter(
    prefix="/dausach",
    tags=["Quản lý Đầu sách"]
)

# Cấu trúc nhận gói hàng
class ThongTinDauSachMoi(BaseModel):
    MaDauSach: int
    TenSach: str
    DanhSachMaTacGia: List[str]   
    DanhSachMaTheLoai: List[str]  
    DanhSachMaNXB: List[int]      

# 1. API Lấy danh sách Đầu Sách (Nâng cấp để trả về kèm chi tiết Tác giả, Thể loại, NXB)
@router.get("")
def lay_danh_sach_dau_sach(db: Session = Depends(get_db)):
    danh_sach = db.query(models.DauSach).all()
    ket_qua = []
    for ds in danh_sach:
        ket_qua.append({
            "MaDauSach": ds.MaDauSach,
            "TenSach": ds.TenSach,
            "tac_gia": [{"MaTacGia": tg.MaTacGia, "TenTacGia": tg.TenTacGia} for tg in ds.tac_gia],
            "the_loai": [{"MaTheLoai": tl.MaTheLoai, "TenTheLoai": tl.TenTheLoai} for tl in ds.the_loai],
            "nha_xuat_ban": [{"MaNXB": nxb.MaNXB, "TenNXB": nxb.TenNXB} for nxb in ds.nha_xuat_ban]
        })
    return ket_qua

# 2. API Thêm 1 Đầu sách
@router.post("")
def them_dau_sach_moi(du_lieu: ThongTinDauSachMoi, db: Session = Depends(get_db)):
    try:
        ton_tai = db.query(models.DauSach).filter(models.DauSach.MaDauSach == du_lieu.MaDauSach).first()
        if ton_tai:
            raise HTTPException(status_code=400, detail="Mã đầu sách đã tồn tại!")

        dau_sach_moi = models.DauSach(MaDauSach=du_lieu.MaDauSach, TenSach=du_lieu.TenSach)
        
        dau_sach_moi.tac_gia = db.query(models.TacGia).filter(models.TacGia.MaTacGia.in_(du_lieu.DanhSachMaTacGia)).all()
        dau_sach_moi.the_loai = db.query(models.TheLoai).filter(models.TheLoai.MaTheLoai.in_(du_lieu.DanhSachMaTheLoai)).all()
        dau_sach_moi.nha_xuat_ban = db.query(models.NXB).filter(models.NXB.MaNXB.in_(du_lieu.DanhSachMaNXB)).all()

        db.add(dau_sach_moi)
        db.commit()
        return {"thong_bao": "Đã thêm Đầu sách thành công!"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

# 3. API Cập nhật (Sửa) Đầu sách
@router.put("/{ma_ds}")
def cap_nhat_dau_sach(ma_ds: int, du_lieu: ThongTinDauSachMoi, db: Session = Depends(get_db)):
    try:
        dau_sach = db.query(models.DauSach).filter(models.DauSach.MaDauSach == ma_ds).first()
        if not dau_sach:
            raise HTTPException(status_code=404, detail="Không tìm thấy Đầu sách!")

        dau_sach.TenSach = du_lieu.TenSach
        
        # Cập nhật lại các liên kết Nhiều - Nhiều
        dau_sach.tac_gia = db.query(models.TacGia).filter(models.TacGia.MaTacGia.in_(du_lieu.DanhSachMaTacGia)).all()
        dau_sach.the_loai = db.query(models.TheLoai).filter(models.TheLoai.MaTheLoai.in_(du_lieu.DanhSachMaTheLoai)).all()
        dau_sach.nha_xuat_ban = db.query(models.NXB).filter(models.NXB.MaNXB.in_(du_lieu.DanhSachMaNXB)).all()

        db.commit()
        return {"thong_bao": "Đã cập nhật Đầu sách thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

# 4. API Thêm hàng loạt
@router.post("/hang-loat")
def them_hang_loat_dau_sach(danh_sach: List[ThongTinDauSachMoi], db: Session = Depends(get_db)):
    try:
        so_luong_them = 0
        for du_lieu in danh_sach:
            ton_tai = db.query(models.DauSach).filter(models.DauSach.MaDauSach == du_lieu.MaDauSach).first()
            if not ton_tai:
                dau_sach_moi = models.DauSach(MaDauSach=du_lieu.MaDauSach, TenSach=du_lieu.TenSach)
                dau_sach_moi.tac_gia = db.query(models.TacGia).filter(models.TacGia.MaTacGia.in_(du_lieu.DanhSachMaTacGia)).all()
                dau_sach_moi.the_loai = db.query(models.TheLoai).filter(models.TheLoai.MaTheLoai.in_(du_lieu.DanhSachMaTheLoai)).all()
                dau_sach_moi.nha_xuat_ban = db.query(models.NXB).filter(models.NXB.MaNXB.in_(du_lieu.DanhSachMaNXB)).all()
                
                db.add(dau_sach_moi)
                so_luong_them += 1
        db.commit()
        return {"thong_bao": f"Đã thêm thành công {so_luong_them} Đầu sách mới!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

# 5. API Xóa
@router.delete("/{ma_ds}")
def xoa_dau_sach(ma_ds: int, db: Session = Depends(get_db)):
    try:
        dau_sach = db.query(models.DauSach).filter(models.DauSach.MaDauSach == ma_ds).first()
        if not dau_sach:
            raise HTTPException(status_code=404, detail="Không tìm thấy Đầu sách!")
        
        # Xóa các liên kết trước khi xóa sách
        dau_sach.tac_gia = []
        dau_sach.the_loai = []
        dau_sach.nha_xuat_ban = []
        
        db.delete(dau_sach)
        db.commit()
        return {"thong_bao": "Đã xóa Đầu sách thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")