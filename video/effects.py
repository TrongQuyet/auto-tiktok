import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Fix Pillow 10+ compatibility with MoviePy 1.x
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

from moviepy.editor import ImageClip, CompositeVideoClip


def crop_to_vertical(clip, target_w=1080, target_h=1920):
    """Center-crop any clip to 9:16 vertical aspect ratio."""
    clip_w, clip_h = clip.size
    target_ratio = target_w / target_h
    clip_ratio = clip_w / clip_h

    if clip_ratio > target_ratio:
        # Clip is too wide -> crop width
        new_w = int(clip_h * target_ratio)
        x_center = clip_w // 2
        clip = clip.crop(
            x1=x_center - new_w // 2,
            x2=x_center + new_w // 2,
            y1=0,
            y2=clip_h,
        )
    else:
        # Clip is too tall -> crop height
        new_h = int(clip_w / target_ratio)
        y_center = clip_h // 2
        clip = clip.crop(
            x1=0,
            x2=clip_w,
            y1=y_center - new_h // 2,
            y2=y_center + new_h // 2,
        )

    return clip.resize((target_w, target_h))


def apply_ken_burns(clip, zoom_factor=1.1):
    """Slow zoom-in effect over the clip duration."""
    w, h = clip.size

    def zoom_effect(get_frame, t):
        progress = t / max(clip.duration, 0.1)
        current_zoom = 1 + (zoom_factor - 1) * progress

        frame = get_frame(t)
        img = Image.fromarray(frame)

        # Calculate crop region for zoom
        new_w = int(w / current_zoom)
        new_h = int(h / current_zoom)
        left = (w - new_w) // 2
        top = (h - new_h) // 2

        cropped = img.crop((left, top, left + new_w, top + new_h))
        resized = cropped.resize((w, h), Image.LANCZOS)
        return np.array(resized)

    return clip.fl(zoom_effect)


def _render_text_frame(text: str, width: int, height: int) -> np.ndarray:
    """Render text onto a transparent RGBA image using Pillow."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Try fonts that support Vietnamese diacritics
    font_size = 42
    font = None
    font_candidates = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Docker/Linux
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",              # Docker/Linux
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",           # Docker/Linux CJK
        "C:/Windows/Fonts/arialbd.ttf",                                  # Windows
        "C:/Windows/Fonts/arial.ttf",                                    # Windows
        "arial.ttf",
    ]
    for font_path in font_candidates:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()

    # Word wrap
    max_text_width = width - 100  # padding
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_text_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Calculate total text height
    line_height = font_size + 10
    total_height = len(lines) * line_height
    y_start = height - total_height - 200  # Position near bottom

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) // 2
        y = y_start + i * line_height

        # Draw shadow
        draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 200), font=font)
        # Draw text
        draw.text((x, y), line, fill=(255, 255, 255, 255), font=font)

    return np.array(img)


def add_text_overlay(clip, text: str):
    """Add styled caption text overlay using Pillow (no ImageMagick needed)."""
    w, h = clip.size
    text_frame = _render_text_frame(text, w, h)

    text_clip = (
        ImageClip(text_frame, ismask=False)
        .set_duration(clip.duration)
        .set_position((0, 0))
    )

    return CompositeVideoClip([clip, text_clip], size=(w, h))
