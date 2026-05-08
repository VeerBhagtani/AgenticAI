"""
Extractor — fetches a URL and returns clean text content.
"""
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Tags that are noise
SKIP_TAGS = {"script","style","nav","header","footer","aside","form","noscript","iframe"}

def fetch(url: str, timeout: int = 10) -> dict:
    """
    Returns:
        {"success": True,  "text": "...", "title": "..."}
        {"success": False, "error": "..."}
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return {"success": False, "error": f"Non-HTML content: {content_type}"}

        soup = BeautifulSoup(resp.text, "lxml")

        # Remove noise tags
        for tag in soup(SKIP_TAGS):
            tag.decompose()

        title = soup.title.get_text(strip=True) if soup.title else ""

        # Try article/main first, fall back to body
        main = soup.find("article") or soup.find("main") or soup.find("body")
        if not main:
            return {"success": False, "error": "No body content found"}

        # Extract paragraphs
        paragraphs = [p.get_text(" ", strip=True) for p in main.find_all("p") if len(p.get_text(strip=True)) > 40]
        text = "\n\n".join(paragraphs)

        if len(text) < 100:
            # Fallback: dump all text
            text = main.get_text(" ", strip=True)

        return {"success": True, "title": title, "text": text[:8000]}  # cap at 8k chars

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection error"}
    except Exception as e:
        return {"success": False, "error": str(e)}
