import hashlib
import re
from urllib.parse import urljoin, urlparse


def resolve_url(base_url: str, href: str) -> str:
    """Resolve a potentially relative URL against a base URL."""
    if not href or href.startswith("data:") or href.startswith("javascript:"):
        return ""
    if href.startswith("//"):
        scheme = urlparse(base_url).scheme or "https"
        href = f"{scheme}:{href}"
    return urljoin(base_url, href)


def safe_filename(url: str, fallback_ext: str = "") -> str:
    """Generate a safe, unique filename from a URL."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    name = path.split("/")[-1] if path else ""

    # Remove query string from filename but use it for uniqueness
    if not name or len(name) > 100:
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        name = f"asset_{url_hash}"

    # Sanitize
    name = re.sub(r'[<>:"/\\|?*]', '_', name)

    # Ensure extension
    if fallback_ext and "." not in name:
        name = f"{name}.{fallback_ext.lstrip('.')}"

    return name


def is_private_ip(url: str) -> bool:
    """Check if URL points to a private/internal IP (SSRF protection)."""
    import ipaddress
    import socket

    hostname = urlparse(url).hostname
    if not hostname:
        return True

    # Block common private hostnames
    if hostname in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        return True

    try:
        ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        return ip.is_private or ip.is_loopback or ip.is_reserved
    except (socket.gaierror, ValueError):
        return False


def get_domain(url: str) -> str:
    """Extract domain name from URL."""
    hostname = urlparse(url).hostname or "unknown"
    return hostname.replace("www.", "")
