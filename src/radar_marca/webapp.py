from __future__ import annotations

from pathlib import Path

from flask import Flask, abort, render_template_string, send_file

from radar_marca.storage import DEFAULT_DATA_DIR, list_brand_profiles, load_brand_profile

INDEX_TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RadarMarca Viewer</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; background: #0b1020; color: #e5e7eb; }
    a { color: #93c5fd; text-decoration: none; }
    .card { background: #121933; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; }
    ul { padding-left: 1.2rem; }
  </style>
</head>
<body>
  <h1>RadarMarca Viewer</h1>
  {% for client, brands in items %}
    <div class="card">
      <h2>{{ client }}</h2>
      <ul>
      {% for brand in brands %}
        <li><a href="/brand/{{ client }}/{{ brand.slug }}">{{ brand.name }}</a></li>
      {% endfor %}
      </ul>
    </div>
  {% endfor %}
</body>
</html>
"""


def create_app(data_dir: str | Path = DEFAULT_DATA_DIR, config_dir: str | Path = "config") -> Flask:
    app = Flask(__name__)
    data_root = Path(data_dir).resolve()
    config_root = Path(config_dir).resolve()

    @app.get("/")
    def index():
        grouped: dict[str, list[dict]] = {}
        for path in list_brand_profiles(config_root):
            profile = load_brand_profile(path)
            grouped.setdefault(profile.client, []).append({"name": profile.brand, "slug": path.stem})
        items = sorted((client, sorted(brands, key=lambda item: item["name"])) for client, brands in grouped.items())
        return render_template_string(INDEX_TEMPLATE, items=items)

    @app.get("/brand/<client>/<brand_slug>")
    def brand_report(client: str, brand_slug: str):
        report_path = data_root / "clients" / client / brand_slug / "reports" / f"{brand_slug}-latest.html"
        if not report_path.exists():
            abort(404)
        return send_file(report_path)

    return app


def run_server(host: str = "127.0.0.1", port: int = 5000, data_dir: str | Path = DEFAULT_DATA_DIR, config_dir: str | Path = "config") -> None:
    app = create_app(data_dir=data_dir, config_dir=config_dir)
    app.run(host=host, port=port)
