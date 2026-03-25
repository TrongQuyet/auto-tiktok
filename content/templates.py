import random

TEMPLATES = {
    "motivation": [
        {
            "title": "Tư duy thành công",
            "script_segments": [
                "Phần lớn mọi người bỏ cuộc ngay trước khi họ thành công. Đừng là số đông.",
                "Thành công không phụ thuộc vào tài năng. Mà là sự kiên trì và nỗ lực mỗi ngày.",
                "Nỗi đau bạn cảm thấy hôm nay sẽ là sức mạnh của bạn ngày mai.",
                "Đừng chờ đợi thời điểm hoàn hảo. Hãy nắm lấy thời điểm và biến nó thành hoàn hảo.",
                "Giới hạn duy nhất của bạn là câu chuyện bạn tự kể cho chính mình.",
            ],
            "caption": "Tư duy quyết định tương lai của bạn",
            "hashtags": ["#motivation", "#fyp", "#tưduy", "#thànhcông", "#nỗlực", "#độnglựcsống"],
            "search_queries": ["sunrise mountain", "person running", "gym workout", "city skyline night", "victory celebration"],
        },
        {
            "title": "Kỷ luật mỗi ngày",
            "script_segments": [
                "Kỷ luật là sự lựa chọn giữa thứ bạn muốn bây giờ và thứ bạn muốn nhất.",
                "Khi người khác còn ngủ, những người thành công đang âm thầm nỗ lực.",
                "Những tiến bộ nhỏ mỗi ngày sẽ dẫn đến những kết quả đáng kinh ngạc.",
                "Bạn không cần động lực. Bạn cần kỷ luật và một thói quen tốt.",
                "Một năm nữa, bạn sẽ ước gì mình đã bắt đầu từ hôm nay.",
            ],
            "caption": "Kỷ luật luôn thắng động lực",
            "hashtags": ["#kỷluật", "#fyp", "#thànhcông", "#nỗlựcmỗingày", "#độnglựcsống", "#tậptrung"],
            "search_queries": ["alarm clock morning", "person studying", "running track", "sunrise meditation", "calendar planning"],
        },
        {
            "title": "Tin vào bản thân",
            "script_segments": [
                "Mọi người đều nói điều đó là không thể. Nhưng họ đã làm được.",
                "Đối thủ lớn nhất của bạn là chính bạn của ngày hôm qua.",
                "Sự tự tin không phải là nghĩ mình giỏi hơn người khác. Mà là biết mình không cần so sánh.",
                "Thế giới sẽ nhường đường cho những ai biết mình đang đi đâu.",
            ],
            "caption": "Hãy tin vào bản thân khi không ai tin bạn",
            "hashtags": ["#tintưởng", "#fyp", "#bảnthân", "#motivation", "#tựtin", "#thànhcông"],
            "search_queries": ["person looking at horizon", "mountain climber", "mirror reflection", "walking forward road"],
        },
    ],
    "fun facts": [
        {
            "title": "Sự thật thú vị",
            "script_segments": [
                "Bạn có biết mật ong không bao giờ bị hỏng không? Các nhà khảo cổ đã tìm thấy mật ong ba nghìn năm tuổi vẫn còn ăn được.",
                "Bạch tuộc có ba trái tim và máu xanh. Hai trái tim bơm máu đến mang và một trái tim bơm máu đi khắp cơ thể.",
                "Một ngày trên sao Kim dài hơn một năm trên sao Kim. Mất hai trăm bốn mươi ba ngày Trái Đất để quay một vòng.",
                "Chuối có chứa chất phóng xạ tự nhiên vì chúng chứa kali. Nhưng đừng lo, bạn phải ăn mười triệu quả mới bị ảnh hưởng.",
            ],
            "caption": "Những sự thật sẽ khiến bạn bất ngờ",
            "hashtags": ["#sựthậtthúvị", "#fyp", "#bạncóbiết", "#khoahọc", "#thúvị", "#họctập"],
            "search_queries": ["honey jar golden", "octopus underwater", "planet venus space", "banana fruit tropical"],
        },
        {
            "title": "Thế giới động vật",
            "script_segments": [
                "Một nhóm hồng hạc được gọi là một sự rực rỡ. Đúng vậy, đó là tên thật.",
                "Bò có bạn thân tốt nhất và chúng bị căng thẳng khi bị tách rời nhau.",
                "Rái cá biển nắm tay nhau khi ngủ để không bị trôi dạt xa nhau.",
                "Voi là động vật duy nhất không thể nhảy. Nhưng chúng có thể giao tiếp bằng rung động mặt đất.",
                "Trái tim của tôm nằm trong đầu. Thiên nhiên thật kỳ diệu.",
            ],
            "caption": "Thế giới động vật kỳ diệu hơn bạn nghĩ",
            "hashtags": ["#độngvật", "#fyp", "#sựthậtthúvị", "#thiênnhiên", "#kỳdiệu", "#họctập"],
            "search_queries": ["flamingos pink lake", "cows field green", "sea otters floating", "elephant walking safari", "shrimp underwater"],
        },
    ],
    "life tips": [
        {
            "title": "Mẹo hay cho cuộc sống",
            "script_segments": [
                "Bật chế độ máy bay khi sạc điện thoại. Nó sẽ sạc nhanh gấp đôi.",
                "Khi không thể quyết định giữa hai lựa chọn, hãy tung đồng xu. Phản ứng của bạn khi đồng xu rơi sẽ cho bạn biết bạn thực sự muốn gì.",
                "Quy tắc hai phút: nếu việc gì mất dưới hai phút, hãy làm ngay. Điều này sẽ thay đổi năng suất của bạn.",
                "Uống một ly nước ngay khi thức dậy. Cơ thể bạn bị mất nước sau tám tiếng ngủ.",
                "Trước khi quyết định lớn, hãy tự hỏi: điều này có quan trọng sau năm năm nữa không? Nếu không, đừng dành quá năm phút cho nó.",
            ],
            "caption": "Những mẹo đơn giản thay đổi cuộc sống",
            "hashtags": ["#mẹohay", "#fyp", "#cuộcsống", "#mẹovặt", "#họcmới", "#pháttiểnbảnthân"],
            "search_queries": ["phone charging", "coin flip hand", "productive workspace", "glass water morning", "person thinking decision"],
        },
    ],
    "technology": [
        {
            "title": "Sự thật về công nghệ",
            "script_segments": [
                "Vi rút máy tính đầu tiên được tạo ra năm một nghìn chín trăm tám mươi sáu. Nó có tên là Brain và được hai anh em ở Pakistan tạo ra.",
                "Nhiều người trên thế giới có điện thoại hơn là có nhà vệ sinh. Công nghệ phát triển thật nhanh.",
                "Trung bình mỗi người dành hơn bốn tiếng một ngày cho điện thoại. Đó là sáu mươi ngày một năm nhìn vào màn hình.",
                "Chín mươi phần trăm dữ liệu của thế giới được tạo ra chỉ trong hai năm gần đây.",
                "Trang web đầu tiên trên thế giới vẫn còn hoạt động. Nó được tạo bởi Tim Berners Lee năm một nghìn chín trăm chín mươi mốt.",
            ],
            "caption": "Những sự thật về công nghệ khiến bạn bất ngờ",
            "hashtags": ["#côngnghệ", "#fyp", "#technology", "#sựthậtthúvị", "#digital", "#họctập"],
            "search_queries": ["retro computer", "smartphone hand", "person using phone", "data center servers", "old website computer"],
        },
    ],
}

