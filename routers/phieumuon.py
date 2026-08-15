from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

import models
from database import get_db

router = APIRouter(
    prefix="/phieumuon",
    tags=["Quản lý Mượn / Trả sách"]
)

# ==========================================
# CẤU TRÚC NHẬN DỮ LIỆU TỪ FRONTEND
# ==========================================
class ThongTinMuonSach(BaseModel):
    MaBanDoc: str
    NguoiLapPhieu: str
    DanhSachMaSach: List[str] # Nhận vào một mảng chứa các mã sách vật lý

# ==========================================
# 1. API TẠO PHIẾU MƯỢN SÁCH MỚI
# ==========================================
@router.post("")
def tao_phieu_muon(du_lieu: ThongTinMuonSach, db: Session = Depends(get_db)):
    # BƯỚC 1: KIỂM TRA SỐ LƯỢNG (Tối đa 5 cuốn, tối thiểu 1 cuốn)
    so_luong_muon = len(du_lieu.DanhSachMaSach)
    if so_luong_muon == 0:
        raise HTTPException(status_code=400, detail="Vui lòng quét/nhập ít nhất 1 mã sách!")
    if so_luong_muon > 5:
        raise HTTPException(status_code=400, detail=f"Chỉ được mượn tối đa 5 cuốn/lần. Bạn đang chọn {so_luong_muon} cuốn.")

    try:
        # BƯỚC 2: KIỂM TRA TÍNH HỢP LỆ CỦA BẠN ĐỌC VÀ TÀI KHOẢN
        ban_doc = db.query(models.BanDoc).filter(models.BanDoc.MaBanDoc == du_lieu.MaBanDoc).first()
        if not ban_doc:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy Bạn đọc với mã {du_lieu.MaBanDoc}")

        tai_khoan = db.query(models.TaiKhoan).filter(models.TaiKhoan.TenDangNhap == du_lieu.NguoiLapPhieu).first()
        if not tai_khoan:
             raise HTTPException(status_code=404, detail="Tài khoản lập phiếu không tồn tại!")

        # BƯỚC 3: KIỂM TRA TRẠNG THÁI TỪNG CUỐN SÁCH
        sach_hop_le = []
        for ma_sach in du_lieu.DanhSachMaSach:
            sach = db.query(models.Sach).filter(models.Sach.MaSach == ma_sach).first()
            if not sach:
                raise HTTPException(status_code=404, detail=f"Mã sách {ma_sach} không tồn tại trong kho!")
            
            # Đảm bảo sách phải nằm trên kệ và sẵn sàng
            if sach.TrangThai != "Sẵn sàng":
                raise HTTPException(status_code=400, detail=f"Cuốn sách mã {ma_sach} đang không sẵn sàng (Tình trạng: {sach.TrangThai}). Không thể mượn!")
            
            sach_hop_le.append(sach)

        # BƯỚC 4: TẠO PHIẾU MƯỢN TỔNG
        thoi_gian_hien_tai = datetime.now()
        ngay_het_han = thoi_gian_hien_tai + timedelta(days=14) # Tự động cộng 14 ngày

        phieu_moi = models.PhieuMuon(
            MaBanDoc=du_lieu.MaBanDoc,
            NguoiLapPhieu=du_lieu.NguoiLapPhieu,
            NgayMuon=thoi_gian_hien_tai,
            HanTra=ngay_het_han,
            TrangThai="Đang mượn"
        )
        db.add(phieu_moi)
        
        # Dùng flush để lưu nháp và lấy MaPhieu vừa tạo ra từ SQL Server (chưa commit thật)
        db.flush() 

        # BƯỚC 5: TẠO CHI TIẾT PHIẾU MƯỢN VÀ CẬP NHẬT KHO SÁCH
        for sach in sach_hop_le:
            # 5.1 Tạo dòng chi tiết
            chi_tiet = models.ChiTietPhieuMuon(
                MaPhieu=phieu_moi.MaPhieu,
                MaSach=sach.MaSach,
                TrangThaiSach="Chưa trả"
            )
            db.add(chi_tiet)
            
            # 5.2 Đổi trạng thái cuốn sách thành Đã mượn
            sach.TrangThai = "Đã mượn"

        # BƯỚC 6: CHỐT LƯU TOÀN BỘ (COMMIT)
        db.commit()
        return {
            "thong_bao": "Đã lập phiếu mượn sách thành công!",
            "ma_phieu": phieu_moi.MaPhieu,
            "han_tra": ngay_het_han.strftime("%d/%m/%Y")
        }

    except HTTPException:
        # Nếu là lỗi logic do code ném ra (HTTPException), thì hoàn tác giao dịch và ném lỗi tiếp
        db.rollback()
        raise
    except Exception as e:
        # Nếu là lỗi hệ thống bất ngờ, cũng phải hoàn tác để bảo vệ CSDL
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

# (Chúng ta sẽ viết thêm API Trả sách và Lấy danh sách phiếu mượn ở các bước tiếp theo)