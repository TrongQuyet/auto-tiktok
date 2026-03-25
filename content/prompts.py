SCRIPT_GENERATION_PROMPT = """Bạn là một nhà sáng tạo nội dung TikTok viral. Hãy tạo kịch bản video ngắn bằng tiếng Việt CÓ DẤU.

Chủ đề: {niche}

Trả về CHỈ JSON hợp lệ với cấu trúc chính xác như sau:
{{
  "title": "tiêu đề nội bộ cho video",
  "script_segments": ["đoạn 1 lời đọc", "đoạn 2 lời đọc", ...],
  "caption": "Caption TikTok (tối đa 150 ký tự)",
  "hashtags": ["#tag1", "#tag2", ...],
  "search_queries": ["từ khóa tìm video trên pexels cho đoạn 1", ...]
}}

Quy tắc:
- 4-6 đoạn, mỗi đoạn 1-2 câu (5-10 giây khi đọc)
- Tổng kịch bản dưới 60 giây khi đọc
- Bắt đầu bằng một câu hook hấp dẫn ở đoạn 1
- Mảng search_queries PHẢI có cùng số lượng với script_segments
- search_queries phải là từ khóa tiếng Anh đơn giản để tìm video stock (ví dụ: "sunset ocean", "person walking city")
- Bao gồm #fyp và các hashtag liên quan đến chủ đề (5-8 tổng cộng)
- Caption bắt mắt và dưới 150 ký tự
- Nội dung script_segments viết bằng tiếng Việt CÓ DẤU đầy đủ
"""