# Default fallback for any niche not in templates
DEFAULT_TEMPLATE = {
    "title": "Những điều thú vị về {niche}",
    "script_segments": [
        "Đây là điều đáng kinh ngạc về {niche} mà hầu hết mọi người không biết.",
        "Các chuyên gia nói rằng {niche} là một trong những chủ đề hấp dẫn nhất thế giới hiện nay.",
        "Nếu bạn quan tâm đến {niche}, sự thật tiếp theo sẽ khiến bạn bất ngờ.",
        "Càng tìm hiểu về {niche}, bạn càng nhận ra còn rất nhiều điều để khám phá.",
        "Hãy chia sẻ video này với người yêu thích {niche}. Họ sẽ cảm ơn bạn.",
    ],
    "caption": "Bạn sẽ không tin những sự thật về {niche}",
    "hashtags": ["#fyp", "#sựthậtthúvị", "#viral", "#trending", "#bạncóbiết", "#thúvị"],
    "search_queries": ["beautiful landscape", "person amazed", "light bulb idea", "books library", "sharing phone"],
}


def get_template(niche: str) -> dict:
    """Get a random template for the given niche."""
    niche_lower = niche.lower().strip()

    # Check for exact or partial match
    for key, templates in TEMPLATES.items():
        if key in niche_lower or niche_lower in key:
            template = random.choice(templates)
            return template

    # Fallback: use default template with niche name inserted
    template = {
        k: (
            v.format(niche=niche) if isinstance(v, str)
            else [s.format(niche=niche) for s in v] if isinstance(v, list) and v and isinstance(v[0], str)
            else v
        )
        for k, v in DEFAULT_TEMPLATE.items()
    }
    return template
