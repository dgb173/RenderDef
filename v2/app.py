from flask import Flask, render_template, jsonify, request
import datetime as dt
import ast
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from modules.estudio_scraper import (
    obtener_datos_completos_partido,
    obtener_datos_preview_rapido,
    format_ah_as_decimal_string_of,
)

app = Flask(__name__)

MATCH_DATA_URL = "https://live18.nowgoal25.com/gf/data/bf_en-idn1.js"
DEFAULT_TIMEOUT = 15


def _build_http_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "Chrome/116.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8",
            "Referer": "https://live18.nowgoal25.com/",
        }
    )
    return session


def _parse_js_array(raw: str):
    expr = "[" + raw + "]"
    expr = re.sub(r",(?=,)", ",None", expr)
    expr = re.sub(r",(?=\])", ",None", expr)
    return ast.literal_eval(expr)


def _normalize_ah(value) -> str | None:
    if value in (None, "", "-", "?", "N/A"):
        return None
    return format_ah_as_decimal_string_of(str(value))


def _normalize_goal_line(value) -> str | None:
    if value in (None, "", "-", "?", "N/A"):
        return None
    return format_ah_as_decimal_string_of(str(value))


def fetch_upcoming_matches(limit: int = 20, handicap_filter: str | None = None):
    session = _build_http_session()
    try:
        response = session.get(MATCH_DATA_URL, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"No se pudieron descargar los partidos: {exc}") from exc

    entries = re.findall(r"A\[(\d+)\]=\[(.*?)\];", response.text, flags=re.S)
    normalized_filter = _normalize_ah(handicap_filter) if handicap_filter else None

    matches = []
    handicap_values = set()
    now_utc = dt.datetime.utcnow()

    for _, raw in entries:
        try:
            arr = _parse_js_array(raw)
        except (SyntaxError, ValueError):
            continue

        if len(arr) < 26:
            continue

        match_id = str(arr[0])
        home_name = arr[4] or "N/A"
        away_name = arr[5] or "N/A"
        match_time_raw = arr[6]

        try:
            match_dt = dt.datetime.strptime(match_time_raw, "%Y-%m-%d %H:%M:%S")
        except (TypeError, ValueError):
            continue
        if match_dt < now_utc:
            continue

        ah_value = _normalize_ah(arr[21])
        goal_value = _normalize_goal_line(arr[25])
        if ah_value is None or goal_value is None:
            continue

        handicap_values.add(ah_value)
        if normalized_filter and ah_value != normalized_filter:
            continue

        matches.append(
            {
                "id": match_id,
                "time": match_dt.strftime("%Y-%m-%d %H:%M"),
                "home_team": home_name,
                "away_team": away_name,
                "handicap": ah_value,
                "goal_line": goal_value,
            }
        )

    matches.sort(key=lambda m: m["time"])
    handicap_options = sorted(
        {float(val) for val in handicap_values if re.match(r"^-?\d+(?:\.\d+)?$", val)}
    )
    formatted_options = [format_ah_as_decimal_string_of(str(opt)) for opt in handicap_options]

    return matches[:limit], formatted_options


@app.route("/")
def index():
    handicap_filter = request.args.get("handicap")
    try:
        matches, handicap_options = fetch_upcoming_matches(limit=40, handicap_filter=handicap_filter)
        normalized_filter = _normalize_ah(handicap_filter) if handicap_filter else None
    except RuntimeError as exc:
        return render_template(
            "index.html",
            matches=[],
            handicap_filter=None,
            handicap_options=[],
            error=str(exc),
        )

    return render_template(
        "index.html",
        matches=matches,
        handicap_filter=normalized_filter,
        handicap_options=handicap_options,
    )


@app.route("/api/matches")
def api_matches():
    handicap_filter = request.args.get("handicap")
    try:
        matches, _ = fetch_upcoming_matches(limit=40, handicap_filter=handicap_filter)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502
    return jsonify({"matches": matches})


@app.route("/analizar", methods=["GET", "POST"])
def analizar_partido_page():
    if request.method == "POST":
        match_id = (request.form.get("match_id") or "").strip()
        if not match_id.isdigit():
            return render_template("analizar_partido.html", error="Introduce un ID de partido válido.")

        datos_partido = obtener_datos_completos_partido(match_id)
        if datos_partido.get("error"):
            return render_template("analizar_partido.html", error=datos_partido["error"])

        return render_template(
            "estudio.html",
            data=datos_partido,
            format_ah=format_ah_as_decimal_string_of,
        )

    return render_template("analizar_partido.html")


@app.route("/api/preview/<string:match_id>")
def api_preview(match_id: str):
    if not match_id.isdigit():
        return jsonify({"error": "ID inválido."}), 400

    data = obtener_datos_preview_rapido(match_id)
    if data.get("error"):
        return jsonify(data), 502
    return jsonify(data)


@app.route("/test_preview")
def test_preview_page():
    return render_template("test_preview.html")


if __name__ == "__main__":
    app.run(debug=True)
