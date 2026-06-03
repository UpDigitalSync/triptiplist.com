#!/usr/bin/env python3
"""
Wed Phase 1: install GYG affiliate blocks into all 11 triptiplist articles.

Per article:
  - 1-3 GYG blocks placed before specific H2s (city-context) and before
    the related-articles section (country-context).
  - CSS for the .affiliate-block component appended to the inline <style>.

Partner ID: ZLEPOU5
UTM scheme: utm_source=triptiplist&utm_medium=affiliate
            &utm_campaign={article-slug}&utm_content=gyg

Idempotent: if a file already contains the affiliate-block CSS sentinel,
that file is skipped (re-runs do not double-insert).
"""
from pathlib import Path
from urllib.parse import quote_plus
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "triptiplist")
PARTNER_ID = "ZLEPOU5"
CSS_SENTINEL = "/* Affiliate blocks (GYG, Booking, Airalo, insurance) */"

AFFILIATE_CSS = """
""" + CSS_SENTINEL + """
.affiliate-block { margin: 2.5rem 0; padding: 1.4rem 1.6rem; background: #fff; border: 1px solid #e8e8e8; border-left: 4px solid #c0504d; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.affiliate-block__head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.55rem; flex-wrap: wrap; gap: 0.5rem; }
.affiliate-tag { display: inline-block; background: #f4cccc; color: #c0504d; font-size: 0.72rem; padding: 0.22rem 0.7rem; border-radius: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.affiliate-disclosure { font-size: 0.72rem; color: #999; font-style: italic; }
.affiliate-block__title { font-size: 1.18rem !important; color: #1a1a1a !important; margin: 0 0 0.5rem 0 !important; line-height: 1.35 !important; }
.affiliate-block__copy { font-size: 0.95rem; color: #555; margin-bottom: 1rem; line-height: 1.55; }
.affiliate-block__cta { display: inline-block; background: #c0504d; color: #fff !important; padding: 0.65rem 1.4rem; border-radius: 6px; font-weight: 600; text-decoration: none !important; transition: background 0.2s ease; font-size: 0.95rem; }
.affiliate-block__cta:hover { background: #a03f3c; text-decoration: none !important; }
.affiliate-block__cta:after { content: " \\2192"; }
"""

# Per-article insertion spec.
# Each entry is a list of blocks; each block is:
#   {"anchor": "before-h2", "id": "<h2-id>", "city": "Rome", "variant": "city"}
#   {"anchor": "before-related", "city": "Italy", "variant": "country"}
#   {"anchor": "before-h2", "id": "<h2-id>", "city": "Lisbon", "variant": "city-alt"}  # alt copy
SPEC = {
    "italy/best-cities-to-visit-in-italy/index.html": [
        {"anchor": "before-h2", "id": "why-is-venice-a-unique-destination",
         "city": "Rome", "variant": "city"},
        {"anchor": "before-h2", "id": "what-local-foods-should-you-try-in-italian-cities",
         "city": "Venice", "variant": "city"},
        {"anchor": "before-related", "city": "Italy", "variant": "country"},
    ],
    "italy/best-time-to-visit-italy/index.html": [
        {"anchor": "before-related", "city": "Italy", "variant": "country"},
    ],
    "japan/10-day-itinerary-for-japan/index.html": [
        {"anchor": "before-h2", "id": "whats-the-best-time-to-visit-japan-for-a-10-day-itinerary",
         "city": "Tokyo", "variant": "city"},
        {"anchor": "before-h2", "id": "what-cultural-experiences-should-i-include-in-my-japan-itinerary",
         "city": "Kyoto", "variant": "city"},
        {"anchor": "before-related", "city": "Japan", "variant": "country"},
    ],
    "japan/7-day-japan-itinerary/index.html": [
        {"anchor": "before-h2", "id": "whens-the-best-time-to-visit-japan",
         "city": "Tokyo", "variant": "city"},
        {"anchor": "before-related", "city": "Japan", "variant": "country"},
    ],
    "japan/best-day-trips-from-tokyo/index.html": [
        {"anchor": "before-h2", "id": "exploring-nikko-a-unesco-world-heritage-site",
         "city": "Kamakura", "variant": "city"},
        {"anchor": "before-h2", "id": "is-hakone-worth-the-trip-from-tokyo",
         "city": "Nikko", "variant": "city"},
        {"anchor": "before-related", "city": "Tokyo day trips", "variant": "country-alt"},
    ],
    "japan/best-time-to-visit-japan/index.html": [
        {"anchor": "before-related", "city": "Japan", "variant": "country"},
    ],
    "portugal/best-beach-towns-in-portugal/index.html": [
        {"anchor": "before-related", "city": "Portugal beaches", "variant": "country-alt"},
    ],
    "portugal/best-cities-to-visit-in-portugal/index.html": [
        {"anchor": "before-h2", "id": "why-is-porto-considered-an-underrated-gem",
         "city": "Lisbon", "variant": "city"},
        {"anchor": "before-h2", "id": "what-unique-experiences-can-you-find-in-funchal",
         "city": "Porto", "variant": "city"},
        {"anchor": "before-related", "city": "Portugal", "variant": "country"},
    ],
    "portugal/best-time-to-visit-portugal/index.html": [
        {"anchor": "before-related", "city": "Portugal", "variant": "country"},
    ],
    "portugal/how-to-get-around-portugal/index.html": [
        {"anchor": "before-h2", "id": "what-is-the-cost-of-renting-a-car-in-portugal",
         "city": "Lisbon", "variant": "city"},
        {"anchor": "before-related", "city": "Portugal", "variant": "country"},
    ],
    "portugal/what-to-do-in-lisbon-for-3-days/index.html": [
        {"anchor": "before-h2", "id": "which-neighborhoods-should-i-explore-in-lisbon",
         "city": "Lisbon", "variant": "city"},
        {"anchor": "before-h2", "id": "what-are-the-best-viewpoints-in-lisbon",
         "city": "Lisbon", "variant": "city-alt"},
        {"anchor": "before-related", "city": "Portugal", "variant": "country"},
    ],
}


