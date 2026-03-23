import feedparser
import datetime
import re

SOURCES = [
    {"name": "Euronews",       "url": "https://www.euronews.com",        "rss": "https://www.euronews.com/rss?format=mrss&level=vertical&name=news", "color": "#38bdf8"},
    {"name": "Deutsche Welle", "url": "https://www.dw.com/en/",           "rss": "https://rss.dw.com/xml/rss-en-all",                                 "color": "#f97316"},
    {"name": "France 24",      "url": "https://www.france24.com/en/",     "rss": "https://www.france24.com/en/rss",                                   "color": "#a78bfa"},
    {"name": "SwissInfo",      "url": "https://www.swissinfo.ch/eng",     "rss": "https://cdn.prod.swi-services.ch/rss/eng/rssxml/latest-news/rss",   "color": "#f472b6"},
    {"name": "EUobserver",     "url": "https://euobserver.com",           "rss": "https://euobserver.com/rss",                                        "color": "#34d399"},
    {"name": "BBC News",       "url": "https://www.bbc.com/news",         "rss": "https://feeds.bbci.co.uk/news/world/europe/rss.xml",                "color": "#facc15"},
    {"name": "The Guardian",   "url": "https://www.theguardian.com",      "rss": "https://www.theguardian.com/world/europe-news/rss",                 "color": "#fb923c"},
]

MAX_ITEMS = 10

THEMES = [
    {
        "id": "war",
        "title": "War & Conflict",
        "color": "#f97316",
        "keywords": [
            "war","conflict","attack","strike","missile","bomb","killed","military",
            "troops","ceasefire","invasion","offensive","fighting","drone","explosion",
            "iran","ukraine","russia","israel","lebanon","gaza","nato","weapons","hostage"
        ]
    },
    {
        "id": "eu",
        "title": "European Union",
        "color": "#38bdf8",
        "keywords": [
            "european union","european commission","brussels","summit","parliament",
            "council","von der leyen","veto","regulation","directive","treaty",
            "eurozone","schengen","single market","eu budget","eu law"
        ]
    },
    {
        "id": "diplomacy",
        "title": "Diplomacy & Politics",
        "color": "#a78bfa",
        "keywords": [
            "diplomat","president","prime minister","chancellor","minister",
            "election","vote","party","coalition","trump","macron","scholz",
            "starmer","merz","sanctions","agreement","talks","foreign"
        ]
    },
    {
        "id": "economy",
        "title": "Economy & Trade",
        "color": "#34d399",
        "keywords": [
            "economy","economic","gdp","trade","tariff","inflation","recession","growth",
            "market","stock","bank","interest rate","energy","oil","gas","price",
            "budget","debt","investment","export","import","business","finance"
        ]
    },
    {
        "id": "society",
        "title": "Society, Science & Environment",
        "color": "#f472b6",
        "keywords": [
            "climate","environment","health","science","research","study","technology",
            "migration","refugee","crime","court","justice","education","culture",
            "sport","space","disease","flood","fire","earthquake","protest","rights"
        ]
    },
    {
        "id": "uk",
        "title": "UK Perspective",
        "color": "#facc15",
        "keywords": [
            "britain","british","england","scotland","wales","london","starmer",
            "labour","tory","conservative","westminster","downing street"
        ]
    },
]

def clean(text):
    text = re.sub(r'<[^>]+>', '', str(text))
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    return text.strip()

def fetch_feeds():
    all_items = []
    source_counts = {}
    for source in SOURCES:
        try:
            feed = feedparser.parse(source["rss"])
            count = 0
            for entry in feed.entries[:MAX_ITEMS]:
                title = clean(entry.get("title", ""))
                desc  = clean(entry.get("summary", ""))
                link  = entry.get("link", source["url"])
                date  = entry.get("published", "")[:25] if entry.get("published") else ""
                if title:
                    all_items.append({
                        "title":  title,
                        "desc":   desc,
                        "link":   link,
                        "date":   date,
                        "source": source
                    })
                    count += 1
            source_counts[source["name"]] = count
            print("OK " + source["name"] + ": " + str(count) + " items")
        except Exception as e:
            source_counts[source["name"]] = 0
            print("FAIL " + source["name"] + ": " + str(e))
    return all_items, source_counts

def classify_item(item):
    text = (item["title"] + " " + item["desc"]).lower()
    for theme in THEMES:
        for kw in theme["keywords"]:
            if kw in text:
                return theme["id"]
    return "society"

def group_by_theme(all_items):
    buckets = {t["id"]: [] for t in THEMES}
    for item in all_items:
        theme_id = classify_item(item)
        buckets[theme_id].append(item)
    return buckets

