
# JJodel Learning Flow – Interactive Sankey (Static CSV)

This project serves a static Plotly Sankey page via Flask. The graph fetches a published CSV **client-side**, so there are no server-side timeouts or proxy issues.

## Deploy on Railway

1. Create a GitHub repo with these files.
2. Railway → New Project → Deploy from GitHub.
3. Open `https://<your-app>.railway.app/health` → should return `{"status":"ok"}`.
4. Open your app root URL to see the Sankey. It auto-loads the prefilled CSV.
   - You can paste a different CSV URL in the input and click **Load** at any time.

## CSV format (required columns)

- `id` — unique section id (e.g., `2.5`)
- `chapter` — chapter label (e.g., `2 Core Principles of MDE`)
- `prereq` — comma-separated list of IDs (e.g., `2.1,2.3`)

Other columns are ignored by the Sankey (but kept in your sheet).

## Local development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export PORT=8000
python app.py
# then visit http://localhost:8000/
```

## Notes
- The CSV is fetched in the browser from your published Google Sheet:
  - File → Share → **Publish to the web** → CSV
  - Use the link that ends with `?output=csv`.
- For GitHub CSV, use the **raw** file URL.
