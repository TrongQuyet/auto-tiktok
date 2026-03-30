import asyncio
import logging

from config import Settings

logger = logging.getLogger(__name__)

PLATFORM_PROMPTS = {
    "facebook": """Bạn là một người dùng Facebook thật. Hãy viết một bài đăng Facebook HOÀN TOÀN TỰ NHIÊN, không có vẻ quảng cáo, để chia sẻ về sản phẩm này.

Yêu cầu:
- Độ dài: 150-250 từ
- Bắt đầu bằng câu chuyện ngắn, trải nghiệm cá nhân, hoặc câu hỏi tạo tò mò
- Đề cập sản phẩm ở giữa bài như một phát hiện thú vị, không phải quảng cáo
- Kết bằng CTA nhẹ nhàng: "ai muốn biết thêm dm mình" hoặc tương tự
- Thêm link ở cuối sau 2-3 hashtag phù hợp
- KHÔNG dùng từ ngữ quảng cáo: "tuyệt vời", "cực xịn", "giảm giá", "mua ngay"
- Viết như người bình thường chia sẻ với bạn bè

Sản phẩm: {product_name}
Mô tả: {product_description}
Link: {affiliate_url}

Chỉ trả về nội dung bài đăng:""",

    "twitter": """Bạn là người dùng Twitter/X. Viết một tweet về sản phẩm này, dưới 230 ký tự (link sẽ được thêm tự động).

Yêu cầu:
- Tối đa 230 ký tự
- 1-2 emoji phù hợp (không quá nhiều)
- Tone: thẳng thắn, thông minh, không spam
- 1-2 hashtag ngắn
- Có thể dùng tiếng Anh hoặc tiếng Việt, chọn cái nào phù hợp hơn với sản phẩm
- CTA tự nhiên: "link bên dưới", "check it out", v.v.
- KHÔNG: "siêu giảm giá", "deal hot", "mua ngay kẻo hết"

Sản phẩm: {product_name}
Mô tả: {product_description}

Chỉ trả về nội dung tweet (không gồm link):""",

    "instagram": """Bạn là Instagram creator. Viết caption cho bài đăng Instagram về sản phẩm này.

Yêu cầu:
- Dòng 1: Hook cực ngắn, gây tò mò (tối đa 100 ký tự - phần hiển thị trước "xem thêm")
- Sau dòng 1: 2 dòng trống
- Phần thân: 4-6 bullet points ngắn về giá trị sản phẩm
- Cuối: "Link in bio 🔗"
- Sau dấu ---: 20-25 hashtag mix (tiếng Việt + tiếng Anh)
- Tone: Aspirational, lifestyle, không hard-sell

Sản phẩm: {product_name}
Mô tả: {product_description}

Chỉ trả về caption:""",

    "reddit": """You are a helpful Reddit community member. Write a Reddit comment to share this product naturally.

Requirements:
- Start with genuinely useful information related to the product's use case
- Mention the product as a personal recommendation, not an advertisement
- English language (Reddit is primarily English)
- 100-180 words
- Tone: Helpful, authentic, community member
- Include the link naturally at the end
- NO: marketing speak, ALL CAPS, excessive exclamation marks, "best deal ever"

Product: {product_name}
Description: {product_description}
Link: {affiliate_url}

Return only the comment text:""",

    "tiktok": """Bạn là TikToker Việt Nam. Viết caption cho video TikTok về sản phẩm này.

Yêu cầu:
- 2-3 dòng đầu: Hook nhanh, relatable, ngôn ngữ Gen Z VN
- Ví dụ hook tốt: "Ủa ai còn chưa biết cái này?", "Đợt này mình obsessed với...", "Thật ra thì..."
- "Link in bio" ở cuối
- 6-10 hashtag: mix #fyp #xuhuong #viral + hashtag niche liên quan sản phẩm
- Tổng caption (không đếm hashtag): 150-200 ký tự

Sản phẩm: {product_name}
Mô tả: {product_description}

Chỉ trả về caption:""",
}

FALLBACK_TEMPLATES = {
    "facebook": "Hôm nay mình tình cờ phát hiện ra {product_name} và thấy khá hay! Dùng thử rồi thấy đáng đồng tiền lắm. Cái này giải quyết được vấn đề mình đang gặp phải từ lâu. Ai quan tâm xem thêm tại đây nhé 👇\n{affiliate_url}\n\n#review #muasắm #chiasẻ",
    "twitter": "Vừa tìm được {product_name} khá ổn 👀 Ai cần thì check link này:",
    "instagram": "Cái này đỉnh hơn mình nghĩ 👀\n\n\n✅ Chất lượng tốt\n✅ Đáng đồng tiền\n✅ Dùng thử là ghiền\n\nLink in bio 🔗\n\n---\n#review #muasắm #vietnam #lifestyle #chiasẻ #sảnphẩmhay",
    "reddit": "I've been using {product_name} for a while now and thought I'd share with this community. It's been pretty solid for what I needed. If you're looking for something in this space, worth checking out: {affiliate_url}",
    "tiktok": "Ủa ai chưa biết {product_name}?? Dùng thử rồi mê luôn 🔥\nLink bio nha!\n\n#fyp #xuhuong #review #viral",
}


async def generate_platform_content(
    affiliate_url: str,
    product_name: str,
    product_description: str,
    platforms: list[str],
    settings: Settings,
) -> dict[str, str]:
    tasks = [
        _generate_for_platform(platform, affiliate_url, product_name, product_description, settings)
        for platform in platforms
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    content = {}
    for platform, result in zip(platforms, results):
        if isinstance(result, Exception):
            logger.warning(f"AI generation failed for {platform}, using fallback: {result}")
            content[platform] = _fallback(platform, product_name, affiliate_url)
        else:
            content[platform] = result

    return content


async def _generate_for_platform(
    platform: str,
    affiliate_url: str,
    product_name: str,
    product_description: str,
    settings: Settings,
) -> str:
    prompt = PLATFORM_PROMPTS[platform].format(
        product_name=product_name,
        product_description=product_description,
        affiliate_url=affiliate_url,
    )

    if settings.ai_provider == "openai":
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
        )
        return resp.choices[0].message.content.strip()

    if settings.ai_provider == "anthropic":
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        resp = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text.strip()

    if settings.ai_provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = await asyncio.get_event_loop().run_in_executor(
            None, model.generate_content, prompt
        )
        return resp.text.strip()

    return _fallback(platform, product_name, affiliate_url)


def _fallback(platform: str, product_name: str, affiliate_url: str) -> str:
    tag = product_name.lower().replace(" ", "")
    template = FALLBACK_TEMPLATES.get(platform, "{product_name}: {affiliate_url}")
    return template.format(
        product_name=product_name,
        affiliate_url=affiliate_url,
        product_name_tag=tag,
    )