def citation_badge(source):
    return (
        '<a class="citation" href="' + source["url"] + '" '
        'target="_blank" rel="noopener" '
        'style="background:' + source["color"] + '22;'
        'color:' + source["color"] + ';'
        'border:1px solid ' + source["color"] + '55">'
        + source["name"] + '</a>'
    )

def story_card(item):
    badge   = citation_badge(item["source"])
    date_el = '<div class="card-date">' + item["date"] + '</div>' if item["date"] else ""
    desc    = item["desc"][:180] + ('...' if len(item["desc"]) > 180 else '') if item["desc"] else ""
    desc_el = '<div class="card-desc">' + desc + '</div>' if desc else ""
    return (
        '<a class="story-card" href="' + item["link"] + '" '
        'target="_blank" rel="noopener" '
        'style="--src-color:' + item["source"]["color"] + '">'
        + date_el
        + '<div class="card-title">' + item["title"] + '</div>'
        + desc_el
        + '<div class="card-footer">' + badge + '</div>'
        + '</a>'
    )

def theme_block(theme, items, idx):
    if not items:
        return ""
    sources_seen  = list(dict.fromkeys(i["source"]["name"] for i in items))
    source_list   = ", ".join(sources_seen[:4])
    if len(sources_seen) > 4:
        source_list += " and " + str(len(sources_seen) - 4) + " more"
    summary = (
        str(len(items)) + " stor" + ("y" if len(items) == 1 else "ies") +
        " across " + str(len(sources_seen)) +
        " outlet" + ("s" if len(sources_seen) != 1 else "") +
        ": " + source_list + "."
    )
    cards   = "".join(story_card(i) for i in items[:6])
    extra   = ""
    if len(items) > 6:
        extra = (
            '<div class="more-count">+ ' + str(len(items) - 6) +
            ' more stories in this category</div>'
        )
    delay = str(idx * 0.1) + "s"
    return (
        '<div class="theme-section" style="animation-delay:' + delay + '">'
        '<div class="theme-header" style="border-left:4px solid ' + theme["color"] + ';padding-left:1rem">'
        '<div class="theme-title-row">'
        '<h2 class="theme-title" style="color:' + theme["color"] + '">' + theme["title"] + '</h2>'
        '<span class="theme-count">' + str(len(items)) + ' stories</span>'
        '</div>'
        '<p class="theme-summary">' + summary + '</p>'
        '</div>'
        '<div class="stories-grid">' + cards + '</div>'
        + extra +
        '</div>'
    )

