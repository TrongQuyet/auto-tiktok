import random
from collections import deque

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
                "Hãy bắt đầu từ hôm nay. Phiên bản tốt nhất của bạn đang chờ ở phía trước.",
            ],
            "caption": "Tư duy quyết định tương lai của bạn",
            "hashtags": ["#motivation", "#fyp", "#tưduy", "#thànhcông", "#nỗlực", "#độnglựcsống"],
            "search_queries": ["sunrise mountain", "person running", "gym workout", "city skyline night", "victory celebration", "new beginning"],
        },
        {
            "title": "Kỷ luật mỗi ngày",
            "script_segments": [
                "Kỷ luật là sự lựa chọn giữa thứ bạn muốn bây giờ và thứ bạn muốn nhất.",
                "Khi người khác còn ngủ, những người thành công đang âm thầm nỗ lực.",
                "Những tiến bộ nhỏ mỗi ngày sẽ dẫn đến những kết quả đáng kinh ngạc.",
                "Bạn không cần động lực. Bạn cần kỷ luật và một thói quen tốt.",
                "Một năm nữa, bạn sẽ ước gì mình đã bắt đầu từ hôm nay.",
                "Kỷ luật là cây cầu giữa mục tiêu và thành tựu.",
            ],
            "caption": "Kỷ luật luôn thắng động lực",
            "hashtags": ["#kỷluật", "#fyp", "#thànhcông", "#nỗlựcmỗingày", "#độnglựcsống", "#tậptrung"],
            "search_queries": ["alarm clock morning", "person studying", "running track", "sunrise meditation", "calendar planning", "focused work"],
        },
        {
            "title": "Đừng bao giờ từ bỏ",
            "script_segments": [
                "Thomas Edison thất bại mười nghìn lần trước khi phát minh ra bóng đèn. Ông nói, tôi không thất bại, tôi chỉ tìm ra mười nghìn cách không hiệu quả.",
                "Jack Ma bị từ chối ba mươi lần khi xin việc. Kể cả KFC cũng không nhận ông. Giờ ông là tỷ phú.",
                "Mỗi lần bạn thất bại, bạn đang tiến gần hơn đến thành công.",
                "J.K. Rowling bị mười hai nhà xuất bản từ chối trước khi Harry Potter được in. Giờ bà là tác giả tỷ phú.",
                "Người thành công không phải là người không bao giờ ngã. Mà là người luôn đứng dậy sau mỗi lần ngã.",
                "Thất bại không phải là kết thúc. Mà là bài học quý giá nhất.",
            ],
            "caption": "Thất bại là mẹ thành công",
            "hashtags": ["#đừngbỏcuộc", "#fyp", "#thấtbại", "#thànhcông", "#motivation", "#bàihọc"],
            "search_queries": ["person falling getting up", "light bulb invention", "businessman success", "writer typing", "phoenix rising", "overcoming obstacles"],
        },
        {
            "title": "Sức mạnh của thói quen",
            "script_segments": [
                "Chúng ta là những gì chúng ta lặp đi lặp lại. Sự xuất sắc không phải là hành động, mà là thói quen.",
                "Thức dậy sớm hơn một tiếng mỗi ngày. Sau một năm, bạn có thêm ba trăm sáu mươi lăm giờ.",
                "Đọc mười trang sách mỗi ngày. Sau một năm, bạn đọc xong mười hai cuốn sách.",
                "Tập thể dục ba mươi phút mỗi ngày giảm nguy cơ trầm cảm đến bốn mươi bảy phần trăm.",
                "Viết ra ba điều biết ơn mỗi tối. Nghiên cứu cho thấy điều này tăng hạnh phúc hai mươi lăm phần trăm.",
                "Những thay đổi nhỏ tạo nên khác biệt lớn. Bắt đầu nhỏ, nhưng bắt đầu ngay.",
            ],
            "caption": "Thói quen nhỏ thay đổi cuộc đời",
            "hashtags": ["#thoiquen", "#fyp", "#pháttriểnbảnthân", "#thànhcông", "#kỷluật", "#mỗingày"],
            "search_queries": ["morning routine", "reading book", "sunrise alarm", "exercise running", "writing journal", "small steps progress"],
        },
        {
            "title": "Bài học từ người thành công",
            "script_segments": [
                "Elon Musk làm việc hơn một trăm giờ mỗi tuần khi khởi nghiệp. Ông ngủ trên sàn nhà máy Tesla.",
                "Oprah Winfrey từng bị sa thải vì không phù hợp với truyền hình. Giờ bà sở hữu đế chế truyền thông tỷ đô.",
                "Jeff Bezos bắt đầu Amazon từ garage với chiếc bàn làm từ cánh cửa cũ.",
                "Michael Jordan bị loại khỏi đội bóng rổ trường trung học. Ông dùng thất bại đó làm động lực.",
                "Walt Disney bị sa thải vì thiếu trí tưởng tượng. Công ty ông tạo ra giờ trị giá hơn hai trăm tỷ đô.",
                "Thành công không phải là đường thẳng. Nó là hành trình đầy thất bại và bài học.",
            ],
            "caption": "Người thành công cũng từng thất bại",
            "hashtags": ["#thànhcông", "#fyp", "#bàihọc", "#motivation", "#khởinghiệp", "#độnglựcsống"],
            "search_queries": ["tesla factory", "tv studio broadcast", "garage startup", "basketball court", "disney castle", "winding road journey"],
        },
        {
            "title": "Tư duy triệu phú",
            "script_segments": [
                "Người giàu nghĩ về cơ hội. Người nghèo nghĩ về rủi ro. Tư duy quyết định kết quả.",
                "Chín mươi phần trăm triệu phú tự thân đều thất bại ít nhất ba lần trước khi thành công.",
                "Warren Buffett dành tám mươi phần trăm thời gian để đọc và suy nghĩ. Ông gọi đó là đầu tư tốt nhất.",
                "Người thành công nói có với cơ hội và không với sự phân tâm. Phần lớn mọi người làm ngược lại.",
                "Bill Gates nói: nếu bạn sinh ra nghèo, đó không phải lỗi của bạn. Nhưng nếu bạn chết trong nghèo khó, đó là lỗi của bạn.",
                "Đầu tư vào bản thân là khoản đầu tư có lợi nhuận cao nhất.",
            ],
            "caption": "Tư duy triệu phú khác gì người thường",
            "hashtags": ["#triệuphú", "#fyp", "#tưduy", "#làmgiàu", "#thànhcông", "#motivation"],
            "search_queries": ["wealthy businessman thinking", "stock market chart", "reading library", "opportunity door", "bill gates portrait", "investing money"],
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
                "Một đồng tiết kiệm hôm nay có giá trị hơn mười đồng trong tương lai nhờ lãi kép.",
                "Tự do tài chính không phải là có nhiều tiền. Mà là tiền không còn kiểm soát cuộc sống bạn.",
            ],
            "caption": "Quy tắc tiền bạc người giàu luôn áp dụng",
            "hashtags": ["#tàichính", "#fyp", "#tiềnbạc", "#làmgiàu", "#đầutư", "#tiếtkiệm"],
            "search_queries": ["money growing plant", "piggy bank savings", "businessman working", "passive income laptop", "compound interest chart", "financial freedom"],
        },
        {
            "title": "Sai lầm tài chính tuổi 20",
            "script_segments": [
                "Tuổi hai mươi là thời điểm vàng để xây dựng nền tảng tài chính. Nhưng hầu hết mọi người lại bỏ lỡ.",
                "Sai lầm số một là không tiết kiệm sớm. Bắt đầu từ năm hai mươi tuổi, chỉ một triệu mỗi tháng, bạn sẽ có hàng tỷ khi về hưu nhờ lãi kép.",
                "Sai lầm số hai là mua những thứ để gây ấn tượng. Xe đẹp, quần áo đắt tiền, nhưng tài khoản thì trống rỗng.",
                "Sai lầm số ba là không đầu tư vào bản thân. Kiến thức và kỹ năng là tài sản giá trị nhất.",
                "Sai lầm số bốn là không có quỹ khẩn cấp. Hãy dành ít nhất ba đến sáu tháng chi tiêu.",
                "Hãy sống dưới khả năng tài chính. Sự giàu có thực sự đến từ khoảng cách giữa thu nhập và chi tiêu.",
            ],
            "caption": "Đừng mắc những sai lầm này ở tuổi 20",
            "hashtags": ["#tàichính", "#fyp", "#tuổi20", "#tiếtkiệm", "#đầutư", "#sailầm"],
            "search_queries": ["young person thinking", "savings jar coins", "luxury car", "student studying", "emergency fund", "simple living"],
        },
        {
            "title": "Bí mật lãi kép",
            "script_segments": [
                "Einstein gọi lãi kép là phép màu thứ tám của thế giới. Ai hiểu nó thì kiếm được nó.",
                "Nếu bạn đầu tư một triệu mỗi tháng với lãi suất mười phần trăm mỗi năm, sau ba mươi năm bạn có hơn hai tỷ.",
                "Quy tắc bảy mươi hai. Lấy bảy mươi hai chia cho lãi suất để biết bao lâu tiền gấp đôi. Lãi mười phần trăm, tiền gấp đôi sau bảy năm.",
                "Warren Buffett kiếm chín mươi chín phần trăm tài sản sau năm mươi tuổi. Vì lãi kép cần thời gian.",
                "Bắt đầu sớm quan trọng hơn bắt đầu lớn. Thời gian là người bạn tốt nhất của nhà đầu tư.",
                "Đừng chờ đến khi có nhiều tiền mới đầu tư. Hãy đầu tư với những gì bạn có ngay bây giờ.",
            ],
            "caption": "Lãi kép: phép màu biến triệu thành tỷ",
            "hashtags": ["#lãikép", "#fyp", "#đầutư", "#tàichính", "#tiếtkiệm", "#tựdotàichính"],
            "search_queries": ["compound interest graph", "money tree growing", "warren buffett", "calculator finance", "clock time passing", "coins stacking"],
        },
        {
            "title": "Thu nhập thụ động",
            "script_segments": [
                "Người giàu trung bình có bảy nguồn thu nhập. Người bình thường chỉ có một.",
                "Cho thuê bất động sản là nguồn thu nhập thụ động phổ biến nhất của triệu phú.",
                "Cổ tức từ cổ phiếu có thể trả cho bạn hàng tháng mà không cần bán.",
                "Bán khóa học online. Tạo một lần, bán mãi mãi. Nhiều người kiếm hàng trăm triệu mỗi tháng.",
                "Viết sách hoặc tạo nội dung số. Tiền bản quyền đến trong khi bạn ngủ.",
                "Bước đầu tiên là thay đổi tư duy. Đừng đổi thời gian lấy tiền. Hãy tạo hệ thống kiếm tiền cho bạn.",
            ],
            "caption": "7 nguồn thu nhập thụ động",
            "hashtags": ["#thunhậpthụđộng", "#fyp", "#tàichính", "#làmgiàu", "#đầutư", "#tựdo"],
            "search_queries": ["real estate buildings", "stock market trading", "online course laptop", "writing book", "passive income sleep", "multiple income streams"],
        },
    ],
    "fun facts": [
        {
            "title": "Sự thật thú vị",
            "script_segments": [
                "Bạn có biết mật ong không bao giờ bị hỏng không? Các nhà khảo cổ đã tìm thấy mật ong ba nghìn năm tuổi vẫn còn ăn được.",
                "Bạch tuộc có ba trái tim và máu xanh. Hai trái tim bơm máu đến mang và một trái tim bơm máu đi khắp cơ thể.",
                "Một ngày trên sao Kim dài hơn một năm trên sao Kim. Mất hai trăm bốn mươi ba ngày Trái Đất để quay một vòng.",
                "Chuối có chứa chất phóng xạ tự nhiên vì chúng chứa kali. Nhưng bạn phải ăn mười triệu quả mới bị ảnh hưởng.",
                "DNA của con người giống chín mươi tám phần trăm DNA của tinh tinh. Và giống sáu mươi phần trăm DNA chuối.",
                "Nếu bạn có thể gập một tờ giấy bốn mươi hai lần, nó sẽ cao đến Mặt Trăng.",
            ],
            "caption": "Những sự thật sẽ khiến bạn bất ngờ",
            "hashtags": ["#sựthậtthúvị", "#fyp", "#bạncóbiết", "#khoahọc", "#thúvị", "#họctập"],
            "search_queries": ["honey jar golden", "octopus underwater", "planet venus space", "banana fruit", "dna molecule", "paper folding"],
        },
        {
            "title": "Thế giới động vật",
            "script_segments": [
                "Rái cá biển nắm tay nhau khi ngủ để không bị trôi dạt xa nhau. Đây gọi là rafting.",
                "Bò có bạn thân tốt nhất và chúng bị căng thẳng khi bị tách rời nhau.",
                "Voi là động vật duy nhất không thể nhảy. Nhưng chúng có thể nghe thấy tiếng gọi cách ba mươi km qua rung động mặt đất.",
                "Cá heo ngủ bằng một nửa não. Nửa còn lại tỉnh để thở và canh chừng kẻ thù.",
                "Trái tim tôm nằm trong đầu. Và chúng có mười chân chứ không phải hai.",
                "Mèo có hơn hai mươi kiểu kêu khác nhau, nhưng chúng chỉ kêu meo meo với con người, không với mèo khác.",
            ],
            "caption": "Thế giới động vật kỳ diệu hơn bạn nghĩ",
            "hashtags": ["#độngvật", "#fyp", "#sựthậtthúvị", "#thiênnhiên", "#kỳdiệu", "#họctập"],
            "search_queries": ["sea otters floating", "cows field green", "elephant walking safari", "dolphin swimming ocean", "shrimp underwater", "cat meowing"],
        },
        {
            "title": "Bí ẩn cơ thể người",
            "script_segments": [
                "Mỗi ngày cơ thể bạn tạo ra hai lít nước bọt. Một năm đủ để đầy hai bồn tắm.",
                "Não người sử dụng hai mươi phần trăm tổng năng lượng cơ thể. Mặc dù nó chỉ chiếm hai phần trăm trọng lượng.",
                "Xương của bạn cứng hơn thép năm lần nếu so sánh cùng trọng lượng.",
                "Mắt người có thể phân biệt mười triệu màu sắc khác nhau.",
                "Nếu trải tất cả mạch máu trong cơ thể ra, chúng dài đủ để quấn quanh Trái Đất hai lần rưỡi.",
                "Mũi bạn có thể nhớ năm mươi nghìn mùi hương khác nhau. Và mùi hương gắn liền với ký ức mạnh nhất.",
            ],
            "caption": "Cơ thể bạn kỳ diệu hơn bạn tưởng",
            "hashtags": ["#cơthểngười", "#fyp", "#khoahọc", "#sựthật", "#bíẩn", "#thúvị"],
            "search_queries": ["human brain neuron", "human eye close up", "blood cells flowing", "human skeleton bones", "blood vessels", "nose smell flowers"],
        },
        {
            "title": "Sự thật về vũ trụ",
            "script_segments": [
                "Một thìa vật chất từ sao neutron nặng sáu tỷ tấn. Bằng cả ngọn núi Everest nén lại.",
                "Ánh sáng Mặt Trời mất tám phút để đến Trái Đất. Nên khi bạn nhìn Mặt Trời, bạn đang nhìn tám phút trước.",
                "Có nhiều ngôi sao trong vũ trụ hơn số hạt cát trên tất cả các bãi biển Trái Đất.",
                "Vũ trụ có mùi. Các phi hành gia nói nó giống mùi kim loại cháy và thịt nướng.",
                "Trên sao Kim, mưa là axit sunfuric. Và nó bốc hơi trước khi chạm đất vì quá nóng.",
                "Kim cương rơi như mưa trên sao Mộc và sao Thổ. Áp suất cao biến methane thành kim cương.",
            ],
            "caption": "Vũ trụ rộng lớn hơn bạn tưởng tượng",
            "hashtags": ["#vũtrụ", "#fyp", "#khoahọc", "#sựthật", "#ngoàikhônggian", "#bíẩn"],
            "search_queries": ["neutron star space", "sun rays earth", "stars galaxy milky way", "astronaut space station", "venus planet surface", "jupiter diamond rain"],
        },
        {
            "title": "Sự thật lịch sử thú vị",
            "script_segments": [
                "Nữ hoàng Cleopatra sống gần thời đại iPhone hơn là thời xây kim tự tháp. Kim tự tháp xưa hơn bà hai nghìn năm.",
                "Trong Thế chiến thứ hai, quân đội Anh đã tạo ra xe tăng bằng bóng bay để đánh lừa quân Đức.",
                "Napoleon không hề thấp. Ông cao một mét sáu tám, cao hơn trung bình người Pháp thời đó.",
                "Oxford University lâu đời hơn Đế chế Aztec. Oxford mở năm mười nghìn chín trăm sáu, Aztec bắt đầu năm mười ba hai mươi lăm.",
                "Vạn Lý Trường Thành không thể nhìn thấy từ vũ trụ bằng mắt thường. Đó là một huyền thoại sai.",
                "Samurai và cowboys đã sống cùng thời đại. Thời kỳ samurai kết thúc năm mười tám bảy sáu.",
            ],
            "caption": "Lịch sử thú vị hơn sách giáo khoa",
            "hashtags": ["#lịchsử", "#fyp", "#sựthật", "#thúvị", "#bạncóbiết", "#kiếnthức"],
            "search_queries": ["cleopatra egypt pyramid", "world war tank", "napoleon portrait", "oxford university", "great wall china", "samurai warrior"],
        },
        {
            "title": "Sự thật về đại dương",
            "script_segments": [
                "Con người đã khám phá được chưa đến năm phần trăm đại dương. Chúng ta biết về Mặt Trăng nhiều hơn đáy biển.",
                "Đại dương chứa khoảng hai mươi triệu tấn vàng. Nhưng nó loãng đến mức không thể khai thác.",
                "Điểm sâu nhất đại dương là rãnh Mariana, sâu gần mười một km. Nếu đặt Everest xuống đó, đỉnh vẫn chìm hai km.",
                "Có hơn ba triệu xác tàu đắm dưới đáy đại dương. Nhiều chiếc chứa kho báu chưa được tìm thấy.",
                "Sứa đã tồn tại trước cả khủng long. Chúng sống trên Trái Đất hơn năm trăm triệu năm.",
                "Âm thanh di chuyển nhanh gấp bốn lần trong nước so với trong không khí.",
            ],
            "caption": "Đại dương bí ẩn hơn vũ trụ",
            "hashtags": ["#đạidương", "#fyp", "#biển", "#khoahọc", "#bíẩn", "#sựthật"],
            "search_queries": ["deep ocean underwater", "gold underwater treasure", "mariana trench deep", "shipwreck underwater", "jellyfish glowing", "sound waves water"],
        },
        {
            "title": "Sự thật về thức ăn",
            "script_segments": [
                "Khoai tây chiên không phải từ Pháp. Chúng được phát minh ở Bỉ. Người Mỹ gọi là French Fries vì lính Mỹ ăn ở vùng nói tiếng Pháp.",
                "Sô cô la từng được dùng làm tiền tệ bởi người Aztec. Một quả bơ giá ba hạt cacao.",
                "Táo bạn mua ở siêu thị có thể đã được hái từ một năm trước. Chúng được bảo quản trong kho lạnh đặc biệt.",
                "Cà chua từng bị coi là độc ở châu Âu vì đĩa bằng chì phản ứng với axit trong cà chua.",
                "Wasabi thật rất đắt, khoảng năm trăm đô mỗi ký. Hầu hết wasabi bạn ăn là mù tạt nhuộm xanh.",
                "Mật ong là thức ăn duy nhất chứa tất cả chất cần thiết để duy trì sự sống.",
            ],
            "caption": "Sự thật bất ngờ về thức ăn hàng ngày",
            "hashtags": ["#thứcăn", "#fyp", "#sựthật", "#ẩmthực", "#bạncóbiết", "#thúvị"],
            "search_queries": ["french fries crispy", "chocolate cacao beans", "apple orchard", "tomato vine red", "wasabi green paste", "honey bee hive"],
        },
    ],
    "life tips": [
        {
            "title": "Mẹo hay cho cuộc sống",
            "script_segments": [
                "Bật chế độ máy bay khi sạc điện thoại. Nó sẽ sạc nhanh gấp đôi.",
                "Khi không thể quyết định, hãy tung đồng xu. Phản ứng của bạn khi đồng xu rơi sẽ cho bạn biết bạn thực sự muốn gì.",
                "Quy tắc hai phút: nếu việc gì mất dưới hai phút, hãy làm ngay.",
                "Uống một ly nước ngay khi thức dậy. Cơ thể bạn bị mất nước sau tám tiếng ngủ.",
                "Trước khi mua thứ gì, hãy tự hỏi: tôi có sẵn sàng làm việc X giờ để trả cho nó không?",
                "Đặt điện thoại xa giường khi ngủ. Buổi sáng bạn phải đứng dậy để tắt chuông.",
            ],
            "caption": "Những mẹo đơn giản thay đổi cuộc sống",
            "hashtags": ["#mẹohay", "#fyp", "#cuộcsống", "#mẹovặt", "#họcmới", "#pháttriểnbảnthân"],
            "search_queries": ["phone charging", "coin flip hand", "productive workspace", "glass water morning", "shopping thinking", "alarm clock bedroom"],
        },
        {
            "title": "Kỹ năng giao tiếp",
            "script_segments": [
                "Khi ai đó nói chuyện, hãy lặp lại ý chính của họ. Họ sẽ cảm thấy được lắng nghe và tin tưởng bạn hơn.",
                "Gọi tên người đối diện trong cuộc trò chuyện. Tên của một người là âm thanh ngọt ngào nhất với họ.",
                "Im lặng là vũ khí mạnh nhất trong đàm phán. Khi bạn im lặng, người khác sẽ tự lấp đầy khoảng trống.",
                "Nói chậm lại. Những người nói chậm và rõ ràng được đánh giá là thông minh và đáng tin cậy hơn.",
                "Khi muốn nói không, hãy nói: để tôi kiểm tra lịch. Nó cho bạn thời gian suy nghĩ mà không mất lòng.",
                "Hãy hỏi câu hỏi mở thay vì câu hỏi đóng. Thay vì hỏi bạn có khỏe không, hãy hỏi hôm nay bạn thế nào.",
            ],
            "caption": "Học cách giao tiếp như người thành công",
            "hashtags": ["#giaotiếp", "#fyp", "#kỹnăng", "#thànhcông", "#đàmphán", "#mẹohay"],
            "search_queries": ["two people talking", "business negotiation", "listening carefully", "public speaking", "saying no politely", "asking questions"],
        },
        {
            "title": "Quản lý thời gian",
            "script_segments": [
                "Chia ngày thành các block chín mươi phút. Não bộ chỉ tập trung tối đa chín mươi phút trước khi cần nghỉ.",
                "Làm việc khó nhất vào buổi sáng. Năng lượng và ý chí của bạn cao nhất lúc này.",
                "Nói không nhiều hơn. Mỗi lần bạn nói có với thứ không quan trọng, bạn đang nói không với thứ quan trọng.",
                "Tắt thông báo điện thoại khi làm việc. Mỗi lần bị gián đoạn, bạn mất hai mươi ba phút để tập trung lại.",
                "Dùng phương pháp Pomodoro. Làm việc hai mươi lăm phút, nghỉ năm phút. Bốn vòng thì nghỉ dài.",
                "Lập kế hoạch cho ngày mai vào tối hôm trước. Bạn sẽ bắt đầu ngày mới với mục tiêu rõ ràng.",
            ],
            "caption": "Quản lý thời gian như CEO",
            "hashtags": ["#quảnlýthờigian", "#fyp", "#năngsuất", "#tậptrung", "#thànhcông", "#mẹohay"],
            "search_queries": ["clock time management", "morning work desk", "saying no hand", "phone notification", "pomodoro timer", "planning notebook"],
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
                "Bạn tin tưởng người lạ mặc đồ đẹp hơn. Hiệu ứng hào quang khiến não đánh giá con người qua vẻ bề ngoài.",
                "Nhạc buồn thực ra khiến bạn cảm thấy tốt hơn vì não tiết prolactin, hormone an ủi.",
            ],
            "caption": "Tâm lý học giúp bạn hiểu con người",
            "hashtags": ["#tâmlýhọc", "#fyp", "#tâmlý", "#hiệuứng", "#thúvị", "#conngười"],
            "search_queries": ["person smiling mirror", "emotional connection", "helping hand", "red restaurant logo", "well dressed person", "listening sad music"],
        },
        {
            "title": "Hiệu ứng tâm lý trong cuộc sống",
            "script_segments": [
                "Hiệu ứng Dunning Kruger. Người biết ít thường nghĩ mình biết nhiều. Người biết nhiều lại nghĩ mình biết ít.",
                "Hiệu ứng neo. Khi thấy giá gốc năm trăm nghìn giảm còn hai trăm nghìn, bạn nghĩ đó là hời. Dù món đồ chỉ đáng một trăm nghìn.",
                "Hiệu ứng đám đông. Khi thấy quán nào đông khách, bạn tự động nghĩ quán đó ngon dù chưa từng ăn.",
                "Hiệu ứng xác nhận. Bạn chỉ tìm kiếm thông tin ủng hộ quan điểm sẵn có và bỏ qua những gì trái ngược.",
                "Hiệu ứng IKEA. Bạn đánh giá cao hơn những thứ bạn tự tay làm ra, kể cả khi chất lượng tệ.",
                "Hiệu ứng mỏ neo số. Khi đàm phán, người nói giá trước thường có lợi thế hơn.",
            ],
            "caption": "Bạn đang bị tâm lý đánh lừa mỗi ngày",
            "hashtags": ["#tâmlýhọc", "#fyp", "#hiệuứng", "#tưduy", "#thúvị", "#khoahọc"],
            "search_queries": ["confused person thinking", "sale price tag discount", "crowded restaurant", "search filter bubble", "diy furniture assembly", "negotiation business"],
        },
        {
            "title": "Ngôn ngữ cơ thể",
            "script_segments": [
                "Bảy mươi phần trăm giao tiếp là phi ngôn ngữ. Cơ thể bạn đang nói nhiều hơn miệng bạn.",
                "Khi ai đó khoanh tay, họ đang tự bảo vệ mình hoặc không đồng ý.",
                "Nhìn vào mắt sáu mươi đến bảy mươi phần trăm thời gian trò chuyện. Ít hơn là thiếu tự tin. Nhiều hơn là đe dọa.",
                "Chân thường chỉ về hướng bạn muốn đi. Nếu chân ai đó chỉ ra cửa, họ muốn kết thúc cuộc trò chuyện.",
                "Nghiêng đầu nhẹ khi lắng nghe thể hiện sự quan tâm và đồng cảm.",
                "Khi nói dối, người ta thường chạm mũi hoặc che miệng vô thức. Và ít tiếp xúc mắt hơn bình thường.",
            ],
            "caption": "Đọc ngôn ngữ cơ thể như chuyên gia",
            "hashtags": ["#ngônngữcơthể", "#fyp", "#tâmlý", "#giaotiếp", "#bíquyết", "#kỹnăng"],
            "search_queries": ["body language crossed arms", "eye contact conversation", "feet direction walking", "head tilt listening", "nonverbal communication", "detecting lies"],
        },
    ],
    "health": [
        {
            "title": "Thói quen sức khỏe",
            "script_segments": [
                "Đi bộ ba mươi phút mỗi ngày giảm năm mươi phần trăm nguy cơ bệnh tim. Không cần chạy marathon.",
                "Ngủ đủ bảy đến tám tiếng mỗi đêm. Thiếu ngủ làm giảm trí nhớ, tăng cân và tăng nguy cơ trầm cảm.",
                "Uống hai lít nước mỗi ngày. Mất nước chỉ hai phần trăm đã giảm hiệu suất não hai mươi phần trăm.",
                "Ngồi lâu nguy hiểm ngang hút thuốc. Cứ mỗi ba mươi phút, hãy đứng dậy và vận động hai phút.",
                "Ăn bảy phần no thay vì mười phần. Người Okinawa Nhật Bản sống lâu nhất thế giới nhờ quy tắc này.",
                "Cười giúp giảm hormone căng thẳng ba mươi phần trăm. Và tăng cường hệ miễn dịch.",
            ],
            "caption": "Thói quen nhỏ cho sức khỏe lớn",
            "hashtags": ["#sứckhỏe", "#fyp", "#thoiquen", "#khoẻmạnh", "#đibộ", "#ngủđủgiấc"],
            "search_queries": ["person walking park", "sleeping peacefully", "drinking water glass", "standing desk office", "healthy food plate", "laughing happy"],
        },
        {
            "title": "Sự thật về não bộ",
            "script_segments": [
                "Não bạn tạo ra đủ điện để thắp sáng một bóng đèn nhỏ. Nó hoạt động hai mươi bốn giờ, kể cả khi ngủ.",
                "Tập thể dục tạo ra protein BDNF giúp não tạo tế bào thần kinh mới. Đây là phân bón cho não.",
                "Não xử lý hình ảnh nhanh gấp sáu mươi nghìn lần so với chữ viết.",
                "Stress kéo dài co nhỏ não bộ. Đặc biệt là vùng hippocampus chịu trách nhiệm trí nhớ.",
                "Thiền định mười phút mỗi ngày làm dày vỏ não trước trán. Vùng não kiểm soát sự tập trung và quyết định.",
                "Não bạn không thể phân biệt giữa trải nghiệm thực và tưởng tượng sinh động. Đó là lý do visualization hiệu quả.",
            ],
            "caption": "Não bộ bạn mạnh hơn bạn nghĩ",
            "hashtags": ["#não", "#fyp", "#khoahọc", "#sứckhỏe", "#trínhớ", "#thiềnđịnh"],
            "search_queries": ["brain neurons glowing", "person exercising running", "visual processing eye", "stressed person", "meditation peaceful", "brain imagination"],
        },
    ],
    "technology": [
        {
            "title": "Sự thật về công nghệ",
            "script_segments": [
                "Vi rút máy tính đầu tiên được tạo ra năm một nghìn chín trăm tám mươi sáu. Nó có tên là Brain, do hai anh em Pakistan tạo ra.",
                "Điện thoại iPhone đầu tiên có bộ nhớ chỉ bốn GB. Giờ một bức ảnh có thể nặng hơn thế.",
                "Trung bình mỗi người chạm vào điện thoại hai nghìn sáu trăm lần mỗi ngày.",
                "Chín mươi phần trăm dữ liệu thế giới được tạo ra chỉ trong hai năm gần đây.",
                "Email đầu tiên được gửi năm mười chín bảy mốt. Nội dung chỉ là dãy chữ QWERTYUIOP.",
                "Google xử lý hơn tám tỷ lượt tìm kiếm mỗi ngày. Mỗi giây là chín mươi nghìn truy vấn.",
            ],
            "caption": "Những sự thật về công nghệ khiến bạn bất ngờ",
            "hashtags": ["#côngnghệ", "#fyp", "#technology", "#sựthật", "#digital", "#họctập"],
            "search_queries": ["retro computer virus", "first iphone", "person using phone", "data center servers", "old email computer", "google search screen"],
        },
        {
            "title": "AI đang thay đổi thế giới",
            "script_segments": [
                "Trí tuệ nhân tạo có thể phát hiện ung thư chính xác hơn bác sĩ chuyên khoa trong nhiều nghiên cứu.",
                "Chat GPT đạt một trăm triệu người dùng trong hai tháng. Instagram mất hai năm rưỡi để đạt con số này.",
                "Đến năm hai nghìn ba mươi, AI có thể thay thế ba trăm triệu việc làm. Nhưng cũng tạo ra hàng triệu việc mới.",
                "AI của Google đã tự học chơi cờ vây và đánh bại nhà vô địch thế giới chỉ sau ba ngày tự luyện.",
                "Deepfake có thể tạo video giả mạo bất kỳ ai. FBI cảnh báo đây là mối đe dọa an ninh quốc gia.",
                "Không phải AI lấy việc của bạn. Mà là người biết dùng AI sẽ lấy việc của người không biết.",
            ],
            "caption": "AI đang thay đổi mọi thứ",
            "hashtags": ["#AI", "#fyp", "#côngnghệ", "#trítuệnhântạo", "#tươnglai", "#ChatGPT"],
            "search_queries": ["artificial intelligence robot", "chatgpt screen", "futuristic technology", "ai playing chess", "deepfake technology", "person using ai laptop"],
        },
    ],
    "mystery": [
        {
            "title": "Bí ẩn chưa có lời giải",
            "script_segments": [
                "Tam giác Bermuda. Hơn năm mươi tàu và hai mươi máy bay đã biến mất mà không để lại dấu vết.",
                "Tín hiệu Wow. Năm bảy bảy, kính viễn vọng nhận được tín hiệu radio mạnh từ ngoài vũ trụ. Không ai biết nó từ đâu.",
                "Đá di chuyển ở Thung lũng Chết. Những tảng đá nặng hàng trăm ký tự di chuyển trên sa mạc mà không ai chạm vào.",
                "Bản thảo Voynich. Cuốn sách bốn trăm năm tuổi viết bằng ngôn ngữ mà không ai trên Trái Đất đọc được.",
                "Tiếng ù Taos. Cư dân ở New Mexico nghe thấy tiếng ù liên tục nhưng không thiết bị nào phát hiện được.",
                "Ánh sáng Hessdalen ở Na Uy. Những quả cầu sáng xuất hiện trên bầu trời suốt bốn mươi năm mà khoa học chưa giải thích được.",
            ],
            "caption": "Những bí ẩn khoa học chưa thể giải thích",
            "hashtags": ["#bíẩn", "#fyp", "#mystery", "#khoahọc", "#thếgiới", "#kỳlạ"],
            "search_queries": ["bermuda triangle ocean", "space signal telescope", "death valley moving rocks", "voynich manuscript book", "mysterious sound waves", "mysterious lights sky"],
        },
        {
            "title": "Những nơi bí ẩn nhất thế giới",
            "script_segments": [
                "Khu Vực năm mươi mốt ở Nevada. Căn cứ quân sự tuyệt mật. Nhiều người tin rằng chính phủ giấu UFO ở đây.",
                "Đảo Phục Sinh. Gần chín trăm bức tượng đá khổng lồ trên hòn đảo hẻo lánh giữa Thái Bình Dương.",
                "Cánh đồng Chum ở Lào. Hàng nghìn chum đá khổng lồ nằm rải rác. Không ai biết ai tạo ra chúng.",
                "Đường hầm Củ Chi ở Việt Nam. Hệ thống đường hầm dài hơn hai trăm km được đào bằng tay.",
                "Thành phố ngầm Derinkuyu ở Thổ Nhĩ Kỳ. Đủ chỗ cho hai mươi nghìn người sống dưới lòng đất.",
                "Kim tự tháp dưới nước ở Nhật Bản. Cấu trúc đá khổng lồ dưới biển mà khoa học vẫn tranh cãi là tự nhiên hay nhân tạo.",
            ],
            "caption": "Những nơi kỳ bí nhất hành tinh",
            "hashtags": ["#bíẩn", "#fyp", "#travel", "#mystery", "#kỳlạ", "#thếgiới"],
            "search_queries": ["area 51 desert", "easter island statues", "plain of jars laos", "cu chi tunnels vietnam", "derinkuyu underground city", "yonaguni pyramid underwater"],
        },
    ],
    "philosophy": [
        {
            "title": "Triết lý sống",
            "script_segments": [
                "Bạn không thể kiểm soát những gì xảy ra. Nhưng bạn có thể kiểm soát cách bạn phản ứng. Đó là triết lý Khắc kỷ.",
                "Cuộc sống ngắn không phải vì nó ngắn. Mà vì chúng ta lãng phí quá nhiều thời gian. Seneca nói điều này hai nghìn năm trước.",
                "Đừng so sánh chương một của bạn với chương hai mươi của người khác.",
                "Hạnh phúc không phải là đích đến. Mà là cách bạn đi trên hành trình.",
                "Ikigai của người Nhật. Hạnh phúc nằm ở giao điểm giữa điều bạn yêu, điều bạn giỏi, điều thế giới cần và điều bạn được trả tiền.",
                "Wabi sabi. Vẻ đẹp nằm trong sự không hoàn hảo. Đừng đợi hoàn hảo, hãy tìm đẹp trong hiện tại.",
            ],
            "caption": "Triết lý sống mà ai cũng nên biết",
            "hashtags": ["#triếtlý", "#fyp", "#cuộcsống", "#khắckỷ", "#hạnhphúc", "#tưduy"],
            "search_queries": ["stoic statue thinking", "hourglass time passing", "different paths journey", "peaceful meditation", "ikigai diagram", "wabi sabi pottery"],
        },
    ],
    "love": [
        {
            "title": "Khoa học về tình yêu",
            "script_segments": [
                "Não bộ người đang yêu giống hệt não bộ người nghiện. Cùng vùng não được kích hoạt.",
                "Ôm ai đó hơn hai mươi giây sẽ giải phóng oxytocin. Hormone này tạo sự gắn kết và tin tưởng.",
                "Nhìn vào mắt người yêu bốn phút liên tục có thể tạo cảm giác yêu. Đây là thí nghiệm nổi tiếng của Arthur Aron.",
                "Tim đập nhanh hơn khi yêu vì adrenaline. Nhưng về lâu dài, tình yêu lại giảm huyết áp và stress.",
                "Những cặp đôi cười cùng nhau nhiều thường bền hơn. Tiếng cười tạo kết nối sâu hơn lời nói.",
                "Sau hai năm, hormone say đắm giảm. Tình yêu thật sự bắt đầu khi bướm trong bụng biến mất.",
            ],
            "caption": "Khoa học đằng sau tình yêu",
            "hashtags": ["#tìnhyêu", "#fyp", "#tâmlý", "#love", "#cặpđôi", "#sựthật"],
            "search_queries": ["couple holding hands sunset", "brain love chemistry", "couple eye contact", "heart beating fast", "couple laughing together", "long term love elderly"],
        },
    ],
    "quotes": [
        {
            "title": "Danh ngôn thay đổi cuộc đời",
            "script_segments": [
                "Steve Jobs nói: Thời gian của bạn có hạn. Đừng lãng phí nó để sống cuộc đời của người khác.",
                "Albert Einstein nói: Trí tưởng tượng quan trọng hơn kiến thức. Kiến thức có giới hạn, trí tưởng tượng thì không.",
                "Bruce Lee nói: Tôi không sợ người tập mười nghìn cú đá. Tôi sợ người tập một cú đá mười nghìn lần.",
                "Mark Twain nói: Hai ngày quan trọng nhất trong đời là ngày bạn sinh ra và ngày bạn tìm ra lý do tại sao.",
                "Rumi nói: Vết thương là nơi ánh sáng đi vào bạn.",
                "Lão Tử nói: Hành trình ngàn dặm bắt đầu từ một bước chân.",
            ],
            "caption": "Những câu nói đáng suy ngẫm",
            "hashtags": ["#danhngôn", "#fyp", "#motivation", "#quoteoftheday", "#cuộcsống", "#tưduy"],
            "search_queries": ["steve jobs stage", "einstein thinking blackboard", "bruce lee martial arts", "typewriter quote", "sunrise inspiration", "ancient wisdom path"],
        },
    ],
    "science": [
        {
            "title": "Khoa học đáng kinh ngạc",
            "script_segments": [
                "Nếu bạn loại bỏ tất cả khoảng trống trong nguyên tử, toàn bộ nhân loại sẽ vừa trong một viên đường.",
                "Ánh sáng mất một trăm nghìn năm để đi từ trung tâm Mặt Trời ra bề mặt. Nhưng chỉ tám phút để đến Trái Đất.",
                "Có nhiều cách sắp xếp một bộ bài năm mươi hai lá hơn số nguyên tử trong Trái Đất.",
                "Nhiệt độ trung tâm Mặt Trời là mười lăm triệu độ C. Nhưng sét nóng gấp năm lần bề mặt Mặt Trời.",
                "Nước nóng đóng băng nhanh hơn nước lạnh. Hiệu ứng Mpemba này vẫn chưa được giải thích hoàn toàn.",
                "Một muỗng cà phê vật chất từ lỗ đen nặng hơn cả Trái Đất.",
            ],
            "caption": "Khoa học điên rồ nhưng có thật",
            "hashtags": ["#khoahọc", "#fyp", "#sựthật", "#vậtlý", "#bạncóbiết", "#thúvị"],
            "search_queries": ["atom particle physics", "sun core hot", "playing cards shuffle", "lightning bolt storm", "ice freezing water", "black hole space"],
        },
    ],
}

