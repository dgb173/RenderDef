from pathlib import Path

path = Path('modules/estudio_scraper.py')
text = path.read_text(encoding='utf-8')
marker = 'BASE_URL_OF = "https://live18.nowgoal25.com"\n'
if marker not in text:
    raise SystemExit('marker missing')
if '_create_http_session' not in text:
    helpers = """BASE_URL_OF = \"https://live18.nowgoal25.com\"\n\n\ndef _create_http_session(timeout: int = 15):\n    session = requests.Session()\n    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])\n    adapter = HTTPAdapter(max_retries=retries)\n    session.mount(\"https://\", adapter)\n    session.mount(\"http://\", adapter)\n    session.headers.update({\n        \"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/116.0.0.0 Safari/537.36\",\n        \"Accept-Language\": \"es-ES,es;q=0.9,en-US;q=0.8\",\n        \"Referer\": f\"{BASE_URL_OF}/\",\n    })\n    return session\n\n\ndef _get_soup_from_url(url: str, *, session: requests.Session | None = None, timeout: int = 15):\n    session_local = session or _create_http_session(timeout)\n    response = session_local.get(url, timeout=timeout)\n    response.raise_for_status()\n    return BeautifulSoup(response.text, 'lxml')\n\n"""
    text = text.replace(marker, helpers)
path.write_text(text, encoding='utf-8')

path = Path('modules/estudio_scraper.py')
