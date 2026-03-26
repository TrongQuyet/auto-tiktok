import logging
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from .utils import get_domain, resolve_url, safe_filename

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_ASSET_SIZE = 20 * 1024 * 1024   # 20 MB per file
MAX_ASSETS = 500
TIMEOUT = 30


class CloneResult:
    def __init__(self):
        self.css_count = 0
        self.js_count = 0
        self.image_count = 0
        self.font_count = 0
        self.failed_assets: list[str] = []
        self.total_size = 0


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
def _download_asset(url: str, save_path: Path, max_size: int = MAX_ASSET_SIZE) -> bool:
    """Download a single asset. Returns True on success."""
    try:
        resp = requests.get(url, headers=HEADERS, stream=True, timeout=TIMEOUT)
        resp.raise_for_status()

        content_length = int(resp.headers.get("content-length", 0))
        if content_length > max_size:
            logger.warning(f"Skipping (too large: {content_length}): {url}")
            return False

        save_path.parent.mkdir(parents=True, exist_ok=True)
        size = 0
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                size += len(chunk)
                if size > max_size:
                    logger.warning(f"Skipping (exceeded size limit): {url}")
                    save_path.unlink(missing_ok=True)
                    return False
                f.write(chunk)
        return True
    except Exception as e:
        logger.warning(f"Failed to download {url}: {e}")
        save_path.unlink(missing_ok=True)
        raise


