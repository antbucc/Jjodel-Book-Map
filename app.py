from flask import Flask, render_template_string
import pandas as pd
import plotly.graph_objects as go
import requests

app = Flask(__name__)

CSV_URL = "https://drive.google.com/file/d/1ifz26EtJPuEyOlZUAzkwkYBNF6O3ASBP/view?usp=sharing"  # or GitHub raw link

@app.route("/")
def index():
    df = pd.read_csv(CSV_URL)

    # Simple Sankey at Chapter level
    chapters = df['chapter'].unique().tolist()
    ch_index = {ch: i for i, ch in enumerate(chapters)}

    links = []
    for _, row in df.iterrows():
        if pd.notna(row.get("prereq")):
            for p in str(row["prereq"]).split(","):
                p = p.strip()
                if p and p in df["id"].values:
                    src_ch = df.loc[df["id"]==p, "chapter"].values[0]
                    dst_ch = row["chapter"]
                    if src_ch != dst_ch:
                        links.append((src_ch, dst_ch))

    from collections import Counter
    count = Counter(links)
    sources, targets, values = zip(*[(ch_index[a], ch_index[b], w) for (a,b), w in count.items()])

    fig = go.Figure(data=[go.Sankey(
        node=dict(label=chapters, pad=20, thickness=14),
        link=dict(source=sources, target=targets, value=values)
    )])
    fig.update_layout(title="MDE+Jjodel Learning Flow (Live CSV)")
    html = fig.to_html(include_plotlyjs="cdn")

    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
