---
description: Tạo video TikTok mới — chạy pipeline đầy đủ hoặc chỉ tạo video (không upload)
argument-hint: "[niche] [--no-upload]"
---

Tôi muốn tạo một video TikTok mới cho dự án Auto TikTok Video Generator.

**Đầu vào từ người dùng:** `$ARGUMENTS`

Hãy thực hiện theo các bước sau:

1. **Đọc file config** `.env` (hoặc `.env.example` nếu `.env` chưa có) để biết các setting hiện tại — đặc biệt `DEFAULT_NICHE`, `AI_PROVIDER`, `VIDEO_SOURCE`.

2. **Xác định tham số:**
   - Nếu `$ARGUMENTS` có niche → dùng niche đó
   - Nếu `$ARGUMENTS` có `--no-upload` → bỏ qua bước upload TikTok
   - Nếu không có gì → hỏi người dùng muốn tạo video về chủ đề gì

3. **Chạy pipeline** bằng lệnh phù hợp:
   - Nếu đang dùng Docker: `docker compose exec app python main.py --niche "<niche>" [--no-upload]`
   - Nếu chạy local: `python main.py --niche "<niche>" [--no-upload]`

   Trước khi chạy, hãy kiểm tra xem Docker container có đang chạy không (`docker compose ps`).

4. **Theo dõi output** và báo cáo kết quả:
   - File video được tạo ở đâu
   - Có lỗi gì không (nếu có, suggest cách fix)
   - Nếu upload thành công → hiển thị link TikTok (nếu có trong log)

5. Nếu có lỗi liên quan đến API key bị thiếu → hướng dẫn người dùng thêm vào `.env`.
