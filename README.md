# ChuyenDe2_Nhom02 

## Môn học: Chuyên đề 2 (GVHD: TS. Nguyễn Văn Hiếu)

## Thành viên nhóm 2
| Họ và tên | Lớp | MSSV |
|---------|-----|------|
| Nguyễn Ngọc Trung | 21KTMT2 | 106210257 |
| Lê Dương Khang | 21KTMT2 | 106210242 |
| Hoàng Bảo Long | 21KTMT1 | 106210049 |

---

## Giới thiệu đề tài
Đề tài xây dựng một **Hệ thống phát hiện làn đường và phương tiện từ video camera hành trình sử dụng xử lý ảnh và học sâu**, tập trung vào hai chức năng chính:
- **Nhận dạng làn đường**
- **Phát hiện và cảnh báo phương tiện phía trước**

Hệ thống được triển khai theo hướng kết hợp giữa **các kỹ thuật xử lý ảnh truyền thống** và **các mô hình học sâu**, nhằm đánh giá và so sánh hiệu quả của từng phương pháp trong điều kiện giao thông thực tế.

---

## Các thành phần chính của hệ thống
- **Mô-đun nhận dạng làn đường**
  - Phương pháp xử lý ảnh truyền thống
  - Mô hình học sâu **UFLDv2**
- **Mô-đun phát hiện phương tiện**
  - Mô hình **YOLOv8**
- **Mô-đun cảnh báo**
  - Lựa chọn phương tiện phía trước
  - Ước lượng khoảng cách tương đối
  - Sinh cảnh báo an toàn
    
## Cấu trúc repository
```text
ChuyenDe2_Nhom02/
├── CODE/                 # Mã nguồn của dự án
│   ├── UFLDv2/           # Mô-đun nhận dạng làn đường bằng học sâu (UFLDv2)
│   ├── YOLOv8/           # Mô-đun phát hiện phương tiện bằng YOLOv8
│   ├── XLA_Traditional/  # Mô-đun xử lý ảnh truyền thống (baseline)
│  
├── REPORT/               # Báo cáo cuối cùng của đề tài
│   └── ChuyenDe2_Nhom02.pdf
└── README.md             # Tệp mô tả tổng quan repository

## Video Demo
- **UFLDv2 nhận dạng làn đường**: https://dutudn-my.sharepoint.com/:f:/g/personal/106210257_sv1_dut_udn_vn/IgDkqveL0UWjQKGcZbx5Cw84Af4msyS_2QDg_X5APbPIVgQ?e=YZjI2X
- **Xử lý ảnh truyền thống nhận dạng làn đường**:
- **YOLOv8 phát hiện phương tiện và cảnh báo**:
- **Full Pipeline**:



