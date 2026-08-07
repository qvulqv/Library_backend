from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware 

# Lệnh này giúp SQLAlchemy kiểm tra và tự động tạo bảng trong SQL Server nếu chưa có
models.Base.metadata.create_all(bind=engine)

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="API Quản Lý Thư Viện Đại Học Mở",
    description="Backend hỗ trợ quản lý thư viện, mượn trả tài liệu",
    version="1.0.0"
)

models.Base.metadata.create_all(bind=engine)

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
    allow_origins=["http://localhost:5173"], # Cổng của giao diện React
    allow_credentials=True,
    allow_methods=["*"], # Cho phép tất cả các phương thức (GET, POST, PUT, DELETE)
    allow_headers=["*"],
)
def get_db():
    db = SessionLocal() # Mở kết nối
    try:
        yield db        # Giao kết nối cho API sử dụng
    finally:
        db.close()      # Đóng kết nối khi hoàn tất để giải phóng bộ nhớ

# ==========================================
# CÁC ĐƯỜNG DẪN API (ROUTES)
# ==========================================

# API Trang chủ
@app.get("/")
def kiem_tra_he_thong():
    return {"thong_bao": "Chào mừng em! Backend Hệ thống Quản lý Thư viện OU đã chạy thành công!"}

# API Lấy danh sách bạn đọc
@app.get("/bandoc")
def lay_danh_sach_ban_doc(db: Session = Depends(get_db)):
    # Dùng hàm query() của SQLAlchemy để lấy tất cả dữ liệu từ lớp BanDoc (tương ứng bảng BanDoc)
    danh_sach = db.query(models.BanDoc).all()
    return danh_sach
# ==========================================
# API LẤY DANH SÁCH SÁCH
# ==========================================
@app.get("/sach")
def lay_danh_sach_sach(db: Session = Depends(get_db)):
    try:
        # Sử dụng hàm join() để kết nối bảng Sach và bảng DauSach
        danh_sach_sach = db.query(
            models.Sach.MaSach,
            models.Sach.TrangThai,
            models.DauSach.TenSach,
            models.DauSach.TacGia
        ).join(
            models.DauSach, 
            models.Sach.MaDauSach == models.DauSach.MaDauSach
        ).all()
        
        # Tạo một danh sách rỗng để chứa dữ liệu đã được làm đẹp
        ket_qua = []
        
        # Duyệt qua từng dòng dữ liệu lấy được và đưa vào danh sách
        for sach in danh_sach_sach:
            ket_qua.append({
                "ma_sach": sach.MaSach,
                "ten_sach": sach.TenSach,
                "tac_gia": sach.TacGia,
                "trang_thai": sach.TrangThai
            })
            
        return ket_qua
        
    except Exception as e:
        # Báo lỗi nếu quá trình lấy dữ liệu gặp trục trặc
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")
    # ==========================================
# CẤU TRÚC DỮ LIỆU ĐĂNG NHẬP
# ==========================================
class ThongTinDangNhap(BaseModel):
    TenDangNhap: str
    MatKhau: str

# ==========================================
# API ĐĂNG NHẬP VÀ XÁC THỰC VAI TRÒ
# ==========================================
@app.post("/dang-nhap")
def dang_nhap(thong_tin: ThongTinDangNhap, db: Session = Depends(get_db)):
    try:
        # 1. Tìm tài khoản trong cơ sở dữ liệu dựa vào Tên đăng nhập
        tai_khoan = db.query(models.TaiKhoan).filter(models.TaiKhoan.TenDangNhap == thong_tin.TenDangNhap).first()
        
        # 2. Kiểm tra tài khoản có tồn tại không và mật khẩu có khớp không
        if not tai_khoan or tai_khoan.MatKhau != thong_tin.MatKhau:
            # Báo lỗi 401 Unauthorized nếu sai thông tin
            raise HTTPException(status_code=401, detail="Tên đăng nhập hoặc mật khẩu không chính xác!")
            
        # 3. Nếu thành công, trả về vai trò để Frontend biết đường hiển thị giao diện
        return {
            "thong_bao": "Đăng nhập thành công!",
            "vai_tro": tai_khoan.VaiTro,
            "ma_nguoi_dung": tai_khoan.MaNguoiDung,
            "ten_dang_nhap": tai_khoan.TenDangNhap
        }
        
    except HTTPException:
        raise # Giữ nguyên lỗi 401 nếu sai mật khẩu
    except Exception as e:
        # Bắt các lỗi hệ thống khác
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")