SCRIPT_GENERATION_PROMPT = """Ban la mot nha sang tao noi dung TikTok viral. Hay tao kich ban video ngan bang tieng Viet.

Chu de: {niche}

Tra ve CHI JSON hop le voi cau truc chinh xac nhu sau:
{{
  "title": "tieu de noi bo cho video",
  "script_segments": ["doan 1 loi doc", "doan 2 loi doc", ...],
  "caption": "Caption TikTok (toi da 150 ky tu)",
  "hashtags": ["#tag1", "#tag2", ...],
  "search_queries": ["tu khoa tim video tren pexels cho doan 1", ...]
}}

Quy tac:
- 4-6 doan, moi doan 1-2 cau (5-10 giay khi doc)
- Tong kich ban duoi 60 giay khi doc
- Bat dau bang mot cau hook hap dan o doan 1
- Mang search_queries PHAI co cung so luong voi script_segments
- search_queries phai la tu khoa tieng Anh don gian de tim video stock (vi du: "sunset ocean", "person walking city")
- Bao gom #fyp va cac hashtag lien quan den chu de (5-8 tong cong)
- Caption bat mat va duoi 150 ky tu, viet bang tieng Viet khong dau
- Noi dung script_segments viet bang tieng Viet KHONG DAU de TTS doc dung
"""
