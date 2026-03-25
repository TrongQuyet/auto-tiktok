import random

TEMPLATES = {
    "motivation": [
        {
            "title": "Tu duy thanh cong",
            "script_segments": [
                "Phan lon moi nguoi bo cuoc ngay truoc khi ho thanh cong. Dung la so dong.",
                "Thanh cong khong phu thuoc vao tai nang. Ma la su kien tri va no luc moi ngay.",
                "Noi dau ban cam thay hom nay se la suc manh cua ban ngay mai.",
                "Dung cho doi thoi diem hoan hao. Hay nam lay thoi diem va bien no thanh hoan hao.",
                "Gioi han duy nhat cua ban la cau chuyen ban tu ke cho chinh minh.",
            ],
            "caption": "Tu duy quyet dinh tuong lai cua ban",
            "hashtags": ["#motivation", "#fyp", "#tuduy", "#thanhcong", "#noiluc", "#donglucsong"],
            "search_queries": ["sunrise mountain", "person running", "gym workout", "city skyline night", "victory celebration"],
        },
        {
            "title": "Ky luat moi ngay",
            "script_segments": [
                "Ky luat la su lua chon giua thu ban muon bay gio va thu ban muon nhat.",
                "Khi nguoi khac con ngu, nhung nguoi thanh cong dang am tham no luc.",
                "Nhung tien bo nho moi ngay se dan den nhung ket qua dang kinh ngac.",
                "Ban khong can dong luc. Ban can ky luat va mot thoi quen tot.",
                "Mot nam nua, ban se uoc gi minh da bat dau tu hom nay.",
            ],
            "caption": "Ky luat luon thang dong luc",
            "hashtags": ["#kyluat", "#fyp", "#thanhcong", "#noilucmoingay", "#donglucsong", "#taptrung"],
            "search_queries": ["alarm clock morning", "person studying", "running track", "sunrise meditation", "calendar planning"],
        },
        {
            "title": "Tin vao ban than",
            "script_segments": [
                "Moi nguoi deu noi dieu do la khong the. Nhung ho da lam duoc.",
                "Doi thu lon nhat cua ban la chinh ban cua ngay hom qua.",
                "Su tu tin khong phai la nghi minh gioi hon nguoi khac. Ma la biet minh khong can so sanh.",
                "The gioi se nhuong duong cho nhung ai biet minh dang di dau.",
            ],
            "caption": "Hay tin vao ban than khi khong ai tin ban",
            "hashtags": ["#tintuong", "#fyp", "#banthan", "#motivation", "#tutin", "#thanhcong"],
            "search_queries": ["person looking at horizon", "mountain climber", "mirror reflection", "walking forward road"],
        },
    ],
    "fun facts": [
        {
            "title": "Su that thu vi",
            "script_segments": [
                "Ban co biet mat ong khong bao gio bi hong khong? Cac nha khao co da tim thay mat ong ba nghin nam tuoi van con an duoc.",
                "Bach tuoc co ba trai tim va mau xanh. Hai trai tim bom mau den mang va mot trai tim bom mau di khap co the.",
                "Mot ngay tren sao Kim dai hon mot nam tren sao Kim. Mat hai tram bon muoi ba ngay Trai Dat de quay mot vong.",
                "Chuoi co chua chat phong xa tu nhien vi chung chua kali. Nhung dung lo, ban phai an muoi trieu qua moi bi anh huong.",
            ],
            "caption": "Nhung su that se khien ban bat ngo",
            "hashtags": ["#suthatthuvi", "#fyp", "#bancobiet", "#khoahoc", "#thuvi", "#hoctap"],
            "search_queries": ["honey jar golden", "octopus underwater", "planet venus space", "banana fruit tropical"],
        },
        {
            "title": "The gioi dong vat",
            "script_segments": [
                "Mot nhom hong hac duoc goi la mot su ruc ro. Dung vay, do la ten that.",
                "Bo co ban than tot nhat va chung bi cang thang khi bi tach roi nhau.",
                "Rai ca bien nam tay nhau khi ngu de khong bi troi dat xa nhau.",
                "Voi la dong vat duy nhat khong the nhay. Nhung chung co the giao tiep bang rung dong mat dat.",
                "Trai tim cua tom nam trong dau. Thien nhien that ky dieu.",
            ],
            "caption": "The gioi dong vat ky dieu hon ban nghi",
            "hashtags": ["#dongvat", "#fyp", "#suthatthuvi", "#thiennhien", "#kydieu", "#hoctap"],
            "search_queries": ["flamingos pink lake", "cows field green", "sea otters floating", "elephant walking safari", "shrimp underwater"],
        },
    ],
    "life tips": [
        {
            "title": "Meo hay cho cuoc song",
            "script_segments": [
                "Bat che do may bay khi sac dien thoai. No se sac nhanh gap doi.",
                "Khi khong the quyet dinh giua hai lua chon, hay tung dong xu. Phan ung cua ban khi dong xu roi se cho ban biet ban thuc su muon gi.",
                "Quy tac hai phut: neu viec gi mat duoi hai phut, hay lam ngay. Dieu nay se thay doi nang suat cua ban.",
                "Uong mot ly nuoc ngay khi thuc day. Co the ban bi mat nuoc sau tam tieng ngu.",
                "Truoc khi quyet dinh lon, hay tu hoi: dieu nay co quan trong sau nam nam nua khong? Neu khong, dung danh qua nam phut cho no.",
            ],
            "caption": "Nhung meo don gian thay doi cuoc song",
            "hashtags": ["#meohay", "#fyp", "#cuocsong", "#meovat", "#hocmoi", "#phattrienthanban"],
            "search_queries": ["phone charging", "coin flip hand", "productive workspace", "glass water morning", "person thinking decision"],
        },
    ],
    "technology": [
        {
            "title": "Su that ve cong nghe",
            "script_segments": [
                "Vi rut may tinh dau tien duoc tao ra nam mot nghin chin tram tam muoi sau. No co ten la Brain va duoc hai anh em o Pakistan tao ra.",
                "Nhieu nguoi tren the gioi co dien thoai hon la co nha ve sinh. Cong nghe phat trien that nhanh.",
                "Trung binh moi nguoi danh hon bon tieng mot ngay cho dien thoai. Do la sau muoi ngay mot nam nhin vao man hinh.",
                "Chin muoi phan tram du lieu cua the gioi duoc tao ra chi trong hai nam gan day.",
                "Trang web dau tien tren the gioi van con hoat dong. No duoc tao boi Tim Berners Lee nam mot nghin chin tram chin muoi mot.",
            ],
            "caption": "Nhung su that ve cong nghe khien ban bat ngo",
            "hashtags": ["#congnghe", "#fyp", "#technology", "#suthatthuvi", "#digital", "#hoctap"],
            "search_queries": ["retro computer", "smartphone hand", "person using phone", "data center servers", "old website computer"],
        },
    ],
}

# Default fallback for any niche not in templates
DEFAULT_TEMPLATE = {
    "title": "Nhung dieu thu vi ve {niche}",
    "script_segments": [
        "Day la dieu dang kinh ngac ve {niche} ma hau het moi nguoi khong biet.",
        "Cac chuyen gia noi rang {niche} la mot trong nhung chu de hap dan nhat the gioi hien nay.",
        "Neu ban quan tam den {niche}, su that tiep theo se khien ban bat ngo.",
        "Cang tim hieu ve {niche}, ban cang nhan ra con rat nhieu dieu de kham pha.",
        "Hay chia se video nay voi nguoi yeu thich {niche}. Ho se cam on ban.",
    ],
    "caption": "Ban se khong tin nhung su that ve {niche}",
    "hashtags": ["#fyp", "#suthatthuvi", "#viral", "#trending", "#bancobiet", "#thuvi"],
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
