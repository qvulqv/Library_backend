from fastapi import FastAPI
from database import engine
import models
from fastapi.middleware.cors import CORSMiddleware
from routers import tacgia, bandoc, sach, theloai, auth, nxb, kesach, dausach

# Khởi tạo bảng trong SQL Server
models.Base.metadata.create_all(bind=engine)

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="API Quản Lý Thư Viện Đại Học Mở",
    description="Backend hỗ trợ quản lý thư viện, mượn trả tài liệu",
    version="1.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Nhúng các Router từ thư mục routers vào ứng dụng chính
app.include_router(tacgia.router)
app.include_router(bandoc.router)
app.include_router(sach.router)
app.include_router(theloai.router)
app.include_router(auth.router)
app.include_router(nxb.router)
app.include_router(kesach.router)
app.include_router(dausach.router)
# API Trang chủ kiểm tra hệ thống
@app.get("/")
def kiem_tra_he_thong():
    return {"thong_bao": "Chào mừng em! Backend Hệ thống Quản lý Thư viện OU đã chạy thành công!"}