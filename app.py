
import os
import io
import time
from collections import Counter
from flask import Flask, render_template, jsonify
import pandas as pd
import plotly.graph_objects as go
import requests

app = Flask(__name__)

CSV_URL = os.getenv("CSV_URL", "").strip()
AUTO_REFRESH = os.getenv("AUTO_REFRESH", "false").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))  # seconds

_cache = {"ts": 0, "df": None, "err": None, "source": None}

def fetch_csv():
    global _cache
    now = time.time()
    if _cache["df"] is not None and (now - _cache["ts"] < CACHE_TTL):
        return _cache["df"], _cache["err"], _cache["source"]

    err = None
    df = None
    source = None

    if CSV_URL:
        try:
            headers = {"User-Agent": "jjodel-sankey/1.0"}
            r = requests.get(CSV_URL, headers=headers, timeout=20, allow_redirects=True)
            r.raise_for_status()
            df = pd.read_csv(io.StringIO(r.text))
            source = CSV_URL
        except Exception as e:
            err = f"Failed to fetch CSV from CSV_URL: {e}"

    if df is None:
        try:
            df = pd.read_csv("sample.csv")
            source = "sample.csv (fallback)"
        except Exception as e2:
            err = (err or "") + f" | Also failed to load fallback sample.csv: {e2}"

    _cache.update({"ts": now, "df": df, "err": err, "source": source})
    return df, err, source

def chapter_label(ch):
    ch = str(ch)
    parts = ch.split(" ", 1)
    num = parts[0]
    rest = parts[1] if len(parts) > 1 else ""
    return f"Ch{num} {rest[:32]}".strip()

def build_sankey(df):
    chapters = df["chapter"].dropna().unique().tolist()
    idx = {c: i for i, c in enumerate(chapters)}

    links = []
    id_to_ch = df.set_index("id")["chapter"].to_dict()
    for _, row in df.iterrows():
        pre = str(row.get("prereq", "")).strip()
        if pre and pre.lower() != "nan":
            for p in [s.strip() for s in pre.split(",") if s.strip()]:
                if p in id_to_ch:
                    src_ch = id_to_ch[p]
                    dst_ch = row["chapter"]
                    if src_ch != dst_ch:
                        links.append((src_ch, dst_ch))

    cnt = Counter(links)
    if not cnt and chapters:
        cnt[(chapters[0], chapters[0])] = 1

    sources, targets, values = [], [], []
    for (a, b), w in cnt.items():
        if a in idx and b in idx:
            sources.append(idx[a])
            targets.append(idx[b])
            values.append(int(w))

    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(label=[chapter_label(c) for c in chapters], pad=18, thickness=16),
        link=dict(source=sources, target=targets, value=values,
                  hovertemplate="From %{source.label} to %{target.label}: %{value} cross-chapter deps<extra></extra>")
    )])
    fig.update_layout(title="MDE + Jjodel Learning Flow (Live CSV)")
    return fig

@app.route("/")
def index():
    df, err, source = fetch_csv()
    required = {"id", "chapter", "prereq"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        err = (err or "") + f" | Missing columns in CSV: {missing}"
    fig = build_sankey(df)
    html_graph = fig.to_html(include_plotlyjs="cdn", full_html=False)
    return render_template("index.html", html_graph=html_graph, error=err, source=source, auto_refresh=AUTO_REFRESH)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/status")
def status():
    _, err, source = fetch_csv()
    return jsonify({"csv_url": CSV_URL, "source": source, "error": err, "cache_ttl": CACHE_TTL})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
