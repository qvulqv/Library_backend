from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Khởi tạo bảng trong SQL Server
models.Base.metadata.create_all(bind=engine)

# Khởi tạo ứng dụng FastAPI (Chỉ viết 1 lần)
app = FastAPI(
    title="API Quản Lý Thư Viện Đại Học Mở",
    description="Backend hỗ trợ quản lý thư viện, mượn trả tài liệu",
    version="1.0.0"
)

# ==========================================
# CẤU HÌNH BẢO MẬT CORS CHO PHÉP FRONTEND KẾT NỐI
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# CẤU TRÚC DỮ LIỆU ĐĂNG NHẬP
# ==========================================
class ThongTinDangNhap(BaseModel):
    TenDangNhap: str
    MatKhau: str

# ==========================================
# CÁC ĐƯỜNG DẪN API (ROUTES)
# ==========================================

# API Trang chủ
@app.get("/")
def kiem_tra_he_thong():
    return {"thong_bao": "Chào mừng em! Backend Hệ thống Quản lý Thư viện OU đã chạy thành công!"}

# API Lấy danh sách bạn đọc (Đã sửa lại thành /ban-doc để khớp với React)
# API Lấy danh sách bạn đọc
@app.get("/bandoc")
def lay_danh_sach_ban_doc(db: Session = Depends(get_db)):
    danh_sach_db = db.query(models.BanDoc).all()
    
    ket_qua = []
    for bandoc in danh_sach_db:
        # Ghép Họ tên đệm và Tên
        ho_ten_day_du = f"{bandoc.HoTenDem} {bandoc.Ten}" if bandoc.HoTenDem else bandoc.Ten
            
        ket_qua.append({
            "ma_bd": bandoc.MaBanDoc,
            "ho_ten": ho_ten_day_du,
            "email": bandoc.Email,
            "trang_thai": bandoc.TrangThai 
        })
        
    return ket_qua

# API LẤY DANH SÁCH SÁCH
@app.get("/sach")
def lay_danh_sach_sach(db: Session = Depends(get_db)):
    try:
        danh_sach_sach = db.query(
            models.Sach.MaSach,
            models.Sach.TrangThai,
            models.DauSach.TenSach,
            models.DauSach.TacGia
        ).join(
            models.DauSach, 
            models.Sach.MaDauSach == models.DauSach.MaDauSach
        ).all()
        
        ket_qua = []
        for sach in danh_sach_sach:
            ket_qua.append({
                "ma_sach": sach.MaSach,
                "ten_sach": sach.TenSach,
                "tac_gia": sach.TacGia,
                "trang_thai": sach.TrangThai
            })
            
        return ket_qua
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")

# API ĐĂNG NHẬP VÀ XÁC THỰC VAI TRÒ
@app.post("/dang-nhap")
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
# ==========================================
# CẤU TRÚC DỮ LIỆU CẬP NHẬT TRẠNG THÁI
# ==========================================
class CapNhatTrangThai(BaseModel):
    TrangThaiMoi: str

# ==========================================
# API CẬP NHẬT TRẠNG THÁI BẠN ĐỌC
# ==========================================
@app.put("/bandoc/{ma_bd}/trangthai")
def cap_nhat_trang_thai(ma_bd: str, du_lieu: CapNhatTrangThai, db: Session = Depends(get_db)):
    try:
        # 1. Tìm bạn đọc trong cơ sở dữ liệu dựa vào mã sinh viên
        ban_doc = db.query(models.BanDoc).filter(models.BanDoc.MaBanDoc == ma_bd).first()
        
        # Nếu không tìm thấy thì báo lỗi
        if not ban_doc:
            raise HTTPException(status_code=404, detail="Không tìm thấy bạn đọc")
            
        # 2. Thay đổi trạng thái hiện tại thành trạng thái mới
        ban_doc.TrangThai = du_lieu.TrangThaiMoi
        
        # 3. Lưu sự thay đổi vào SQL Server
        db.commit()
        
        return {"thong_bao": "Đã cập nhật trạng thái thành công"}
        
    except Exception as e:
        db.rollback() # Hoàn tác nếu có lỗi
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")
    # ==========================================
# CẤU TRÚC DỮ LIỆU THÊM BẠN ĐỌC
# ==========================================
# Lớp này định nghĩa hình dáng gói dữ liệu mà React sẽ gửi sang
class ThongTinBanDocMoi(BaseModel):
    MaBanDoc: str
    HoTenDem: str
    Ten: str
    SDT: str
    Email: str

