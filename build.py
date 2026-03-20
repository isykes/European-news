import feedparser
import datetime
import re

SOURCES = [
    {"name": "Euronews",       "url": "https://www.euronews.com",        "rss": "https://www.euronews.com/rss?format=mrss&level=vertical&name=news", "color": "#38bdf8"},
    {"name": "Deutsche Welle", "url": "https://www.dw.com/en/",           "rss": "https://rss.dw.com/xml/rss-en-all",                                 "color": "#f97316"},
    {"name": "France 24",      "url": "https://www.france24.com/en/",     "rss": "https://www.france24.com/en/rss",                                   "color": "#a78bfa"},
    {"name": "SwissInfo",      "url": "https://www.swissinfo.ch/eng",     "rss": "https://www.swissinfo.ch/eng/rss/news",                             "color": "#f472b6"},
    {"name": "EUobserver",     "url": "https://euobserver.com",           "rss": "https://euobserver.com/rss",                                        "color": "#34d399"},
    {"name": "BBC News",       "url": "https://www.bbc.com/news",         "rss": "https://feeds.bbci.co.uk/news/world/europe/rss.xml",                "color": "#facc15"},
    {"name": "The Guardian",   "url": "https://www.theguardian.com",      "rss": "https://www.theguardian.com/world/europe-news/rss",                 "color": "#fb923c"},
]

MAX_ITEMS = 5

