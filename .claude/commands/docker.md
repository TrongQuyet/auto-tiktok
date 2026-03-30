---
description: Quản lý Docker — restart, xem logs, rebuild khi cần
argument-hint: "[restart|logs|rebuild|status]"
---

Tôi muốn quản lý Docker cho dự án Auto TikTok Video Generator.

**Lệnh:** `$ARGUMENTS`

Xử lý theo từng trường hợp:

### Nếu `$ARGUMENTS` là `restart` hoặc trống:
Chạy `docker compose restart` rồi theo dõi logs 10 giây:
```bash
docker compose restart && docker compose logs --tail=30 -f
```
Giải thích: restart chỉ reload Python code, không cần rebuild image.

### Nếu `$ARGUMENTS` là `logs`:
```bash
docker compose logs --tail=50 -f
```
Theo dõi và tóm tắt nếu có lỗi xuất hiện.

### Nếu `$ARGUMENTS` là `rebuild`:
Cảnh báo người dùng: rebuild sẽ mất vài phút. Hỏi xác nhận trước, sau đó:
```bash
docker compose up --build -d
```
Chỉ cần rebuild khi: thêm package vào `requirements.txt`, sửa `Dockerfile`, hoặc thêm thư mục mới chưa có trong `volumes`.

### Nếu `$ARGUMENTS` là `status`:
```bash
docker compose ps
```
Hiển thị trạng thái các container và port đang mở.

### Sau khi chạy xong:
- Nếu thành công → thông báo Web UI: `http://localhost:8000` | noVNC: `http://localhost:6080`
- Nếu có lỗi → đọc log lỗi và suggest fix cụ thể
- Nếu container không start được → kiểm tra `.env` có đủ config chưa