# Pool of general knowledge templates for unknown niches
GENERAL_FACTS = [
    {
        "title": "Sự thật bất ngờ về thế giới",
        "script_segments": [
            "Mỗi ngày có hai trăm nghìn người mới được sinh ra trên Trái Đất. Dân số tăng thêm gần một trăm triệu mỗi năm.",
            "Nước sôi trên đỉnh Everest ở bảy mươi độ C thay vì một trăm độ. Vì áp suất không khí thấp hơn.",
            "Biển Chết mặn đến mức bạn nổi mà không cần bơi. Độ mặn gấp mười lần đại dương.",
            "Mật ong là thức ăn duy nhất không bao giờ hỏng. Mật ong ba nghìn năm vẫn ăn được.",
            "Cây tre có thể mọc cao chín mươi cm chỉ trong một ngày. Nhanh nhất trong thế giới thực vật.",
            "Trung Quốc dùng nhiều xi măng trong ba năm hơn Mỹ dùng trong cả thế kỷ hai mươi.",
        ],
        "caption": "Những sự thật về thế giới bạn chưa biết",
        "hashtags": ["#sựthật", "#fyp", "#thếgiới", "#bạncóbiết", "#khoahọc", "#thúvị"],
        "search_queries": ["world population earth", "boiling water mountain", "dead sea floating", "honey jar bee", "bamboo forest growing", "china city construction"],
    },
    {
        "title": "Những con số đáng kinh ngạc",
        "script_segments": [
            "Trung bình bạn sẽ dành hai tuần trong đời đợi đèn đỏ. Và sáu tháng xếp hàng chờ đợi.",
            "Con người chỉ sử dụng khoảng mười phần trăm đại dương. Chín mươi phần trăm còn lại chưa được khám phá.",
            "Bạn tạo ra đủ nước bọt trong đời để đổ đầy hai bể bơi cỡ Olympic.",
            "Não bạn xử lý bảy mươi nghìn suy nghĩ mỗi ngày. Hầu hết là những suy nghĩ lặp đi lặp lại.",
            "Trái Đất quay quanh Mặt Trời với tốc độ một trăm bảy nghìn km mỗi giờ. Nhưng bạn không cảm nhận được.",
            "Nếu lịch sử Trái Đất nén thành một ngày, con người chỉ xuất hiện vào mười một giờ năm mươi tám phút đêm.",
        ],
        "caption": "Những con số khiến bạn phải suy nghĩ",
        "hashtags": ["#consố", "#fyp", "#sựthật", "#khoahọc", "#bạncóbiết", "#thúvị"],
        "search_queries": ["traffic red light", "deep ocean dark", "swimming pool water", "brain thinking neurons", "earth orbit sun", "earth history timeline"],
    },
    {
        "title": "Điều kỳ lạ trên thế giới",
        "script_segments": [
            "Ở Nhật Bản, có hòn đảo thỏ. Hàng trăm con thỏ hoang sống tự do và chạy đến ôm du khách.",
            "Iceland không có muỗi. Là một trong số ít quốc gia trên thế giới không có loài côn trùng này.",
            "Ở Venezuela có cơn bão sét vĩnh cửu. Sét đánh liên tục mười tiếng mỗi đêm, ba trăm ngày mỗi năm.",
            "Hồ nước hồng ở Úc. Không ai biết chính xác tại sao nước có màu hồng rực rỡ.",
            "Ở Turkmenistan có hố gas cháy liên tục từ năm bảy mốt. Được gọi là Cổng địa ngục.",
            "Finland có nhiều phòng xông hơi hơn số ô tô. Ba triệu phòng xông hơi cho năm triệu dân.",
        ],
        "caption": "Những nơi kỳ lạ nhất hành tinh",
        "hashtags": ["#kỳlạ", "#fyp", "#thếgiới", "#travel", "#bạncóbiết", "#thúvị"],
        "search_queries": ["rabbit island japan", "iceland landscape", "catatumbo lightning venezuela", "pink lake australia", "door to hell turkmenistan", "finland sauna"],
    },
    {
        "title": "Sự thật về giấc ngủ",
        "script_segments": [
            "Con người là loài duy nhất cố tình trì hoãn giấc ngủ. Không loài nào khác làm điều này.",
            "Bạn sẽ dành một phần ba cuộc đời để ngủ. Nếu sống tám mươi năm, bạn ngủ hai mươi sáu năm.",
            "Kỷ lục thức lâu nhất là mười một ngày. Randy Gardner mười bảy tuổi đã làm điều này năm sáu bốn.",
            "Trong năm phút đầu sau khi tỉnh dậy, bạn quên năm mươi phần trăm giấc mơ. Sau mười phút, quên chín mươi phần trăm.",
            "Não bạn tích cực hơn khi ngủ so với khi xem TV. Giấc ngủ là lúc não sắp xếp và lưu trữ ký ức.",
            "Người mù bẩm sinh vẫn mơ. Nhưng giấc mơ của họ là âm thanh, mùi hương và cảm giác.",
        ],
        "caption": "Những sự thật kỳ lạ về giấc ngủ",
        "hashtags": ["#giấcngủ", "#fyp", "#sựthật", "#sứckhỏe", "#khoahọc", "#bạncóbiết"],
        "search_queries": ["person sleeping bed", "alarm clock night", "dreaming clouds", "brain activity sleep", "peaceful sleeping", "blind person dreaming"],
    },
    {
        "title": "Sự thật về ngôn ngữ",
        "script_segments": [
            "Có hơn bảy nghìn ngôn ngữ trên thế giới. Cứ hai tuần lại có một ngôn ngữ biến mất.",
            "Tiếng Việt có sáu thanh điệu. Một từ ma có thể có sáu nghĩa khác nhau tùy cách phát âm.",
            "Emoji phổ biến nhất thế giới là mặt cười ra nước mắt. Nó chiếm năm phần trăm tất cả emoji được gửi.",
            "Ngôn ngữ Pirahã ở Brazil không có số đếm. Họ không phân biệt một, hai hay nhiều.",
            "Shakespeare phát minh hơn một nghìn bảy trăm từ tiếng Anh. Bao gồm lonely, generous và eyeball.",
            "Trẻ em có thể học bất kỳ ngôn ngữ nào trước bảy tuổi. Sau đó, khả năng này giảm dần.",
        ],
        "caption": "Ngôn ngữ thú vị hơn bạn nghĩ",
        "hashtags": ["#ngônngữ", "#fyp", "#sựthật", "#tiếngviệt", "#thúvị", "#bạncóbiết"],
        "search_queries": ["world languages map", "vietnamese tones speaking", "emoji phone screen", "amazon tribe brazil", "shakespeare writing", "child learning language"],
    },
]

# Track recently used templates to avoid duplicates
_recent_titles: deque = deque(maxlen=20)


def get_template(niche: str) -> dict:
    """Get a random template for the given niche, avoiding recent duplicates."""
    niche_lower = niche.lower().strip()

    # Find matching templates
    matched = []
    for key, templates in TEMPLATES.items():
        if key in niche_lower or niche_lower in key:
            matched.extend(templates)

    # If no match, use general facts pool
    if not matched:
        matched = list(GENERAL_FACTS)

    # Filter out recently used
    available = [t for t in matched if t["title"] not in _recent_titles]
    if not available:
        # All used recently, reset and use all
        _recent_titles.clear()
        available = matched

    chosen = random.choice(available)
    _recent_titles.append(chosen["title"])
    return chosen