def clone_website(url: str, output_dir: Path, include_js: bool = True,
                  include_images: bool = True, include_fonts: bool = True,
                  progress_callback=None) -> CloneResult:
    """Clone a website's frontend assets into output_dir."""
    result = CloneResult()

    def report(msg: str, pct: int):
        if progress_callback:
            progress_callback(msg, pct)

    # Step 1: Fetch HTML
    report("Fetching page...", 5)
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
    resp.raise_for_status()

    content_type = resp.headers.get("content-type", "")
    if "text/html" not in content_type and "application/xhtml" not in content_type:
        raise ValueError(f"URL did not return HTML (got {content_type})")

    base_url = resp.url  # Final URL after redirects
    html = resp.text

    # Step 2: Parse HTML
    report("Parsing page...", 10)
    soup = BeautifulSoup(html, "html.parser")

    css_urls = []
    js_urls = []
    image_urls = []
    font_urls = []

    # Collect CSS
    for tag in soup.find_all("link", rel=lambda r: r and "stylesheet" in r):
        href = tag.get("href")
        resolved = resolve_url(base_url, href)
        if resolved:
            css_urls.append(resolved)

    # Collect inline @import in <style> tags
    for style_tag in soup.find_all("style"):
        if style_tag.string:
            for match in re.findall(r'@import\s+url\(["\']?(.*?)["\']?\)', style_tag.string):
                resolved = resolve_url(base_url, match)
                if resolved:
                    css_urls.append(resolved)

    # Collect JS
    if include_js:
        for tag in soup.find_all("script", src=True):
            resolved = resolve_url(base_url, tag["src"])
            if resolved:
                js_urls.append(resolved)

    # Collect images
    if include_images:
        for tag in soup.find_all("img", src=True):
            resolved = resolve_url(base_url, tag["src"])
            if resolved:
                image_urls.append(resolved)
        # srcset
        for tag in soup.find_all(["img", "source"], srcset=True):
            for part in tag["srcset"].split(","):
                src = part.strip().split()[0]
                resolved = resolve_url(base_url, src)
                if resolved:
                    image_urls.append(resolved)
        # Favicons
        for tag in soup.find_all("link", rel=lambda r: r and ("icon" in r or "apple-touch-icon" in r)):
            href = tag.get("href")
            resolved = resolve_url(base_url, href)
            if resolved:
                image_urls.append(resolved)
        # OG images
        for tag in soup.find_all("meta", property="og:image"):
            content = tag.get("content")
            resolved = resolve_url(base_url, content)
            if resolved:
                image_urls.append(resolved)

    # Deduplicate
    css_urls = list(dict.fromkeys(css_urls))
    js_urls = list(dict.fromkeys(js_urls))
    image_urls = list(dict.fromkeys(image_urls))

    total_assets = len(css_urls) + len(js_urls) + len(image_urls)
    if total_assets > MAX_ASSETS:
        logger.warning(f"Too many assets ({total_assets}), limiting to {MAX_ASSETS}")

    # Step 3: Create directories
    report("Creating directory structure...", 12)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "css").mkdir(exist_ok=True)
    (output_dir / "js").mkdir(exist_ok=True)
    (output_dir / "images").mkdir(exist_ok=True)
    (output_dir / "fonts").mkdir(exist_ok=True)

    # Track URL -> local path mapping for rewriting
    url_map: dict[str, str] = {}
    asset_count = 0

    def _check_limits():
        nonlocal asset_count
        asset_count += 1
        return asset_count <= MAX_ASSETS and result.total_size <= MAX_TOTAL_SIZE

    # Step 4: Download CSS + parse for nested assets
    css_url_pattern = re.compile(r'url\(["\']?((?!data:)[^"\')\s]+)["\']?\)')

    for i, css_url in enumerate(css_urls):
        if not _check_limits():
            break
        pct = 15 + int((i / max(len(css_urls), 1)) * 25)
        report(f"Downloading CSS ({i+1}/{len(css_urls)})...", pct)

        filename = safe_filename(css_url, "css")
        local_path = output_dir / "css" / filename

        try:
            ok = _download_asset(css_url, local_path)
            if not ok:
                result.failed_assets.append(css_url)
                continue
        except Exception:
            result.failed_assets.append(css_url)
            continue

        result.css_count += 1
        result.total_size += local_path.stat().st_size
        url_map[css_url] = f"css/{filename}"

        # Parse CSS for url() references
        css_text = local_path.read_text(encoding="utf-8", errors="ignore")
        for match in css_url_pattern.findall(css_text):
            resolved = resolve_url(css_url, match)
            if not resolved:
                continue
            lower = resolved.lower()
            if include_fonts and any(lower.endswith(ext) for ext in (".woff2", ".woff", ".ttf", ".eot", ".otf")):
                if resolved not in font_urls:
                    font_urls.append(resolved)
            elif include_images and any(lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico")):
                if resolved not in image_urls:
                    image_urls.append(resolved)

    # Step 5: Download JS
    if include_js:
        for i, js_url in enumerate(js_urls):
            if not _check_limits():
                break
            pct = 40 + int((i / max(len(js_urls), 1)) * 15)
            report(f"Downloading JS ({i+1}/{len(js_urls)})...", pct)

            filename = safe_filename(js_url, "js")
            local_path = output_dir / "js" / filename

            try:
                ok = _download_asset(js_url, local_path)
                if not ok:
                    result.failed_assets.append(js_url)
                    continue
            except Exception:
                result.failed_assets.append(js_url)
                continue

            result.js_count += 1
            result.total_size += local_path.stat().st_size
            url_map[js_url] = f"js/{filename}"

    # Step 6: Download images
    if include_images:
        for i, img_url in enumerate(image_urls):
            if not _check_limits():
                break
            pct = 55 + int((i / max(len(image_urls), 1)) * 25)
            report(f"Downloading images ({i+1}/{len(image_urls)})...", pct)

            filename = safe_filename(img_url)
            local_path = output_dir / "images" / filename

            try:
                ok = _download_asset(img_url, local_path)
                if not ok:
                    result.failed_assets.append(img_url)
                    continue
            except Exception:
                result.failed_assets.append(img_url)
                continue

            result.image_count += 1
            result.total_size += local_path.stat().st_size
            url_map[img_url] = f"images/{filename}"

    # Step 7: Download fonts
    if include_fonts:
        for i, font_url in enumerate(font_urls):
            if not _check_limits():
                break
            pct = 80 + int((i / max(len(font_urls), 1)) * 8)
            report(f"Downloading fonts ({i+1}/{len(font_urls)})...", pct)

            filename = safe_filename(font_url)
            local_path = output_dir / "fonts" / filename

            try:
                ok = _download_asset(font_url, local_path)
                if not ok:
                    result.failed_assets.append(font_url)
                    continue
            except Exception:
                result.failed_assets.append(font_url)
                continue

            result.font_count += 1
            result.total_size += local_path.stat().st_size
            url_map[font_url] = f"fonts/{filename}"

    # Step 8: Rewrite URLs in HTML
    report("Rewriting HTML URLs...", 90)

    # Rewrite tag attributes
    for tag in soup.find_all(True):
        for attr in ("href", "src", "srcset"):
            val = tag.get(attr)
            if not val:
                continue

            if attr == "srcset":
                parts = []
                for part in val.split(","):
                    tokens = part.strip().split()
                    if tokens:
                        resolved = resolve_url(base_url, tokens[0])
                        if resolved in url_map:
                            tokens[0] = url_map[resolved]
                        parts.append(" ".join(tokens))
                tag[attr] = ", ".join(parts)
            else:
                resolved = resolve_url(base_url, val)
                if resolved in url_map:
                    tag[attr] = url_map[resolved]

    # Rewrite inline style url()
    for tag in soup.find_all(style=True):
        style = tag["style"]
        def replace_inline_url(m):
            inner = m.group(1)
            resolved = resolve_url(base_url, inner)
            if resolved in url_map:
                return f'url({url_map[resolved]})'
            return m.group(0)
        tag["style"] = css_url_pattern.sub(replace_inline_url, style)

    # Rewrite <style> tags
    for style_tag in soup.find_all("style"):
        if style_tag.string:
            text = style_tag.string
            def replace_style_url(m):
                inner = m.group(1)
                resolved = resolve_url(base_url, inner)
                if resolved in url_map:
                    return f'url({url_map[resolved]})'
                return m.group(0)
            style_tag.string = css_url_pattern.sub(replace_style_url, text)
            # Rewrite @import
            def replace_import(m):
                import_url = m.group(1)
                resolved = resolve_url(base_url, import_url)
                if resolved in url_map:
                    return f'@import url({url_map[resolved]})'
                return m.group(0)
            style_tag.string = re.sub(r'@import\s+url\(["\']?(.*?)["\']?\)', replace_import, style_tag.string)

    # Step 9: Rewrite URLs in CSS files
    report("Rewriting CSS URLs...", 93)
    for css_url, local_rel in url_map.items():
        if not local_rel.startswith("css/"):
            continue
        css_path = output_dir / local_rel
        if not css_path.exists():
            continue

        css_text = css_path.read_text(encoding="utf-8", errors="ignore")

        def replace_css_url(m):
            inner = m.group(1)
            resolved = resolve_url(css_url, inner)
            if resolved in url_map:
                # Make path relative from css/ folder
                target = url_map[resolved]
                return f'url(../{target})'
            return m.group(0)

        new_text = css_url_pattern.sub(replace_css_url, css_text)

        # Also handle @import
        def replace_css_import(m):
            import_url = m.group(1)
            resolved = resolve_url(css_url, import_url)
            if resolved in url_map:
                target = url_map[resolved]
                return f'@import url(../{target})'
            return m.group(0)

        new_text = re.sub(r'@import\s+url\(["\']?(.*?)["\']?\)', replace_css_import, new_text)
        css_path.write_text(new_text, encoding="utf-8")

    # Step 10: Save HTML
    report("Saving HTML...", 96)
    html_path = output_dir / "index.html"
    html_path.write_text(str(soup), encoding="utf-8")

    report("Done!", 100)
    logger.info(
        f"Clone complete: {result.css_count} CSS, {result.js_count} JS, "
        f"{result.image_count} images, {result.font_count} fonts, "
        f"{len(result.failed_assets)} failed, {result.total_size / 1024 / 1024:.1f} MB total"
    )

    return result
