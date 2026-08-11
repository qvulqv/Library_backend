# Nhập các công cụ cần thiết từ thư viện sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ==========================================
# THIẾT LẬP THÔNG TIN KẾT NỐI SQL SERVER
# ==========================================
# 1. Tên Server lấy từ ảnh (chữ 'r' ở đầu giúp Python hiểu đúng ký tự '\')
SERVER_NAME = r".\QUANLYTHUVIEN"

# 2. Tên cơ sở dữ liệu chúng ta đã tạo ở Bước 1
DATABASE_NAME = "QuanLyThuVien_OU"

# 3. Thông tin tài khoản đăng nhập (SQL Server Authentication)
USERNAME = "sa"
PASSWORD = "123" 
DRIVER = "ODBC+Driver+17+for+SQL+Server"
DATABASE_URL = f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER_NAME}/{DATABASE_NAME}?driver={DRIVER}&TrustServerCertificate=yes"

# Khởi tạo Engine
engine = create_engine(DATABASE_URL)

# Khởi tạo SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: Lớp nền tảng để sau này chúng ta định nghĩa cấu trúc bảng (Models)
Base = declarative_base()