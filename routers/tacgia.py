from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Gọi mô hình dữ liệu và cấu hình CSDL từ thư mục gốc bên ngoài
import models 
from database import get_db

# Khởi tạo Router (Bản sao thu nhỏ của app)
router = APIRouter(
    prefix="/tacgia",        # Tất cả API trong tệp này đều tự động có /tacgia ở đầu
    tags=["Quản lý Tác giả"] # Giúp phân nhóm gọn gàng nếu em xem tài liệu Swagger UI
)

# Cấu trúc dữ liệu
class ThongTinTacGia(BaseModel):
    MaTacGia: str
    TenTacGia: str

# 1. API Lấy danh sách (Đường dẫn giờ chỉ là "/")
@router.get("/")
def lay_danh_sach_tac_gia(db: Session = Depends(get_db)):
    return db.query(models.TacGia).all()

# 2. API Thêm mới
@router.post("/")
def them_tac_gia(du_lieu: ThongTinTacGia, db: Session = Depends(get_db)):
    try:
        tac_gia_cu = db.query(models.TacGia).filter(models.TacGia.MaTacGia == du_lieu.MaTacGia).first()
        if tac_gia_cu:
            raise HTTPException(status_code=400, detail="Mã tác giả đã tồn tại!")
            
        tac_gia_moi = models.TacGia(MaTacGia=du_lieu.MaTacGia, TenTacGia=du_lieu.TenTacGia)
        db.add(tac_gia_moi)
        db.commit()
        return {"thong_bao": "Thêm tác giả thành công!"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# 3. API Xóa
@router.delete("/{ma_tg}")
def xoa_tac_gia(ma_tg: str, db: Session = Depends(get_db)):
    try:
        tac_gia = db.query(models.TacGia).filter(models.TacGia.MaTacGia == ma_tg).first()
        if not tac_gia:
            raise HTTPException(status_code=404, detail="Không tìm thấy tác giả!")
            
        db.delete(tac_gia)
        db.commit()
        return {"thong_bao": "Đã xóa tác giả thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Không thể xóa do ràng buộc dữ liệu!")
    from typing import List


# API Thêm tác giả hàng loạt
@router.post("/hang-loat")
def them_tac_gia_hang_loat(danh_sach: List[ThongTinTacGia], db: Session = Depends(get_db)):
    so_luong_thanh_cong = 0
    loi_chi_tiet = []
    
    try:
        for item in danh_sach:
            # Kiểm tra xem mã tác giả đã tồn tại chưa
            ton_tai = db.query(models.TacGia).filter(models.TacGia.MaTacGia == item.MaTacGia).first()
            if ton_tai:
                loi_chi_tiet.append(f"Mã {item.MaTacGia} đã tồn tại.")
                continue
                
            tac_gia_moi = models.TacGia(
                MaTacGia=item.MaTacGia,
                TenTacGia=item.TenTacGia
            )
            db.add(tac_gia_moi)
            so_luong_thanh_cong += 1
            
        db.commit()
        return {
            "thong_bao": f"Đã thêm thành công {so_luong_thanh_cong} tác giả.",
            "loi": loi_chi_tiet
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")