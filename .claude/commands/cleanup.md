---
description: Dọn dẹp temp files và output cũ — giải phóng dung lượng ổ cứng
argument-hint: "[temp|output|all]"
---

Tôi muốn dọn dẹp files trong dự án Auto TikTok Video Generator.

**Phạm vi:** `$ARGUMENTS` (mặc định: `temp` nếu không có)

### Trước khi xóa — luôn kiểm tra:
1. Chạy lệnh sau để xem dung lượng:
   ```bash
   du -sh temp/ output/ 2>/dev/null
   ```
2. Hiển thị số lượng files và tổng dung lượng cho người dùng thấy.
3. **Hỏi xác nhận** trước khi xóa bất kỳ thứ gì trong `output/`.

### Nếu `$ARGUMENTS` là `temp` hoặc trống:
Xóa toàn bộ nội dung trong `temp/` nhưng giữ lại thư mục:
```bash
find temp/ -type f -delete 2>/dev/null
find temp/ -mindepth 1 -type d -delete 2>/dev/null
```
An toàn — temp files là file tạm, không cần giữ.

### Nếu `$ARGUMENTS` là `output`:
Hiển thị danh sách video trong `output/` với kích thước và ngày tạo.
Hỏi người dùng muốn xóa tất cả hay chọn file cụ thể.
Chỉ xóa sau khi được xác nhận rõ ràng.

### Nếu `$ARGUMENTS` là `all`:
Thực hiện cleanup cả `temp/` và hỏi về `output/` như trên.

### Sau khi cleanup:
Hiển thị lại dung lượng đã giải phóng:
```bash
du -sh temp/ output/ 2>/dev/null
```