# ==========================================
# API THÊM BẠN ĐỌC MỚI
# ==========================================
@app.post("/bandoc")
def them_ban_doc_moi(du_lieu: ThongTinBanDocMoi, db: Session = Depends(get_db)):
    try:
        # 1. Kiểm tra xem Mã sinh viên này đã có trong SQL Server chưa
        ban_doc_cu = db.query(models.BanDoc).filter(models.BanDoc.MaBanDoc == du_lieu.MaBanDoc).first()
        
        if ban_doc_cu:
            # Nếu đã có, từ chối lưu và báo lỗi về cho React
            raise HTTPException(status_code=400, detail="Mã sinh viên này đã tồn tại trong hệ thống!")
            
        # 2. Nếu chưa có, tạo một bản ghi BanDoc mới
        ban_doc_moi = models.BanDoc(
            MaBanDoc=du_lieu.MaBanDoc,
            HoTenDem=du_lieu.HoTenDem,
            Ten=du_lieu.Ten,
            SDT=du_lieu.SDT,
            Email=du_lieu.Email,
            TrangThai="Hoạt động"  # Mặc định tài khoản mới sẽ được phép hoạt động
        )
        
        # 3. Thêm vào CSDL và lưu lại (commit)
        db.add(ban_doc_moi)
        db.commit()
        
        return {"thong_bao": "Thêm bạn đọc mới thành công!"}
        
    except HTTPException:
        raise # Giữ nguyên lỗi 400 để gửi về Frontend
    except Exception as e:
        db.rollback() # Nếu SQL lỗi, hoàn tác mọi thay đổi để tránh hỏng dữ liệu
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")
    # ==========================================
# API XÓA BẠN ĐỌC
# ==========================================
@app.delete("/bandoc/{ma_bd}")
def xoa_ban_doc(ma_bd: str, db: Session = Depends(get_db)):
    try:
        # 1. Tìm bạn đọc cần xóa dựa vào mã sinh viên
        ban_doc = db.query(models.BanDoc).filter(models.BanDoc.MaBanDoc == ma_bd).first()
        
        # Nếu không tìm thấy thì báo lỗi
        if not ban_doc:
            raise HTTPException(status_code=404, detail="Không tìm thấy bạn đọc này trong hệ thống!")
            
        # 2. Xóa khỏi cơ sở dữ liệu và lưu lại thay đổi
        db.delete(ban_doc)
        db.commit()
        
        return {"thong_bao": "Đã xóa bạn đọc thành công!"}
        
    except Exception as e:
        db.rollback() # Hoàn tác nếu có lỗi bất ngờ
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")
    # ==========================================
# API THÊM BẠN ĐỌC HÀNG LOẠT
# ==========================================
@app.post("/bandoc/hang-loat")
def them_ban_doc_hang_loat(danh_sach_du_lieu: List[ThongTinBanDocMoi], db: Session = Depends(get_db)):
    so_luong_thanh_cong = 0
    loi_chi_tiet = [] # Danh sách ghi chép lại các mã sinh viên bị lỗi

    try:
        # Duyệt qua từng sinh viên trong danh sách gửi lên
        for du_lieu in danh_sach_du_lieu:
            # 1. Kiểm tra mã sinh viên đã tồn tại chưa
            ban_doc_cu = db.query(models.BanDoc).filter(models.BanDoc.MaBanDoc == du_lieu.MaBanDoc).first()
            
            if ban_doc_cu:
                # Nếu đã có, ghi chú lại lỗi và bỏ qua, đi tới người tiếp theo
                loi_chi_tiet.append(f"Mã {du_lieu.MaBanDoc} đã tồn tại.")
                continue 

            # 2. Nếu mã mới tinh, tạo bản ghi mới
            ban_doc_moi = models.BanDoc(
                MaBanDoc=du_lieu.MaBanDoc,
                HoTenDem=du_lieu.HoTenDem,
                Ten=du_lieu.Ten,
                SDT=du_lieu.SDT,
                Email=du_lieu.Email,
                TrangThai="Hoạt động"
            )
            
            # Đưa vào hàng đợi để chuẩn bị lưu
            db.add(ban_doc_moi)
            so_luong_thanh_cong += 1

        # 3. Lưu tất cả những người hợp lệ vào CSDL cùng một lúc
        db.commit()

        # 4. Trả về báo cáo kết quả cho giao diện
        return {
            "thong_bao": f"Đã thêm thành công {so_luong_thanh_cong} bạn đọc.",
            "loi": loi_chi_tiet
        }

    except Exception as e:
        db.rollback() # Hoàn tác nếu có lỗi hệ thống nghiêm trọng
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")