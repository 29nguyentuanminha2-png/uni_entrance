# Hệ thống Quản lý Thí sinh Dự thi Đại học

Ứng dụng OOP Python quản lý thí sinh dự thi đại học khối A và khối B, với giao diện web React và Docker deployment.

## Tính năng

- Quản lý thí sinh (CRUD): thêm, sửa, xóa, tìm kiếm
- Hiển thị danh sách theo khối A (Toán, Lý, Hóa) và khối B (Toán, Hóa, Sinh)
- Tính điểm xét tuyển:
  - Khối A: Toán × 1.5 + Lý + Hóa + Điểm tư duy
  - Khối B: Toán + Hóa × 1.5 + Sinh + Điểm tư duy
- Tính trung bình cộng điểm
- Sắp xếp theo tổng 3 môn / điểm tư duy (tăng/giảm dần)
- Thống kê: không liệt, có liệt, học bổng
- Danh sách học bổng: Top 5 mỗi khối (điểm XT ≥ 32, tư duy ≥ 70)
- Validation nghiêm ngặt (CCCD 12 số, điểm 0-10, tư duy 0-100)
- Lưu trữ JSON, 20 thí sinh mẫu

## Kiến trúc

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Nginx   │────▶│  React   │     │  Flask   │
│  :8080   │     │ Frontend │     │   API    │
│  proxy   │────▶│          │     │  :5001   │
└──────────┘     └──────────┘     └──────────┘
     Docker Compose (3 containers)
```

## Cấu trúc thư mục

```
├── backend/
│   ├── models/
│   │   ├── student.py          # ThiSinh, ThiSinhKhoiA, ThiSinhKhoiB
│   │   └── manage_student.py   # ManageStudent (CRUD + logic)
│   ├── validators.py           # Validation nghiêm ngặt
│   ├── app.py                  # Flask REST API
│   ├── main_console.py         # Chương trình Console
│   ├── data/sample_data.json   # 20 thí sinh mẫu
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/              # Dashboard, Students, Search, Reports, Scholarships
│   │   ├── components/         # Layout, StudentTable, StudentForm, StatCard
│   │   ├── api/studentApi.ts   # API client
│   │   └── types/student.ts    # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── nginx/
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Cài đặt & Chạy

### Cách 1: Docker Compose (Khuyến nghị)

```bash
# Build và chạy
docker compose up --build

# Truy cập: http://localhost:8080
```

### Cách 2: Chạy thủ công (Development)

```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
python app.py
# API chạy tại http://localhost:5001

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
# Web chạy tại http://localhost:3000
```

### Cách 3: Console (Terminal)

```bash
cd backend
pip install -r requirements.txt
python main_console.py
```

## OOP Class Diagram

```
ThiSinh (ABC)
├── cccd, so_bao_danh, ho_ten, dia_chi
├── tinh_diem_xet_tuyen() [abstract]
├── get_khoi(), get_diem_mon(), get_diem_tu_duy() [abstract]
├── is_liet(), tong_3_mon()
├── to_dict(), from_dict()
│
├── ThiSinhKhoiA
│   ├── toan, ly, hoa, diem_tu_duy
│   └── XT = Toán*1.5 + Lý + Hóa + tư_duy
│
└── ThiSinhKhoiB
    ├── toan, hoa, sinh, diem_tu_duy
    └── XT = Toán + Hóa*1.5 + Sinh + tư_duy

ManageStudent
├── them/sua/xoa_thi_sinh()
├── tim_kiem(), hien_thi_theo_khoi()
├── tinh_diem_xet_tuyen(), trung_binh_cong_diem()
├── sap_xep_3_mon(), sap_xep_tu_duy()
├── ds_khong_liet(), ds_hoc_bong()
└── thong_ke()
```

## API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | /api/students | Lấy danh sách (filter: ?khoi=A) |
| POST | /api/students | Thêm thí sinh |
| PUT | /api/students/:sbd | Sửa thí sinh |
| DELETE | /api/students/:sbd | Xóa thí sinh |
| GET | /api/students/search?q= | Tìm kiếm |
| GET | /api/reports/thong-ke | Thống kê tổng quan |
| GET | /api/reports/hoc-bong?khoi= | Danh sách học bổng |
| GET | /api/reports/sap-xep-3-mon?khoi=&order= | Sắp xếp 3 môn |
| GET | /api/reports/sap-xep-tu-duy?khoi=&order= | Sắp xếp tư duy |
| GET | /api/reports/khong-liet | Không liệt |

## Tech Stack

- **Backend**: Python 3.12, Flask, Gunicorn
- **Frontend**: React, TypeScript, Vite, Tailwind CSS v4, Framer Motion
- **Infrastructure**: Docker, Docker Compose, Nginx
- **Storage**: JSON file
