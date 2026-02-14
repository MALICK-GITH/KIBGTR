import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_API_URL = (
    "https://1xbet.com/service-api/LiveFeed/Get1x2_VZip?"
    "sports=85&count={count}&lng=fr&gr=285&mode=4&country=96"
    "&getEmpty=true&virtualSports=true&noFilterBlockEvent=true"
)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Referer": "https://1xbet.com/",
    "Origin": "https://1xbet.com",
    "Connection": "keep-alive",
}


def _build_session():
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.3,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


_SESSION = _build_session()


def fetch_1xbet_matches(count=40, *, timeout=10, verify=False, session=None, headers=None):
    url = DEFAULT_API_URL.format(count=count)
    hdrs = dict(DEFAULT_HEADERS)
    if headers:
        hdrs.update(headers)
    sess = session or _SESSION
    response = sess.get(url, headers=hdrs, timeout=timeout, verify=verify)
    response.raise_for_status()
    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError("Invalid JSON response from 1xbet API") from exc
    if not isinstance(data, dict):
        raise ValueError("Unexpected response type from 1xbet API")
    return data.get("Value", [])


def is_1xbet_available(*, timeout=5, verify=False):
    try:
        fetch_1xbet_matches(count=1, timeout=timeout, verify=verify)
        return True
    except Exception:
        return False