def build_html(all_items, source_counts):
    now      = datetime.datetime.utcnow()
    date_str = now.strftime("%A %-d %B %Y")
    time_str = now.strftime("%H:%M UTC")
    buckets  = group_by_theme(all_items)
    total    = len(all_items)
    sources_ok = sum(1 for v in source_counts.values() if v > 0)

    sections = ""
    for idx, theme in enumerate(THEMES):
        sections += theme_block(theme, buckets.get(theme["id"], []), idx)

    stats_data = [
        ("#f97316", str(len(buckets.get("war",      []))), "War &amp; Conflict"),
        ("#38bdf8", str(len(buckets.get("eu",       []))), "EU Stories"),
        ("#a78bfa", str(len(buckets.get("diplomacy",[]))), "Diplomacy"),
        ("#34d399", str(len(buckets.get("economy",  []))), "Economy"),
        ("#f472b6", str(len(buckets.get("society",  []))), "Society &amp; Science"),
        ("#facc15", str(len(buckets.get("uk",       []))), "UK Stories"),
    ]
    stats_html = ""
    for color, val, label in stats_data:
        stats_html += (
            '<div class="stat-box">'
            '<div class="stat-num" style="color:' + color + '">' + val + '</div>'
            '<div class="stat-label">' + label + '</div>'
            '</div>'
        )

    source_status = ""
    for source in SOURCES:
        count = source_counts.get(source["name"], 0)
        ok    = count > 0
        icon  = " &#10003;" if ok else " &#10007;"
        opacity = "" if ok else "opacity:0.35;"
        source_status += (
            '<span class="src-status" style="' + opacity +
            'color:' + source["color"] + ';'
            'border-color:' + source["color"] + '55">'
            + source["name"] + icon + '</span>'
        )

    pills = "".join(
        '<a class="pill" href="' + s["url"] + '" target="_blank">' + s["name"] + '</a>'
        for s in SOURCES
    )
    footer_links = " &middot; ".join(
        '<a href="' + s["url"] + '" target="_blank">' + s["name"] + '</a>'
        for s in SOURCES
    )

    css = (
        "*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n"
        ":root { --bg:#0b0f1a; --surface:#111827; --border:rgba(255,255,255,0.08); --text:#e8eaf0; --muted:#8890a4; }\n"
        "html { scroll-behavior:smooth; }\n"
        "body { background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;font-weight:300;line-height:1.6;overflow-x:hidden; }\n"
        ".hero { position:relative;min-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:4rem 6vw;overflow:hidden; }\n"
        ".hero-bg-blobs { position:absolute;inset:0;z-index:0;pointer-events:none; }\n"
        ".blob { position:absolute;border-radius:50%;filter:blur(120px);opacity:0.15; }\n"
        ".blob-1{width:55vw;height:55vw;top:-15vw;left:-10vw;background:#f97316;animation:drift1 14s ease-in-out infinite alternate;}\n"
        ".blob-2{width:40vw;height:40vw;top:20vw;right:-8vw;background:#38bdf8;animation:drift2 18s ease-in-out infinite alternate;}\n"
        ".blob-3{width:35vw;height:35vw;bottom:-5vw;left:30vw;background:#a78bfa;animation:drift3 22s ease-in-out infinite alternate;}\n"
        "@keyframes drift1{to{transform:translate(5vw,8vw) scale(1.08);}}\n"
        "@keyframes drift2{to{transform:translate(-6vw,5vw) scale(0.95);}}\n"
        "@keyframes drift3{to{transform:translate(4vw,-7vw) scale(1.1);}}\n"
        ".hero-inner{position:relative;z-index:1;max-width:860px;}\n"
        ".eyebrow{display:inline-flex;align-items:center;gap:0.6rem;font-size:0.68rem;letter-spacing:0.28em;text-transform:uppercase;color:var(--muted);margin-bottom:1.8rem;opacity:0;animation:slideUp 0.7s 0.1s ease forwards;}\n"
        ".eyebrow-dot{width:7px;height:7px;border-radius:50%;background:#34d399;animation:pulse-dot 2s ease-in-out infinite;}\n"
        "@keyframes pulse-dot{0%,100%{transform:scale(1);opacity:1;}50%{transform:scale(1.7);opacity:0.5;}}\n"
        ".hero h1{font-family:'Fraunces',serif;font-size:clamp(3.2rem,8vw,7.5rem);font-weight:900;line-height:0.95;letter-spacing:-0.03em;margin-bottom:1.6rem;opacity:0;animation:slideUp 0.8s 0.25s ease forwards;}\n"
        ".hero h1 em{font-style:italic;font-weight:300;background:linear-gradient(135deg,#f97316 0%,#a78bfa 50%,#38bdf8 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}\n"
        ".hero-lead{font-size:clamp(1rem,2vw,1.18rem);color:var(--muted);max-width:580px;line-height:1.7;margin-bottom:2.5rem;opacity:0;animation:slideUp 0.8s 0.4s ease forwards;}\n"
        ".source-pills{display:flex;flex-wrap:wrap;gap:0.5rem;opacity:0;animation:slideUp 0.8s 0.55s ease forwards;}\n"
        ".pill{display:inline-block;padding:0.3rem 0.9rem;border-radius:100px;border:1px solid var(--border);font-size:0.67rem;letter-spacing:0.1em;text-transform:uppercase;background:rgba(255,255,255,0.04);color:var(--muted);transition:all 0.25s;text-decoration:none;}\n"
        ".pill:hover{border-color:rgba(255,255,255,0.3);color:var(--text);}\n"
        ".scroll-cue{position:absolute;bottom:2.5rem;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:0.5rem;opacity:0;animation:slideUp 0.8s 1s ease forwards;}\n"
        ".scroll-cue span{font-size:0.6rem;letter-spacing:0.22em;text-transform:uppercase;color:var(--muted);}\n"
        ".scroll-arrow{width:1px;height:40px;background:linear-gradient(to bottom,var(--muted),transparent);animation:scrollBob 2s ease-in-out infinite;}\n"
        "@keyframes scrollBob{0%,100%{opacity:0.4;}50%{opacity:1;}}\n"
        ".main-wrap{max-width:1200px;margin:0 auto;padding:3rem 4vw 4rem;}\n"
        ".status-bar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.8rem;padding:0.75rem 1.2rem;background:var(--surface);border:1px solid var(--border);border-radius:4px;margin-bottom:1.5rem;}\n"
        ".status-left{font-size:0.7rem;color:var(--muted);display:flex;align-items:center;gap:0.6rem;}\n"
        ".live-dot{width:6px;height:6px;border-radius:50%;background:#34d399;animation:pulse-dot 2s ease-in-out infinite;}\n"
        ".status-left strong{color:#34d399;}\n"
        ".source-status-row{display:flex;flex-wrap:wrap;gap:0.4rem;margin-bottom:2rem;}\n"
        ".src-status{font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;padding:0.2rem 0.6rem;border-radius:100px;border:1px solid;background:transparent;}\n"
        ".stats-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:2px;margin-bottom:3rem;background:var(--border);}\n"
        ".stat-box{background:var(--surface);padding:1.5rem 1.2rem;text-align:center;}\n"
        ".stat-num{font-family:'Fraunces',serif;font-size:2.5rem;font-weight:900;line-height:1;margin-bottom:0.3rem;}\n"
        ".stat-label{font-size:0.6rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--muted);}\n"
        ".theme-section{margin-bottom:3.5rem;opacity:0;transform:translateY(20px);animation:slideUp 0.5s ease forwards;}\n"
        ".theme-header{padding:1.2rem 1.5rem;background:var(--surface);border:1px solid var(--border);margin-bottom:2px;}\n"
        ".theme-title-row{display:flex;align-items:baseline;gap:1rem;margin-bottom:0.5rem;}\n"
        ".theme-title{font-family:'Fraunces',serif;font-size:1.5rem;font-weight:900;}\n"
        ".theme-count{font-size:0.62rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--muted);}\n"
        ".theme-summary{font-size:0.82rem;color:var(--muted);line-height:1.6;}\n"
        ".stories-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:2px;background:var(--border);}\n"
        ".story-card{background:var(--surface);padding:1.2rem 1.4rem;text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:0.4rem;transition:background 0.2s;position:relative;overflow:hidden;}\n"
        ".story-card::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:var(--src-color,#888);opacity:0.5;transition:opacity 0.2s;}\n"
        ".story-card:hover{background:#16213a;}\n"
        ".story-card:hover::before{opacity:1;}\n"
        ".card-date{font-size:0.58rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--muted);}\n"
        ".card-title{font-family:'Fraunces',serif;font-size:0.95rem;font-weight:700;line-height:1.3;color:var(--text);}\n"
        ".card-desc{font-size:0.78rem;color:var(--muted);line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}\n"
        ".card-footer{margin-top:auto;padding-top:0.6rem;}\n"
        ".citation{font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;padding:0.15rem 0.5rem;border-radius:3px;text-decoration:none;font-weight:500;}\n"
        ".more-count{font-size:0.68rem;color:var(--muted);padding:0.6rem 1rem;background:var(--surface);border:1px solid var(--border);border-top:none;letter-spacing:0.1em;}\n"
        "footer{border-top:1px solid var(--border);padding:1.8rem 4vw;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;font-size:0.63rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--muted);}\n"
        "footer a{color:var(--muted);text-decoration:none;}\n"
        "footer a:hover{color:var(--text);}\n"
        "@keyframes slideUp{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}\n"
        "@media(max-width:600px){\n"
        "  .stories-grid{grid-template-columns:1fr;}\n"
        "  .stats-row{grid-template-columns:repeat(3,1fr);}\n"
        "  .hero{padding:3rem 5vw;}\n"
        "}\n"
    )

    html = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Europe Briefing - ' + date_str + '</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">\n'
        '<style>' + css + '</style>\n'
        '</head>\n'
        '<body>\n'
        '<section class="hero">\n'
        '<div class="hero-bg-blobs"><div class="blob blob-1"></div><div class="blob blob-2"></div><div class="blob blob-3"></div></div>\n'
        '<div class="hero-inner">\n'
        '<div class="eyebrow"><span class="eyebrow-dot"></span>' + date_str + ' - Daily Briefing</div>\n'
        '<h1>Europe<br><em>Briefing</em></h1>\n'
        '<p class="hero-lead">Headlines from ' + str(sources_ok) + ' outlets, grouped by theme with citations - automatically refreshed every morning.</p>\n'
        '<div class="source-pills">' + pills + '</div>\n'
        '</div>\n'
        '<div class="scroll-cue"><span>Scroll</span><div class="scroll-arrow"></div></div>\n'
        '</section>\n'
        '<div class="main-wrap">\n'
        '<div class="status-bar">\n'
        '<div class="status-left"><span class="live-dot"></span>Last updated <strong>' + time_str + '</strong> - ' + str(total) + ' stories from ' + str(sources_ok) + ' outlets</div>\n'
        '</div>\n'
        '<div class="source-status-row">' + source_status + '</div>\n'
        '<div class="stats-row">' + stats_html + '</div>\n'
        + sections +
        '</div>\n'
        '<footer>\n'
        '<span>Europe Briefing - ' + date_str + '</span>\n'
        '<span>' + footer_links + '</span>\n'
        '</footer>\n'
        '</body>\n'
        '</html>\n'
    )
    return html

if __name__ == '__main__':
    print("Fetching feeds...")
    all_items, source_counts = fetch_feeds()
    print("Total items: " + str(len(all_items)))
    print("Building HTML...")
    html = build_html(all_items, source_counts)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Done! index.html written.")
