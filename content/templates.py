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
        {
            "title": "Đừng bao giờ từ bỏ",
            "script_segments": [
                "Thomas Edison thất bại mười nghìn lần trước khi phát minh ra bóng đèn. Ông nói, tôi không thất bại, tôi chỉ tìm ra mười nghìn cách không hiệu quả.",
                "Jack Ma bị từ chối ba mươi lần khi xin việc. Kể cả KFC cũng không nhận ông. Giờ ông là tỷ phú.",
                "Mỗi lần bạn thất bại, bạn đang tiến gần hơn đến thành công. Thất bại không phải là kết thúc, mà là bài học.",
                "Người thành công không phải là người không bao giờ ngã. Mà là người luôn đứng dậy sau mỗi lần ngã.",
            ],
            "caption": "Thất bại là mẹ thành công",
            "hashtags": ["#đừngbỏcuộc", "#fyp", "#thấtbại", "#thànhcông", "#motivation", "#bàihọc"],
            "search_queries": ["person falling getting up", "light bulb invention", "businessman success", "phoenix rising"],
        },
        {
            "title": "Sức mạnh của thói quen",
            "script_segments": [
                "Chúng ta là những gì chúng ta lặp đi lặp lại. Sự xuất sắc không phải là hành động, mà là thói quen.",
                "Thức dậy sớm hơn một tiếng mỗi ngày. Sau một năm, bạn có thêm ba trăm sáu mươi lăm giờ. Đó là mười lăm ngày.",
                "Đọc mười trang sách mỗi ngày. Sau một năm, bạn đọc xong mười hai cuốn sách.",
                "Những thay đổi nhỏ tạo nên khác biệt lớn. Bắt đầu nhỏ, nhưng bắt đầu ngay.",
            ],
            "caption": "Thói quen nhỏ thay đổi cuộc đời",
            "hashtags": ["#thoiquen", "#fyp", "#pháttriểnbảnthân", "#thànhcông", "#kỷluật", "#mỗingày"],
            "search_queries": ["morning routine", "reading book", "sunrise alarm", "small steps progress"],
        },
    ],
    "finance": [
        {
            "title": "Quy tắc tiền bạc",
            "script_segments": [
                "Người giàu không làm việc vì tiền. Họ để tiền làm việc cho họ. Đó là sự khác biệt lớn nhất.",
                "Quy tắc năm mươi ba mươi hai mươi. Năm mươi phần trăm cho nhu cầu. Ba mươi phần trăm cho mong muốn. Hai mươi phần trăm để tiết kiệm.",
                "Đừng tiết kiệm những gì còn lại sau khi chi tiêu. Hãy chi tiêu những gì còn lại sau khi tiết kiệm.",
                "Thu nhập thụ động là chìa khóa tự do tài chính. Hãy tìm cách kiếm tiền ngay cả khi bạn đang ngủ.",
            ],
            "caption": "Quy tắc tiền bạc người giàu luôn áp dụng",
            "hashtags": ["#tàichính", "#fyp", "#tiềnbạc", "#làmgiàu", "#đầutư", "#tiếtkiệm"],
            "search_queries": ["money growing plant", "piggy bank savings", "businessman working", "passive income laptop"],
        },
        {
            "title": "Sai lầm tài chính tuổi 20",
            "script_segments": [
                "Tuổi hai mươi là thời điểm vàng để xây dựng nền tảng tài chính. Nhưng hầu hết mọi người lại bỏ lỡ.",
                "Sai lầm số một là không tiết kiệm sớm. Nếu bạn tiết kiệm một triệu mỗi tháng từ năm hai mươi tuổi, bạn sẽ có hàng tỷ khi về hưu.",
                "Sai lầm số hai là mua những thứ để gây ấn tượng với người khác. Xe đẹp, quần áo đắt tiền, nhưng tài khoản thì trống rỗng.",
                "Sai lầm số ba là không đầu tư vào bản thân. Kiến thức và kỹ năng là tài sản giá trị nhất bạn có.",
                "Hãy sống dưới khả năng tài chính của bạn. Sự giàu có thực sự đến từ khoảng cách giữa thu nhập và chi tiêu.",
            ],
            "caption": "Đừng mắc những sai lầm này ở tuổi 20",
            "hashtags": ["#tàichính", "#fyp", "#tuổi20", "#tiếtkiệm", "#đầutư", "#sailầm"],
            "search_queries": ["young person thinking money", "savings jar coins", "luxury car shopping", "student studying", "simple living"],
        },
        {
            "title": "Thói quen người giàu",
            "script_segments": [
                "Tám mươi phần trăm triệu phú thức dậy ít nhất hai tiếng trước khi đi làm. Họ dùng thời gian đó để đọc sách, tập thể dục và lên kế hoạch.",
                "Người giàu có nhiều nguồn thu nhập. Trung bình bảy nguồn. Đừng bao giờ phụ thuộc vào một nguồn duy nhất.",
                "Họ đầu tư trước, chi tiêu sau. Mỗi đồng kiếm được, họ đầu tư ít nhất hai mươi phần trăm.",
                "Người giàu đọc sách mỗi ngày. Trong khi người bình thường xem tivi bốn tiếng, người giàu đọc sách hai tiếng.",
            ],
            "caption": "Thói quen tạo nên triệu phú",
            "hashtags": ["#ngườigiàu", "#fyp", "#thoiquen", "#triệuphú", "#thànhcông", "#tàichính"],
            "search_queries": ["wealthy businessman morning", "multiple income streams", "investing stock market", "reading book library"],
        },
        {
            "title": "Cách tiết kiệm thông minh",
            "script_segments": [
                "Mẹo đầu tiên là tự động hóa tiết kiệm. Cài đặt chuyển tiền tự động vào tài khoản tiết kiệm ngay khi nhận lương.",
                "Áp dụng quy tắc hai mươi bốn giờ. Trước khi mua bất cứ thứ gì không cần thiết, hãy đợi hai mươi bốn giờ. Phần lớn bạn sẽ không mua nữa.",
                "Nấu ăn ở nhà thay vì ăn ngoài. Bạn có thể tiết kiệm ba đến năm triệu mỗi tháng chỉ với thay đổi này.",
                "Hủy những đăng ký dịch vụ bạn không dùng. Kiểm tra ngay bây giờ, bạn sẽ ngạc nhiên đấy.",
            ],
            "caption": "Tiết kiệm thông minh không khó như bạn nghĩ",
            "hashtags": ["#tiếtkiệm", "#fyp", "#tàichính", "#mẹohay", "#quảnlýtiền", "#thôngminh"],
            "search_queries": ["piggy bank money", "cooking at home kitchen", "phone subscription cancel", "waiting patience clock"],
        },
        {
            "title": "Đầu tư cho người mới",
            "script_segments": [
                "Đầu tư không phải chỉ dành cho người giàu. Bạn có thể bắt đầu với chỉ một trăm nghìn đồng.",
                "Quy tắc quan trọng nhất là đa dạng hóa. Đừng bỏ tất cả trứng vào một giỏ.",
                "Lãi kép là phép màu thứ tám của thế giới. Ai hiểu nó thì kiếm được nó. Ai không hiểu thì phải trả nó.",
                "Đầu tư vào kiến thức trước khi đầu tư vào thị trường. Đọc ít nhất ba cuốn sách về đầu tư trước khi bắt đầu.",
            ],
            "caption": "Bắt đầu đầu tư từ hôm nay",
            "hashtags": ["#đầutư", "#fyp", "#tàichính", "#lãikép", "#chứngkhoán", "#ngườimới"],
            "search_queries": ["stock market chart", "coins growing plant", "reading finance book", "diverse portfolio"],
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
        {
            "title": "Bí ẩn cơ thể người",
            "script_segments": [
                "Mỗi ngày cơ thể bạn tạo ra hai lít nước bọt. Một năm đủ để đầy hai bồn tắm.",
                "Não người sử dụng hai mươi phần trăm tổng năng lượng cơ thể. Mặc dù nó chỉ chiếm hai phần trăm trọng lượng.",
                "Xương của bạn cứng hơn thép năm lần nếu so sánh cùng trọng lượng.",
                "Mắt người có thể phân biệt mười triệu màu sắc khác nhau. Nhưng não bạn chỉ ghi nhớ một phần nhỏ.",
                "Nếu trải tất cả mạch máu trong cơ thể ra, chúng dài đủ để quấn quanh Trái Đất hai lần rưỡi.",
            ],
            "caption": "Cơ thể bạn kỳ diệu hơn bạn tưởng",
            "hashtags": ["#cơthểngười", "#fyp", "#khoahọc", "#sựthật", "#bíẩn", "#thúvị"],
            "search_queries": ["human brain neuron", "human eye close up", "blood cells flowing", "human skeleton bones", "human body anatomy"],
        },
        {
            "title": "Sự thật về vũ trụ",
            "script_segments": [
                "Ánh sáng Mặt Trời mất tám phút để đến Trái Đất. Nên khi bạn nhìn Mặt Trời, bạn đang nhìn tám phút trước.",
                "Trên sao Kim, mưa là axit sunfuric. Và nó bốc hơi trước khi chạm đất vì quá nóng.",
                "Có nhiều ngôi sao trong vũ trụ hơn số hạt cát trên tất cả các bãi biển Trái Đất.",
                "Một ngày trên sao Mộc chỉ dài mười tiếng. Nhưng một năm dài bằng mười hai năm Trái Đất.",
            ],
            "caption": "Vũ trụ rộng lớn hơn bạn tưởng tượng",
            "hashtags": ["#vũtrụ", "#fyp", "#khoahọc", "#sựthật", "#ngoàikhônggian", "#bíẩn"],
            "search_queries": ["sun rays earth", "venus planet surface", "stars galaxy milky way", "jupiter planet space"],
        },
        {
            "title": "Sự thật lịch sử thú vị",
            "script_segments": [
                "Nữ hoàng Cleopatra sống gần thời đại iPhone hơn là thời xây kim tự tháp. Kim tự tháp xưa hơn bà hai nghìn năm.",
                "Trong Thế chiến thứ hai, quân đội Anh đã tạo ra xe tăng bằng bóng bay để đánh lừa quân Đức.",
                "Napoleon không hề thấp. Ông cao một mét sáu tám, cao hơn trung bình người Pháp thời đó.",
                "Vạn Lý Trường Thành không thể nhìn thấy từ vũ trụ bằng mắt thường. Đó là một huyền thoại sai.",
            ],
            "caption": "Lịch sử thú vị hơn sách giáo khoa",
            "hashtags": ["#lịchsử", "#fyp", "#sựthật", "#thúvị", "#bạncóbiết", "#kiếnthức"],
            "search_queries": ["cleopatra egypt", "world war tank", "napoleon portrait", "great wall china"],
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
        {
            "title": "Kỹ năng giao tiếp",
            "script_segments": [
                "Khi ai đó nói chuyện, hãy lặp lại ý chính của họ. Họ sẽ cảm thấy được lắng nghe và tin tưởng bạn hơn.",
                "Gọi tên người đối diện trong cuộc trò chuyện. Tên của một người là âm thanh ngọt ngào nhất với họ.",
                "Im lặng là vũ khí mạnh nhất trong đàm phán. Khi bạn im lặng, người khác sẽ tự lấp đầy khoảng trống.",
                "Nói chậm lại. Những người nói chậm và rõ ràng được đánh giá là thông minh và đáng tin cậy hơn.",
            ],
            "caption": "Học cách giao tiếp như người thành công",
            "hashtags": ["#giaotiếp", "#fyp", "#kỹnăng", "#thànhcông", "#đàmphán", "#mẹohay"],
            "search_queries": ["two people talking", "business negotiation", "listening carefully", "public speaking"],
        },
        {
            "title": "Quản lý thời gian",
            "script_segments": [
                "Chia ngày thành các block chín mươi phút. Não bộ chỉ tập trung tối đa chín mươi phút trước khi cần nghỉ.",
                "Làm việc khó nhất vào buổi sáng. Năng lượng và ý chí của bạn cao nhất lúc này.",
                "Nói không nhiều hơn. Mỗi lần bạn nói có với thứ không quan trọng, bạn đang nói không với thứ quan trọng.",
                "Tắt thông báo điện thoại khi làm việc. Mỗi lần bị gián đoạn, bạn mất hai mươi ba phút để tập trung lại.",
            ],
            "caption": "Quản lý thời gian như CEO",
            "hashtags": ["#quảnlýthờigian", "#fyp", "#năngsất", "#tậptrung", "#thànhcông", "#mẹohay"],
            "search_queries": ["clock time management", "morning work desk", "saying no hand", "phone notification off"],
        },
    ],
    "psychology": [
        {
            "title": "Tâm lý học thú vị",
            "script_segments": [
                "Hiệu ứng gương. Khi bạn mỉm cười với ai, họ sẽ tự động mỉm cười lại. Não bộ không thể kiểm soát điều này.",
                "Người ta nhớ cảm xúc nhiều hơn lời nói. Họ sẽ quên bạn nói gì, nhưng không bao giờ quên bạn khiến họ cảm thấy thế nào.",
                "Nếu bạn muốn ai đó thích bạn, hãy nhờ họ giúp một việc nhỏ. Đây gọi là hiệu ứng Benjamin Franklin.",
                "Màu đỏ khiến bạn ăn nhiều hơn. Đó là lý do hầu hết nhà hàng fast food dùng màu đỏ trong logo.",
            ],
            "caption": "Tâm lý học giúp bạn hiểu con người",
            "hashtags": ["#tâmlýhọc", "#fyp", "#tâmlý", "#hiệuứng", "#thúvị", "#conngười"],
            "search_queries": ["person smiling mirror", "emotional connection", "helping hand", "red restaurant logo"],
        },
        {
            "title": "Ngôn ngữ cơ thể",
            "script_segments": [
                "Bảy mươi phần trăm giao tiếp là phi ngôn ngữ. Cơ thể bạn đang nói nhiều hơn miệng bạn.",
                "Khi ai đó khoanh tay, họ đang tự bảo vệ mình hoặc không đồng ý. Nhưng đôi khi chỉ vì họ lạnh.",
                "Nhìn vào mắt người đối diện sáu mươi đến bảy mươi phần trăm thời gian trò chuyện. Ít hơn là thiếu tự tin. Nhiều hơn là đe dọa.",
                "Chân thường chỉ về hướng bạn muốn đi. Nếu chân ai đó chỉ ra cửa, họ muốn kết thúc cuộc trò chuyện.",
                "Nghiêng đầu nhẹ khi lắng nghe thể hiện sự quan tâm và đồng cảm.",
            ],
            "caption": "Đọc ngôn ngữ cơ thể như chuyên gia",
            "hashtags": ["#ngônngữcơthể", "#fyp", "#tâmlý", "#giaotiếp", "#bíquyết", "#kỹnăng"],
            "search_queries": ["body language crossed arms", "eye contact conversation", "feet direction walking", "head tilt listening", "nonverbal communication"],
        },
        {
            "title": "Hiệu ứng tâm lý trong cuộc sống",
            "script_segments": [
                "Hiệu ứng Dunning Kruger. Người biết ít thường nghĩ mình biết nhiều. Người biết nhiều lại nghĩ mình biết ít.",
                "Hiệu ứng neo. Khi bạn thấy giá gốc năm trăm nghìn giảm còn hai trăm nghìn, bạn nghĩ đó là hời. Dù món đồ chỉ đáng một trăm nghìn.",
                "Hiệu ứng đám đông. Khi bạn thấy quán nào đông khách, bạn tự động nghĩ quán đó ngon. Dù chưa từng ăn.",
                "Hiệu ứng xác nhận. Bạn chỉ tìm kiếm thông tin ủng hộ quan điểm sẵn có của mình và bỏ qua những gì trái ngược.",
            ],
            "caption": "Bạn đang bị tâm lý đánh lừa mỗi ngày",
            "hashtags": ["#tâmlýhọc", "#fyp", "#hiệuứng", "#tưduy", "#thúvị", "#khoahọc"],
            "search_queries": ["confused person thinking", "sale price tag discount", "crowded restaurant queue", "search filter bubble"],
        },
    ],
    "health": [
        {
            "title": "Thói quen sức khỏe",
            "script_segments": [
                "Đi bộ ba mươi phút mỗi ngày giảm năm mươi phần trăm nguy cơ bệnh tim. Không cần chạy marathon, chỉ cần đi bộ.",
                "Ngủ đủ bảy đến tám tiếng mỗi đêm. Thiếu ngủ làm giảm trí nhớ, tăng cân và tăng nguy cơ trầm cảm.",
                "Uống hai lít nước mỗi ngày. Hầu hết mọi người bị mất nước mà không biết. Dấu hiệu là mệt mỏi và đau đầu.",
                "Ngồi lâu nguy hiểm ngang hút thuốc. Cứ mỗi ba mươi phút, hãy đứng dậy và vận động hai phút.",
            ],
            "caption": "Thói quen nhỏ cho sức khỏe lớn",
            "hashtags": ["#sứckhỏe", "#fyp", "#thoiquen", "#khoẻmạnh", "#đibộ", "#ngủđủgiấc"],
            "search_queries": ["person walking park", "sleeping peacefully", "drinking water glass", "standing desk office"],
        },
        {
            "title": "Bí quyết ngủ ngon",
            "script_segments": [
                "Không dùng điện thoại một tiếng trước khi ngủ. Ánh sáng xanh từ màn hình ức chế melatonin, hormone giúp bạn ngủ.",
                "Giữ phòng ngủ mát, khoảng mười tám đến hai mươi hai độ. Cơ thể cần hạ nhiệt độ để vào giấc ngủ sâu.",
                "Ngủ và thức dậy cùng một giờ mỗi ngày, kể cả cuối tuần. Đồng hồ sinh học của bạn cần sự nhất quán.",
                "Nếu không ngủ được sau hai mươi phút, hãy ra khỏi giường. Đọc sách nhàm chán cho đến khi buồn ngủ rồi quay lại.",
            ],
            "caption": "Bí quyết để ngủ ngon mỗi đêm",
            "hashtags": ["#ngủngon", "#fyp", "#sứckhỏe", "#giấcngủ", "#mẹohay", "#khoẻmạnh"],
            "search_queries": ["phone screen blue light", "cool bedroom temperature", "alarm clock morning routine", "reading book bed night"],
        },
    ],
    "love": [
        {
            "title": "Sự thật về tình yêu",
            "script_segments": [
                "Não bộ người đang yêu giống hệt não bộ người nghiện. Cùng vùng não được kích hoạt và cùng loại hormone được tiết ra.",
                "Trung bình một người yêu bảy lần trước khi kết hôn. Mỗi lần là một bài học giúp bạn hiểu mình hơn.",
                "Ôm ai đó hơn hai mươi giây sẽ giải phóng oxytocin. Hormone này tạo sự gắn kết và tin tưởng.",
                "Những cặp đôi cười cùng nhau nhiều thường mạnh mẽ hơn. Vì tiếng cười tạo ra kết nối sâu hơn lời nói.",
            ],
            "caption": "Khoa học đằng sau tình yêu",
            "hashtags": ["#tìnhyêu", "#fyp", "#tâmlý", "#love", "#cặpđôi", "#sựthật"],
            "search_queries": ["couple holding hands sunset", "brain love chemistry", "couple hugging", "couple laughing together"],
        },
        {
            "title": "Dấu hiệu tình yêu thực sự",
            "script_segments": [
                "Tình yêu thực sự không phải là bướm trong bụng. Mà là cảm giác bình yên khi ở bên cạnh nhau.",
                "Người yêu bạn thật sự sẽ không cố thay đổi bạn. Họ chấp nhận bạn, kể cả những phần không hoàn hảo.",
                "Họ nhớ những chi tiết nhỏ. Món ăn yêu thích, câu chuyện bạn kể tuần trước, điều khiến bạn cười.",
                "Tình yêu thật không cần phải chứng minh trên mạng xã hội. Nó được thể hiện trong những hành động nhỏ hàng ngày.",
            ],
            "caption": "Tình yêu thật khác xa phim ảnh",
            "hashtags": ["#tìnhyêu", "#fyp", "#yêuthương", "#cặpđôi", "#hạnhphúc", "#tìnhcảm"],
            "search_queries": ["couple peaceful morning", "accepting partner", "remembering details note", "couple cooking together"],
        },
    ],
    "philosophy": [
        {
            "title": "Triết lý sống",
            "script_segments": [
                "Bạn không thể kiểm soát những gì xảy ra với bạn. Nhưng bạn có thể kiểm soát cách bạn phản ứng. Đó là triết lý Khắc kỷ.",
                "Cuộc sống ngắn không phải vì nó ngắn. Mà vì chúng ta lãng phí quá nhiều thời gian. Seneca nói điều này hai nghìn năm trước.",
                "Đừng so sánh chương một của bạn với chương hai mươi của người khác. Mỗi người có một hành trình riêng.",
                "Hạnh phúc không phải là đích đến. Mà là cách bạn đi trên hành trình.",
            ],
            "caption": "Triết lý sống mà ai cũng nên biết",
            "hashtags": ["#triếtlý", "#fyp", "#cuộcsống", "#khắckỷ", "#hạnhphúc", "#tưduy"],
            "search_queries": ["stoic statue thinking", "hourglass time passing", "different paths journey", "peaceful person meditating"],
        },
        {
            "title": "Lời dạy của người xưa",
            "script_segments": [
                "Khổng Tử nói: Hành trình ngàn dặm bắt đầu từ một bước chân. Đừng sợ hành trình dài, hãy sợ không bắt đầu.",
                "Lão Tử nói: Biết người là khôn ngoan. Biết mình là giác ngộ. Trước khi muốn thay đổi thế giới, hãy hiểu bản thân.",
                "Phật nói: Giữ tâm bình an giữa nghìn sóng gió. Mọi khổ đau đều bắt nguồn từ sự bám víu.",
                "Marcus Aurelius nói: Hạnh phúc phụ thuộc vào chất lượng suy nghĩ của bạn. Hãy bảo vệ tâm trí như bảo vệ thành trì.",
            ],
            "caption": "Lời dạy ngàn năm vẫn đúng đến hôm nay",
            "hashtags": ["#triếtlý", "#fyp", "#lờidạy", "#khổngtử", "#tưduy", "#cuộcsống"],
            "search_queries": ["confucius statue", "zen garden peaceful", "buddha meditation", "roman emperor statue"],
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
            "hashtags": ["#côngnghệ", "#fyp", "#technology", "#sựthật", "#digital", "#họctập"],
            "search_queries": ["retro computer", "smartphone hand", "person using phone", "data center servers", "old website computer"],
        },
        {
            "title": "AI đang thay đổi thế giới",
            "script_segments": [
                "Trí tuệ nhân tạo có thể viết code, vẽ tranh, sáng tác nhạc và thậm chí chẩn đoán bệnh chính xác hơn bác sĩ.",
                "Chat GPT đạt một trăm triệu người dùng trong hai tháng. Nhanh hơn bất kỳ ứng dụng nào trong lịch sử.",
                "Đến năm hai nghìn ba mươi, AI có thể thay thế ba trăm triệu việc làm trên toàn thế giới. Nhưng cũng tạo ra hàng triệu việc mới.",
                "Không phải AI lấy việc của bạn. Mà là người biết dùng AI sẽ lấy việc của người không biết.",
            ],
            "caption": "AI đang thay đổi mọi thứ",
            "hashtags": ["#AI", "#fyp", "#côngnghệ", "#trítuệnhântạo", "#tươnglai", "#ChatGPT"],
            "search_queries": ["artificial intelligence robot", "chatgpt phone screen", "futuristic technology", "person using ai computer"],
        },
    ],
    "mystery": [
        {
            "title": "Bí ẩn chưa có lời giải",
            "script_segments": [
                "Tam giác Bermuda. Hơn năm mươi tàu và hai mươi máy bay đã biến mất ở đây mà không để lại dấu vết nào.",
                "Tín hiệu Wow. Năm một nghìn chín trăm bảy mươi bảy, một kính viễn vọng nhận được tín hiệu radio mạnh từ ngoài vũ trụ. Không ai biết nó từ đâu.",
                "Đá di chuyển ở Thung lũng Chết. Những tảng đá nặng hàng trăm ký tự di chuyển trên sa mạc mà không ai chạm vào.",
                "Bản thảo Voynich. Một cuốn sách bốn trăm năm tuổi viết bằng ngôn ngữ mà không ai trên Trái Đất đọc được.",
            ],
            "caption": "Những bí ẩn khoa học chưa thể giải thích",
            "hashtags": ["#bíẩn", "#fyp", "#mystery", "#khoahọc", "#thếgiới", "#kỳlạ"],
            "search_queries": ["bermuda triangle ocean", "space signal telescope", "death valley moving rocks", "voynich manuscript book"],
        },
        {
            "title": "Những nơi bí ẩn nhất thế giới",
            "script_segments": [
                "Khu Vực năm mươi mốt ở Nevada, Mỹ. Căn cứ quân sự tuyệt mật. Nhiều người tin rằng chính phủ giấu UFO ở đây.",
                "Đảo Phục Sinh. Gần chín trăm bức tượng đá khổng lồ trên một hòn đảo hẻo lánh. Không ai biết chắc người xưa làm thế nào.",
                "Rừng tự tử Aokigahara ở Nhật Bản. Khu rừng yên tĩnh đến mức la bàn không hoạt động vì đá núi lửa.",
                "Cánh đồng Chum ở Lào. Hàng nghìn chum đá khổng lồ nằm rải rác. Các nhà khoa học vẫn tranh cãi về mục đích của chúng.",
            ],
            "caption": "Những nơi kỳ bí nhất hành tinh",
            "hashtags": ["#bíẩn", "#fyp", "#travel", "#mystery", "#kỳlạ", "#thếgiới"],
            "search_queries": ["area 51 desert", "easter island statues", "aokigahara forest japan", "plain of jars laos"],
        },
    ],
    "quotes": [
        {
            "title": "Danh ngôn thay đổi cuộc đời",
            "script_segments": [
                "Steve Jobs nói: Thời gian của bạn có hạn. Đừng lãng phí nó để sống cuộc đời của người khác.",
                "Albert Einstein nói: Trí tưởng tượng quan trọng hơn kiến thức. Kiến thức có giới hạn, trí tưởng tượng thì không.",
                "Bruce Lee nói: Tôi không sợ người tập mười nghìn cú đá. Tôi sợ người tập một cú đá mười nghìn lần.",
                "Mark Twain nói: Hai ngày quan trọng nhất trong đời bạn là ngày bạn sinh ra và ngày bạn tìm ra lý do tại sao.",
            ],
            "caption": "Những câu nói đáng suy ngẫm",
            "hashtags": ["#danhngôn", "#fyp", "#motivation", "#quoteoftheday", "#cuộcsống", "#tưduy"],
            "search_queries": ["steve jobs presentation", "einstein thinking", "bruce lee martial arts", "typewriter quote"],
        },
        {
            "title": "Danh ngôn về sự kiên trì",
            "script_segments": [
                "Winston Churchill nói: Thành công là đi từ thất bại này đến thất bại khác mà không mất đi nhiệt huyết.",
                "Walt Disney nói: Tất cả ước mơ đều có thể thành hiện thực nếu bạn có can đảm theo đuổi chúng.",
                "Nelson Mandela nói: Mọi thứ đều có vẻ không thể cho đến khi nó được thực hiện.",
                "Confucius nói: Không quan trọng bạn đi chậm thế nào, miễn là bạn không dừng lại.",
            ],
            "caption": "Kiên trì là chìa khóa mọi thành công",
            "hashtags": ["#danhngôn", "#fyp", "#kiêntrì", "#thànhcông", "#nỗlực", "#quoteoftheday"],
            "search_queries": ["churchill portrait", "walt disney castle", "nelson mandela", "turtle slow steady"],
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
            return random.choice(templates)

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
