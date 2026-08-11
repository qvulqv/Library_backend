from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import get_db

router = APIRouter(tags=["Xác thực & Đăng nhập"])

class ThongTinDangNhap(BaseModel):
    TenDangNhap: str
    MatKhau: str

@router.post("/dang-nhap")
def dang_nhap(thong_tin: ThongTinDangNhap, db: Session = Depends(get_db)):
    try:
        tai_khoan = db.query(models.TaiKhoan).filter(models.TaiKhoan.TenDangNhap == thong_tin.TenDangNhap).first()
        if not tai_khoan or tai_khoan.MatKhau != thong_tin.MatKhau:
            raise HTTPException(status_code=401, detail="Tên đăng nhập hoặc mật khẩu không chính xác!")
            
        return {
            "thong_bao": "Đăng nhập thành công!",
            "vai_tro": tai_khoan.VaiTro,
            "ma_nguoi_dung": tai_khoan.MaNguoiDung,
            "ten_dang_nhap": tai_khoan.TenDangNhap
        }
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")