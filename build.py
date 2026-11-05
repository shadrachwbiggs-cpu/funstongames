#!/usr/bin/env python3
"""Builds the Funston Games website.

Each page lives in pages/ as a small HTML file that starts with a few settings lines:

    title: Page title
    description: One sentence for search engines and link previews.
    layout: company            (or rtr for Rally the Realm pages)
    ---
    <the page's own HTML>

Running `python3 build.py` wraps every page in its layout, swaps in the values from site.json
(written in pages as {{name}}), copies static/ to docs/assets/, and writes the finished site to docs/,
which is what GitHub Pages serves. Never edit docs/ by hand: it is rebuilt every time.
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
SITE = json.loads((ROOT / "site.json").read_text())
RTR = SITE["rallyTheRealm"]
YEAR = "2026"


def store_button(extra_class=""):
    """The App Store button. While appStoreUrl is empty it shows a "Coming soon" sign instead of a link."""
    if RTR["appStoreUrl"]:
        return (f'<a class="btn btn-red {extra_class}" href="{RTR["appStoreUrl"]}">'
                f'Download on the App Store</a>')
    return f'<span class="btn btn-wood btn-soon {extra_class}" aria-disabled="true">{RTR["comingSoonText"]}</span>'


VALUES = {
    "company": SITE["companyName"],
    "legalName": SITE["companyLegalName"],
    "state": SITE["governingState"],
    "email": SITE["contactEmail"],
    "baseUrl": SITE["baseUrl"],
    "legalUpdated": RTR["legalUpdated"],
    "adultAge": RTR["adultAge"],
    "rewardGold": RTR["rewardGold"],
    "rewardsPerDay": RTR["rewardsPerDay"],
    "storeButton": store_button(),
    "storeButtonLarge": store_button("btn-large"),
    "year": YEAR,
}

COMPANY_NAV = [("/games/", "Games"), ("/about/", "About"), ("/contact/", "Contact")]
RTR_NAV = [("/rally-the-realm/", "The Game"), ("/rally-the-realm/guide/", "Game Guide"),
           ("/rally-the-realm/support/", "Help")]


def nav_html(items, current):
    out = []
    for href, label in items:
        here = ' aria-current="page"' if current == href or (href != "/rally-the-realm/" and current.startswith(href)) else ""
        out.append(f'<a href="{href}"{here}>{label}</a>')
    return "".join(out)


def footer_html():
    return f"""<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-cols">
      <div>
        <p class="footer-title">{SITE["companyName"]}</p>
        <a href="/">Home</a><a href="/games/">Games</a><a href="/about/">About</a><a href="/contact/">Contact</a>
        <a href="/privacy/">Website privacy</a>
      </div>
      <div>
        <p class="footer-title">Rally the Realm</p>
        <a href="/rally-the-realm/">The game</a><a href="/rally-the-realm/guide/">Game guide</a>
        <a href="/rally-the-realm/support/">Help and support</a>
        <a href="/rally-the-realm/privacy/">Privacy policy</a><a href="/rally-the-realm/terms/">Terms of use</a>
      </div>
    </div>
    <p class="fine">&copy; {YEAR} {SITE["companyLegalName"]}. Rally the Realm and its art are our own.
    Apple, the Apple logo, iPhone, iPad, App Store, and Game Center are trademarks of Apple Inc.</p>
  </div>
</footer>"""


def layout(page, body, path):
    title = page["title"]
    full_title = title if page.get("layout") == "company" and title == SITE["companyName"] else f'{title} | {SITE["companyName"]}'
    is_rtr = page.get("layout") == "rtr"
    canonical = SITE["baseUrl"].rstrip("/") + path
    icon = "/assets/img/rtr/ui/app_icon_180.png" if is_rtr else "/assets/img/fg/icon_180.png"
    og_image = SITE["baseUrl"].rstrip("/") + (page.get("image") or ("/assets/img/rtr/shots/battle_ember.jpg" if is_rtr else "/assets/img/fg/og.jpg"))
    if is_rtr:
        header = f"""<header class="rtr-header">
  <div class="rtr-header-inner">
    <a class="rtr-brand" href="/rally-the-realm/"><img src="/assets/img/rtr/ui/logo_small.png" alt="Rally the Realm" width="150" height="75"></a>
    <nav class="rtr-nav" aria-label="Rally the Realm">{nav_html(RTR_NAV, path)}</nav>
    <a class="rtr-company" href="/">by {SITE["companyName"]}</a>
  </div>
</header>"""
    else:
        header = f"""<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="/"><img src="/assets/img/fg/mark.svg" alt="" width="34" height="34"><span>{SITE["companyName"]}</span></a>
    <nav class="site-nav" aria-label="Main">{nav_html(COMPANY_NAV, path)}</nav>
  </div>
</header>"""
    css = '<link rel="stylesheet" href="/assets/css/site.css">'
    if is_rtr:
        css += '\n<link rel="stylesheet" href="/assets/css/rtr.css">'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{page["description"]}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{page["description"]}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{icon}">
<link rel="apple-touch-icon" href="{icon}">
<meta name="theme-color" content="{"#2b1a0f" if is_rtr else "#b3261e"}">
{css}
</head>
<body class="{"rtr" if is_rtr else "company"}">
<a class="skip" href="#main">Skip to content</a>
{header}
<main id="main">
{body}
</main>
{footer_html()}
</body>
</html>
"""


def parse(text):
    head, body = text.split("\n---\n", 1)
    page = {}
    for line in head.strip().splitlines():
        key, value = line.split(":", 1)
        page[key.strip()] = value.strip()
    return page, body


def fill(text):
    def swap(m):
        key = m.group(1)
        if key not in VALUES:
            raise SystemExit(f"Unknown value {{{{{key}}}}}")
        return VALUES[key]
    return re.sub(r"\{\{(\w+)\}\}", swap, text)


def with_base(html):
    """Lets the site live under a sub-folder (basePath) until it has its own domain."""
    base = SITE["basePath"].rstrip("/")
    if not base:
        return html
    html = re.sub(r'(href|src)="/(?!/)', rf'\1="{base}/', html)
    return re.sub(r"url\('/(?!/)", f"url('{base}/", html)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "static", OUT / "assets")
    urls = []
    for src in sorted((ROOT / "pages").rglob("*.html")):
        rel = src.relative_to(ROOT / "pages").with_suffix("")
        page, body = parse(src.read_text())
        if rel.name == "404":
            path, dest = "/404.html", OUT / "404.html"
        elif rel.name == "index":
            path = "/" + (str(rel.parent) + "/" if str(rel.parent) != "." else "")
            dest = OUT / rel.parent / "index.html"
        else:
            path = f"/{rel}/"
            dest = OUT / rel / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(with_base(layout(page, fill(body), path)))
        if rel.name != "404":
            urls.append(path)
    base = SITE["baseUrl"].rstrip("/")
    sitemap = "".join(f"  <url><loc>{base}{u}</loc></url>\n" for u in urls)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "app-ads.txt").write_text(f"google.com, pub-{SITE['admobPublisherId']}, DIRECT, f08c47fec0942fa0\n")
    domain = re.sub(r"^https?://", "", base)
    if not domain.endswith("github.io") and "/" not in domain:
        (OUT / "CNAME").write_text(domain + "\n")
    print(f"Built {len(urls)} pages into docs/")


if __name__ == "__main__":
    main()
