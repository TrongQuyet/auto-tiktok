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
        new_w = int(clip_h * target_ratio)
        x_center = clip_w // 2
        clip = clip.crop(
            x1=x_center - new_w // 2,
            x2=x_center + new_w // 2,
            y1=0,
            y2=clip_h,
        )
    else:
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
    """Slow zoom-in effect over the clip duration using cv2 (low memory)."""
    import cv2

    w, h = clip.size
    duration = max(clip.duration, 0.1)

    def zoom_effect(get_frame, t):
        progress = t / duration
        current_zoom = 1 + (zoom_factor - 1) * progress

        frame = get_frame(t)

        new_w = int(w / current_zoom)
        new_h = int(h / current_zoom)
        left = (w - new_w) // 2
        top = (h - new_h) // 2

        cropped = frame[top:top + new_h, left:left + new_w]
        return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

    return clip.fl(zoom_effect)


# ── Font helpers ────────────────────────────────────────────────────
_font_cache = {}

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "arial.ttf",
]


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    if size in _font_cache:
        return _font_cache[size]
    for font_path in FONT_CANDIDATES:
        try:
            font = ImageFont.truetype(font_path, size)
            _font_cache[size] = font
            return font
        except OSError:
            continue
    font = ImageFont.load_default()
    _font_cache[size] = font
    return font


def _word_wrap(words: list[str], font, max_width: int, draw: ImageDraw.Draw) -> list[list[int]]:
    """Wrap words into lines. Returns list of lines, each line is list of word indices."""
    lines = []
    current_line = []
    current_text = ""

    for i, word in enumerate(words):
        test = f"{current_text} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(i)
            current_text = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = [i]
            current_text = word

    if current_line:
        lines.append(current_line)
    return lines


# ── Static subtitle (original) ─────────────────────────────────────
def _render_static_frame(text: str, width: int, height: int) -> np.ndarray:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _get_font(42)

    max_text_width = width - 100
    words = text.split()
    lines = _word_wrap(words, font, max_text_width, draw)

    line_height = 52
    total_height = len(lines) * line_height
    y_start = height - total_height - 200

    for line_indices in lines:
        line_text = " ".join(words[i] for i in line_indices)
        bbox = draw.textbbox((0, 0), line_text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) // 2

        # Background box
        pad = 8
        draw.rounded_rectangle(
            [x - pad, y_start - pad, x + text_w + pad, y_start + 42 + pad],
            radius=6, fill=(0, 0, 0, 160),
        )
        # Shadow + text
        draw.text((x + 2, y_start + 2), line_text, fill=(0, 0, 0, 200), font=font)
        draw.text((x, y_start), line_text, fill=(255, 255, 255, 255), font=font)
        y_start += line_height

    return np.array(img)


def _add_static_overlay(clip, text: str):
    w, h = clip.size
    text_frame = _render_static_frame(text, w, h)
    text_clip = (
        ImageClip(text_frame, ismask=False)
        .set_duration(clip.duration)
        .set_position((0, 0))
    )
    return CompositeVideoClip([clip, text_clip], size=(w, h))


# ── Karaoke subtitle (one word at a time) ──────────────────────────
def _add_karaoke_overlay(clip, text: str):
    words = text.split()
    if not words:
        return clip

    w, h = clip.size
    duration = max(clip.duration, 0.1)
    font_big = _get_font(56)
    font_small = _get_font(40)

    # Time per word
    time_per_word = duration / len(words)

    # Y position: center-bottom area
    y_pos = h - 300

    def make_frame(get_frame, t):
        frame = get_frame(t)

        # Which word is active now
        word_idx = min(int(t / time_per_word), len(words) - 1)
        word = words[word_idx]

        # Progress within this word (0.0 to 1.0)
        word_start = word_idx * time_per_word
        word_progress = (t - word_start) / time_per_word

        img = Image.fromarray(frame.copy())
        draw = ImageDraw.Draw(img)

        # Measure word size
        bbox = draw.textbbox((0, 0), word, font=font_big)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (w - text_w) // 2

        # Scale effect: pop in at start of word
        if word_progress < 0.15:
            # Use smaller font for pop-in effect
            bbox_s = draw.textbbox((0, 0), word, font=font_small)
            text_w_s = bbox_s[2] - bbox_s[0]
            x_s = (w - text_w_s) // 2

            pad = 14
            draw.rounded_rectangle(
                [x_s - pad, y_pos - pad, x_s + text_w_s + pad, y_pos + 42 + pad],
                radius=10, fill=(0, 0, 0, 200),
            )
            draw.text((x_s + 2, y_pos + 2), word, fill=(0, 0, 0, 180), font=font_small)
            draw.text((x_s, y_pos), word, fill=(255, 215, 0, 255), font=font_small)
        else:
            # Full size word with highlight
            pad = 14
            draw.rounded_rectangle(
                [x - pad, y_pos - pad - 4, x + text_w + pad, y_pos + text_h + pad + 4],
                radius=10, fill=(0, 0, 0, 200),
            )
            # Shadow
            draw.text((x + 2, y_pos + 2), word, fill=(0, 0, 0, 180), font=font_big)
            # Main text: yellow highlight
            draw.text((x, y_pos), word, fill=(255, 215, 0, 255), font=font_big)

        return np.array(img)

    return clip.fl(make_frame)


# ── Public API ──────────────────────────────────────────────────────
def add_text_overlay(clip, text: str, style: str = "karaoke"):
    """Add subtitle overlay. style: 'static' or 'karaoke'."""
    if style == "karaoke":
        return _add_karaoke_overlay(clip, text)
    return _add_static_overlay(clip, text)
