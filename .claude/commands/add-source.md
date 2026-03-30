---
description: Scaffold nguồn stock footage mới — tạo client file, đăng ký vào web.py, thêm API key vào Settings
argument-hint: "<source-name>"
---

Tôi muốn thêm một nguồn stock footage mới vào dự án Auto TikTok Video Generator.

**Tên nguồn:** `$ARGUMENTS`

Nếu `$ARGUMENTS` trống, hỏi người dùng tên nguồn (ví dụ: `storyblocks`, `videvo`, `mazwai`).

Thực hiện theo đúng pattern của dự án:

### Bước 1 — Đọc file mẫu
Đọc `media/pexels_client.py` và `media/coverr_client.py` để hiểu interface chuẩn trước khi tạo file mới.

### Bước 2 — Tạo client file
Tạo `media/<source_name>_client.py` với:
- Async function `search_videos(query: str, count: int) -> list[dict]`
- Mỗi dict trong list phải có: `url`, `duration`, `width`, `height`, `thumbnail` (theo cùng schema với Pexels/Coverr)
- Dùng `aiohttp` cho HTTP requests (không dùng `requests` blocking)
- API key lấy từ `settings` object (không đọc `os.environ` trực tiếp)
- Logger: `logger = logging.getLogger(__name__)`
- Retry decorator `@retry` từ `tenacity` cho API calls

### Bước 3 — Cập nhật Settings
Mở `config.py`, thêm field API key mới vào `Settings` dataclass (ví dụ: `STORYBLOCKS_API_KEY: str = ""`).

### Bước 4 — Cập nhật .env.example
Thêm dòng API key vào `.env.example` với comment giải thích.

### Bước 5 — Đăng ký vào web.py
Đọc `web.py`, tìm chỗ xử lý `video_source` selection (nơi các nguồn Pexels/Pixabay/Coverr được import và gọi), thêm nguồn mới vào đó theo đúng pattern hiện có.

### Bước 6 — Báo cáo
Liệt kê tất cả files đã thay đổi và hướng dẫn người dùng:
1. Thêm API key vào `.env`
2. Test thử bằng cách chọn nguồn mới trong UI
