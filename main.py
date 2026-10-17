# Signature: Mourad.Soltani
"""
FounderPricingDigest - Minimal CLI micro-tool for solo SaaS founders.
Snapshots competitor pricing pages, extracts price-like amounts, computes content hash,
and detects changes for a simple digest.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

SNAPSHOT_DIR = Path.home() / ".founder_pricing_digest"
SNAPSHOT_DIR.mkdir(exist_ok=True)


def fetch_page(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch page content. Returns None on failure."""
    try:
        headers = {
            "User-Agent": "FounderPricingDigest/1.0 (Mourad.Soltani; solo founder tool)"
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Fetch error for {url}: {e}", file=sys.stderr)
        return None


def extract_prices(html: str) -> List[str]:
    """Extract price-like strings (e.g. $29, $99/mo, 49 USD)."""
    text = BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)
    # Simple regex for common price patterns
    patterns = [
        r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?",  # $29, $1,299.00
        r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|£|€|/mo|/month)",
    ]
    prices = set()
    for pat in patterns:
        prices.update(re.findall(pat, text, re.IGNORECASE))
    return sorted(list(prices))[:20]  # Limit for digest


def content_hash(html: str) -> str:
    """Hash of cleaned text content for change detection."""
    soup = BeautifulSoup(html, "html.parser")
    # Remove scripts, styles
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_snapshot(url: str) -> Optional[Dict]:
    safe = hashlib.md5(url.encode()).hexdigest()
    path = SNAPSHOT_DIR / f"{safe}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return None
    return None


def save_snapshot(url: str, data: Dict) -> None:
    safe = hashlib.md5(url.encode()).hexdigest()
    path = SNAPSHOT_DIR / f"{safe}.json"
    path.write_text(json.dumps(data, indent=2))


def check_url(url: str) -> Dict:
    html = fetch_page(url)
    if not html:
        return {"url": url, "status": "error", "message": "Failed to fetch"}

    prices = extract_prices(html)
    chash = content_hash(html)
    prev = load_snapshot(url)

    changed = prev is None or prev.get("hash") != chash
    result = {
        "url": url,
        "status": "changed" if changed else "unchanged",
        "hash": chash,
        "prices": prices,
        "previous_hash": prev.get("hash") if prev else None,
        "previous_prices": prev.get("prices") if prev else None,
    }
    save_snapshot(url, {"hash": chash, "prices": prices, "url": url})
    return result


def main():
    parser = argparse.ArgumentParser(
        description="FounderPricingDigest - Watch SaaS pricing pages. Signature: Mourad.Soltani"
    )
    parser.add_argument("urls", nargs="+", help="Pricing page URLs to check")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    results = [check_url(u) for u in args.urls]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"\n=== {r['url']} ===")
            print(f"Status: {r['status']}")
            if r["status"] == "error":
                print(r.get("message"))
                continue
            print(f"Content hash: {r['hash']}")
            print(f"Detected prices: {', '.join(r['prices']) or 'none'}")
            if r["status"] == "changed" and r["previous_prices"]:
                print(f"Previous prices: {', '.join(r['previous_prices'])}")


if __name__ == "__main__":
    main()
