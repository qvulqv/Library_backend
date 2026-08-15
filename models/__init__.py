# Tệp __init__.py giúp thư mục models hoạt động như một module thống nhất
from .bandoc import BanDoc
from .nxb import NXB
from .tacgia import TacGia
from .theloai import TheLoai
from .kesach import KeSach
from .taikhoan import TaiKhoan
from .dausach import DauSach, dausach_tacgia, dausach_theloai, dausach_nxb
from .sach import Sach
from .phieumuonvachitiet import PhieuMuon, ChiTietPhieuMuon