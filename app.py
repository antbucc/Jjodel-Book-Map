
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__, static_url_path="", static_folder=".")

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/health", methods=["GET", "HEAD"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
