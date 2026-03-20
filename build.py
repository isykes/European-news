import feedparser
import datetime

SOURCES = [
    {
        "name": "Euronews",
        "url": "https://www.euronews.com",
        "rss": "https://www.euronews.com/rss?format=mrss&level=vertical&name=news",
        "color": "#38bdf8"
    },
    {
        "name": "Deutsche Welle",
        "url": "https://www.dw.com/en/",
        "rss": "https://rss.dw.com/xml/rss-en-all",
        "color": "#f97316"
    },
    {
        "name": "France 24",
        "url": "https://www.france24.com/en/",
        "rss": "https://www.france24.com/en/rss",
        "color": "#a78bfa"
    },
    {
        "name": "SwissInfo",
        "url": "https://www.swissinfo.ch/eng",
        "rss": "https://www.swissinfo.ch/eng/rss/news",
        "color": "#f472b6"
    },
    {
        "name": "EUobserver",
        "url": "https://euobserver.com",
        "rss": "https://euobserver.com/rss",
        "color": "#34d399"
    },
    {
        "name": "BBC News",
        "url": "https://www.bbc.com/news",
        "rss": "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
        "color": "#facc15"
    },
    {
        "name": "The Guardian",
        "url": "https://www.theguardian.com",
        "rss": "https://www.theguardian.com/world/europe-news/rss",
        "color": "#fb923c"
    }
]

MAX_ITEMS = 5

def fetch_feeds():
    results = []
    for source in SOURCES:
        try:
            feed = feedparser.parse(source["rss"])
            items = []
            for entry in feed.entries[:MAX_ITEMS]:
                items.append({
                    "title": entry.get("title", ""),
                    "link":  entry.get("link", source["url"]),
                    "desc":  entry.get("summary", ""),
                    "date":  entry.get("published", "")
                })
            results.append({"source": source, "items": items})
            print(f"✅ {source['name']}: {len(items)} items")
        except Exception as e:
            print(f"❌ {source['name']}: {e}")
            results.append({"source": source, "items": []})
    return results

def clean(text):
    import re
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    return text.strip()

def build_html(results):
    now = datetime.datetime.utcnow()
    date_str = now.strftime("%A %-d %B %Y")
    time_str = now.strftime("%H:%M UTC")

    sections_html = ""
    for r in results:
        source = r["source"]
        items  = r["items"]

        cards_html = ""
        if not items:
            cards_html = f'<div class="feed-error">Feed unavailable — <a href="{source["url"]}" target="_blank">visit {source["name"]} directly</a>.</div>'
        else:
            cards = ""
            for item in items:
                title = clean(item["title"])
                desc  = clean(item["desc"])
                link  = item["link"]
                date  = clean(item["date"])[:25] if item["date"] else ""
                cards += f'''
                <a class="article-card" href="{link}" target="_blank" rel="noopener" style="--src-color:{source["color"]}">
                    {f'<div class="article-date">{date}</div>' if date else ''}
                    <div class="article-title">{title}</div>
                    {f'<div class="article-desc">{desc}</div>' if desc else ''}
                    <div class="article-footer">Read on {source["name"]} →</div>
                </a>'''
            cards_html = f'<div class="articles-grid">{cards}</div>'

        sections_html += f'''
        <div class="source-section">
            <div class="source-header">
                <div class="source-colour-bar" style="background:{source["color"]}"></div>
                <span class="source-name">{source["name"]}</span>
                <span class="source-meta">{len(items)} headlines</span>
                <a class="source-link" href="{source["url"]}" target="_blank" rel="noopener">Visit site ↗</a>
            </div>
            {cards_html}
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Europe Briefing — {date_str}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --bg:#0b0f1a; --surface:#111827; --border:rgba(255,255,255,0.08);
  --text:#e8eaf0; --muted:#8890a4;
  --c1:#f97316; --c2:#38bdf8; --c3:#a78bfa; --c4:#34d399; --c5:#f472b6; --c6:#facc15; --c7:#fb923c;
}}