def clean(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    return text.strip()

def fetch_feeds():
    results = []
    for source in SOURCES:
        try:
            feed = feedparser.parse(source["rss"])
            items = []
            for entry in feed.entries[:MAX_ITEMS]:
                items.append({
                    "title": clean(entry.get("title", "")),
                    "link":  entry.get("link", source["url"]),
                    "desc":  clean(entry.get("summary", "")),
                    "date":  entry.get("published", "")[:25] if entry.get("published") else ""
                })
            results.append({"source": source, "items": items})
            print("OK " + source["name"] + ": " + str(len(items)) + " items")
        except Exception as e:
            print("FAIL " + source["name"] + ": " + str(e))
            results.append({"source": source, "items": []})
    return results

def card_html(item, source):
    date_div = '<div class="article-date">' + item["date"] + '</div>' if item["date"] else ""
    desc_div = '<div class="article-desc">' + item["desc"] + '</div>' if item["desc"] else ""
    return (
        '<a class="article-card" href="' + item["link"] + '" target="_blank" rel="noopener" style="--src-color:' + source["color"] + '">'
        + date_div
        + '<div class="article-title">' + item["title"] + '</div>'
        + desc_div
        + '<div class="article-footer">Read on ' + source["name"] + ' &rarr;</div>'
        + '</a>'
    )

def section_html(r):
    source = r["source"]
    items  = r["items"]
    header = (
        '<div class="source-header">'
        '<div class="source-colour-bar" style="background:' + source["color"] + '"></div>'
        '<span class="source-name">' + source["name"] + '</span>'
        '<span class="source-meta">' + str(len(items)) + ' headlines</span>'
        '<a class="source-link" href="' + source["url"] + '" target="_blank" rel="noopener">Visit site &uarr;</a>'
        '</div>'
    )
    if not items:
        body = '<div class="feed-error">Feed unavailable &mdash; <a href="' + source["url"] + '" target="_blank">visit ' + source["name"] + ' directly</a>.</div>'
    else:
        cards = "".join(card_html(item, source) for item in items)
        body = '<div class="articles-grid">' + cards + '</div>'
    return '<div class="source-section">' + header + body + '</div>'

def build_html(results):
    now      = datetime.datetime.utcnow()
    date_str = now.strftime("%A %-d %B %Y")
    time_str = now.strftime("%H:%M UTC")
    sections = "".join(section_html(r) for r in results)

    pills = (
        '<a class="pill" href="https://www.euronews.com" target="_blank">Euronews</a>'
        '<a class="pill" href="https://www.dw.com/en/" target="_blank">Deutsche Welle</a>'
        '<a class="pill" href="https://www.france24.com/en/" target="_blank">France 24</a>'
        '<a class="pill" href="https://www.swissinfo.ch/eng" target="_blank">SwissInfo</a>'
        '<a class="pill" href="https://euobserver.com" target="_blank">EUobserver</a>'
        '<a class="pill" href="https://www.bbc.com/news" target="_blank">BBC News</a>'
        '<a class="pill" href="https://www.theguardian.com" target="_blank">The Guardian</a>'
    )

    footer_links = (
        '<a href="https://www.euronews.com" target="_blank">Euronews</a> &middot; '
        '<a href="https://www.dw.com/en/" target="_blank">DW</a> &middot; '
        '<a href="https://www.france24.com/en/" target="_blank">France 24</a> &middot; '
        '<a href="https://www.swissinfo.ch/eng" target="_blank">SwissInfo</a> &middot; '
        '<a href="https://euobserver.com" target="_blank">EUobserver</a> &middot; '
        '<a href="https://www.bbc.com/news" target="_blank">BBC News</a> &middot; '
        '<a href="https://www.theguardian.com" target="_blank">The Guardian</a>'
    )

    css = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg:#0b0f1a; --surface:#111827; --border:rgba(255,255,255,0.08);
  --text:#e8eaf0; --muted:#8890a4;
  --c1:#f97316; --c2:#38bdf8; --c3:#a78bfa; --c4:#34d399; --c5:#f472b6; --c6:#facc15; --c7:#fb923c;
}
html { scroll-behavior:smooth; }
body { background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;font-weight:300;line-height:1.6;overflow-x:hidden; }
.hero { position:relative;min-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:4rem 6vw;overflow:hidden; }
.hero-bg-blobs { position:absolute;inset:0;z-index:0;pointer-events:none; }
.blob { position:absolute;border-radius:50%;filter:blur(120px);opacity:0.15; }
.blob-1{width:55vw;height:55vw;top:-15vw;left:-10vw;background:var(--c1);animation:drift1 14s ease-in-out infinite alternate;}
.blob-2{width:40vw;height:40vw;top:20vw;right:-8vw;background:var(--c2);animation:drift2 18s ease-in-out infinite alternate;}
.blob-3{width:35vw;height:35vw;bottom:-5vw;left:30vw;background:var(--c3);animation:drift3 22s ease-in-out infinite alternate;}
@keyframes drift1{to{transform:translate(5vw,8vw) scale(1.08);}}
@keyframes drift2{to{transform:translate(-6vw,5vw) scale(0.95);}}
@keyframes drift3{to{transform:translate(4vw,-7vw) scale(1.1);}}
.hero-inner { position:relative;z-index:1;max-width:860px; }
.eyebrow { display:inline-flex;align-items:center;gap:0.6rem;font-size:0.68rem;letter-spacing:0.28em;text-transform:uppercase;color:var(--muted);margin-bottom:1.8rem;opacity:0;animation:slideUp 0.7s 0.1s ease forwards; }
.eyebrow-dot { width:7px;height:7px;border-radius:50%;background:var(--c4);animation:pulse-dot 2s ease-in-out infinite; }
@keyframes pulse-dot{0%,100%{transform:scale(1);opacity:1;}50%{transform:scale(1.7);opacity:0.5;}}
.hero h1 { font-family:'Fraunces',serif;font-size:clamp(3.2rem,8vw,7.5rem);font-weight:900;line-height:0.95;letter-spacing:-0.03em;margin-bottom:1.6rem;opacity:0;animation:slideUp 0.8s 0.25s ease forwards; }
.hero h1 em { font-style:italic;font-weight:300;background:linear-gradient(135deg,var(--c1) 0%,var(--c3) 50%,var(--c2) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text; }
.hero-lead { font-size:clamp(1rem,2vw,1.18rem);color:var(--muted);max-width:580px;line-height:1.7;margin-bottom:2.5rem;opacity:0;animation:slideUp 0.8s 0.4s ease forwards; }
.source-pills { display:flex;flex-wrap:wrap;gap:0.5rem;opacity:0;animation:slideUp 0.8s 0.55s ease forwards; }
.pill { display:inline-block;padding:0.3rem 0.9rem;border-radius:100px;border:1px solid var(--border);font-size:0.67rem;letter-spacing:0.1em;text-transform:uppercase;background:rgba(255,255,255,0.04);color:var(--muted);transition:all 0.25s;text-decoration:none; }
.pill:hover { border-color:rgba(255,255,255,0.3);color:var(--text); }
.scroll-cue { position:absolute;bottom:2.5rem;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:0.5rem;opacity:0;animation:slideUp 0.8s 1s ease forwards; }
.scroll-cue span { font-size:0.6rem;letter-spacing:0.22em;text-transform:uppercase;color:var(--muted); }
.scroll-arrow { width:1px;height:40px;background:linear-gradient(to bottom,var(--muted),transparent);animation:scrollBob 2s ease-in-out infinite; }
@keyframes scrollBob{0%,100%{opacity:0.4;}50%{opacity:1;}}
.main-wrap { max-width:1200px;margin:0 auto;padding:3rem 4vw 4rem; }
.status-bar { display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.8rem;padding:0.75rem 1.2rem;background:var(--surface);border:1px solid var(--border);border-radius:4px;margin-bottom:2.5rem; }
.status-left { font-size:0.7rem;color:var(--muted);display:flex;align-items:center;gap:0.6rem; }
.live-dot { width:6px;height:6px;border-radius:50%;background:var(--c4);animation:pulse-dot 2s ease-in-out infinite; }
.status-left strong { color:var(--c4); }
.source-section { margin-bottom:3rem;opacity:0;transform:translateY(20px);animation:slideUp 0.5s ease forwards; }
.source-header { display:flex;align-items:center;gap:1rem;margin-bottom:1.2rem;padding-bottom:0.8rem;border-bottom:1px solid var(--border); }
.source-colour-bar { width:4px;height:2rem;border-radius:2px;flex-shrink:0; }
.source-name { font-family:'Fraunces',serif;font-size:1.3rem;font-weight:700; }
.source-meta { font-size:0.62rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--muted); }
.source-link { font-size:0.62rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--muted);text-decoration:none;margin-left:auto;transition:color 0.2s; }
.source-link:hover { color:var(--text); }
.articles-grid { display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:1px;background:var(--border); }
.article-card { background:var(--surface);padding:1.3rem 1.5rem;text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:0.45rem;transition:background 0.2s;position:relative;overflow:hidden; }
.article-card::before { content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:var(--src-color,#888);opacity:0.6;transition:opacity 0.2s; }
.article-card:hover { background:#16213a; }
.article-card:hover::before { opacity:1; }
.article-date { font-size:0.58rem;letter-spacing:0.18em;text-transform:uppercase;color:var(--muted); }
.article-title { font-family:'Fraunces',serif;font-size:1rem;font-weight:700;line-height:1.3;color:var(--text); }
.article-desc { font-size:0.79rem;color:var(--muted);line-height:1.55;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden; }
.article-footer { font-size:0.65rem;color:var(--muted);margin-top:auto;padding-top:0.6rem; }
.feed-error { padding:1rem 0;font-size:0.82rem;color:var(--muted); }
.feed-error a { color:var(--c2); }
footer { border-top:1px solid var(--border);padding:1.8rem 4vw;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;font-size:0.63rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--muted); }
footer a { color:var(--muted);text-decoration:none; }
footer a:hover { color:var(--text); }
@keyframes slideUp{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
@media(max-width:600px){
  .articles-grid{grid-template-columns:1fr;}
  .hero{padding:3rem 5vw;}
  .source-header{flex-wrap:wrap;}
  .source-link{margin-left:0;}
}
"""

    html = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Europe Briefing &mdash; ' + date_str + '</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">\n'
        '<style>' + css + '</style>\n'
        '</head>\n'
        '<body>\n'
        '<section class="hero">\n'
        '  <div class="hero-bg-blobs"><div class="blob blob-1"></div><div class="blob blob-2"></div><div class="blob blob-3"></div></div>\n'
        '  <div class="hero-inner">\n'
        '    <div class="eyebrow"><span class="eyebrow-dot"></span>' + date_str + ' &nbsp;&middot;&nbsp; Daily Edition</div>\n'
        '    <h1>Europe<br><em>Briefing</em></h1>\n'
        '    <p class="hero-lead">Daily headlines from seven leading European and British news outlets, automatically refreshed every morning.</p>\n'
        '    <div class="source-pills">' + pills + '</div>\n'
        '  </div>\n'
        '  <div class="scroll-cue"><span>Scroll</span><div class="scroll-arrow"></div></div>\n'
        '</section>\n'
        '<div class="main-wrap">\n'
        '  <div class="status-bar">\n'
        '    <div class="status-left"><span class="live-dot"></span>Last updated <strong>' + time_str + '</strong></div>\n'
        '  </div>\n'
        + sections +
        '</div>\n'
        '<footer>\n'
        '  <span>Europe Briefing &nbsp;&middot;&nbsp; ' + date_str + '</span>\n'
        '  <span>' + footer_links + '</span>\n'
        '</footer>\n'
        '</body>\n'
        '</html>\n'
    )
    return html

if __name__ == '__main__':
    print("Fetching feeds...")
    results = fetch_feeds()
    print("Building HTML...")
    html = build_html(results)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Done! index.html written.")