def slug_of(rel_path: str) -> str:
    return rel_path.replace("/index.html", "").replace("/", "-")


def build_block(spec: dict, article_slug: str) -> str:
    city = spec["city"]
    variant = spec["variant"]
    query = quote_plus(city)
    campaign = article_slug

    if variant == "city":
        title = f"Top tours and tickets in {city}"
        copy = (f"Skip-the-line entries, small-group guided walks, and "
                f"locally-led experiences in {city}. Most tickets are free to "
                f"cancel up to 24 hours before.")
        cta = f"Browse experiences in {city}"
    elif variant == "city-alt":
        title = f"Make the most of {city}: tickets and day tours"
        copy = (f"From iconic landmarks to off-the-beaten-path neighborhoods — "
                f"compare top-rated experiences in {city} side-by-side. Free "
                f"cancellation on most bookings.")
        cta = f"See {city} experiences"
    elif variant == "country":
        title = f"Plan experiences for your {city} trip"
        copy = (f"Compare top-rated tours, day trips, and skip-the-line tickets "
                f"across {city}. Free cancellation on most experiences.")
        cta = f"Explore {city} on GetYourGuide"
    elif variant == "country-alt":
        title = f"Curated experiences for {city}"
        copy = (f"Real-traveller reviews, instant confirmation, and free "
                f"cancellation on most tours. Find the right experience for "
                f"your {city}.")
        cta = f"Browse {city}"
    else:
        raise ValueError(f"Unknown variant: {variant}")

    url = (
        f"https://www.getyourguide.com/s/?q={query}"
        f"&partner_id={PARTNER_ID}"
        f"&utm_source=triptiplist"
        f"&utm_medium=affiliate"
        f"&utm_campaign={campaign}"
        f"&utm_content=gyg"
    )

    return (
        '<aside class="affiliate-block">\n'
        '  <div class="affiliate-block__head">\n'
        '    <span class="affiliate-tag">Plan ahead</span>\n'
        '    <span class="affiliate-disclosure">Affiliate link &mdash; we may earn a commission at no extra cost to you.</span>\n'
        '  </div>\n'
        f'  <h3 class="affiliate-block__title">{title}</h3>\n'
        f'  <p class="affiliate-block__copy">{copy}</p>\n'
        f'  <a class="affiliate-block__cta" href="{url}" target="_blank" rel="sponsored noopener">{cta}</a>\n'
        '</aside>\n'
    )


def inject_css(html: str) -> str:
    if CSS_SENTINEL in html:
        return html
    # Insert CSS just before the closing </style> of the inline style block.
    # Each article has exactly one <style>...</style>.
    closing = "</style>"
    idx = html.rfind(closing)
    if idx == -1:
        raise RuntimeError("no </style> found")
    return html[:idx] + AFFILIATE_CSS + "\n" + html[idx:]


def insert_block(html: str, spec: dict, article_slug: str) -> str:
    block = build_block(spec, article_slug)
    if spec["anchor"] == "before-h2":
        marker = f'<h2 id="{spec["id"]}">'
        if marker not in html:
            print(f"   !! anchor missing: {marker}")
            return html
        return html.replace(marker, block + marker, 1)
    if spec["anchor"] == "before-related":
        marker = '<section class="related-articles">'
        if marker not in html:
            # Some articles may not have related-articles. Fall back to
            # inserting before the closing </div></div></main> wrap.
            fallback = '</div>\n </div>\n</main>'
            if fallback not in html:
                print(f"   !! no related-articles AND no main close")
                return html
            return html.replace(fallback, block + fallback, 1)
        return html.replace(marker, block + marker, 1)
    raise ValueError(f"Unknown anchor type: {spec['anchor']}")


def main() -> int:
    total_files = 0
    total_blocks = 0
    skipped_already_has = 0
    for rel, specs in SPEC.items():
        path = ROOT / rel
        if not path.exists():
            print(f"!! missing file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if CSS_SENTINEL in text:
            print(f"  already has affiliate blocks → {rel}")
            skipped_already_has += 1
            continue
        text = inject_css(text)
        slug = slug_of(rel)
        for spec in specs:
            text = insert_block(text, spec, slug)
            total_blocks += 1
        path.write_text(text, encoding="utf-8")
        print(f"OK {rel}  (+{len(specs)} blocks)")
        total_files += 1
    print(f"\nfiles updated: {total_files}")
    print(f"blocks inserted: {total_blocks}")
    print(f"files already had blocks (skipped): {skipped_already_has}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
