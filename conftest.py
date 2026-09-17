"""Fixtures shared by every suite in the repository.

At the repository root rather than under `tests/`: pytest loads the conftest of
every directory from the rootdir down to a test file, so one file here serves
the repository's own suite *and* each skill's suite. A skill's own conftest
carries only what is local to it — the path to its `scripts/`.
"""
from __future__ import annotations

import http.server
import shutil
import ssl
import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


@pytest.fixture
def repo() -> Path:
    """The repository root."""
    return ROOT


# --------------------------------------------------------------------------
# A real web server, local and offline
# --------------------------------------------------------------------------
@dataclass
class Route:
    status: int = 200
    body: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)
    # Answer 403 unless the request's User-Agent looks like a browser's: the
    # filtering some hosts do, reproduced.
    browsers_only: bool = False


class Web:
    """A local HTTP(S) server whose answers the test writes.

    Used rather than mocking urllib: what these tests guard is the behaviour of
    real requests — redirects followed, headers sent, a certificate refused —
    and a mock would only replay what the test already believes.
    """

    def __init__(self, scheme: str = "http"):
        self.routes: dict[str, Route] = {}
        self.handlers: list[tuple[str, object]] = []
        self.paths: list[str] = []
        self.requests: list[dict[str, str]] = []
        web = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                web.requests.append(dict(self.headers))
                web.paths.append(self.path)
                route = web.routes.get(self.path)
                if route is None:
                    for prefix, handler in web.handlers:
                        if self.path.startswith(prefix):
                            status, content_type, body = handler(self.path)
                            if isinstance(body, str):
                                body = body.encode("utf-8")
                            route = Route(status, body, {"Content-Type": content_type})
                            break
                if route is None:
                    route = Route(404, b"<!DOCTYPE html><title>404</title>",
                                  {"Content-Type": "text/html"})
                elif route.browsers_only and "Chrome/" not in self.headers.get("User-Agent", ""):
                    route = Route(403, b"<!DOCTYPE html><title>Forbidden</title>",
                                  {"Content-Type": "text/html"})
                self.send_response(route.status)
                for k, v in route.headers.items():
                    self.send_header(k, v)
                self.send_header("Content-Length", str(len(route.body)))
                self.end_headers()
                self.wfile.write(route.body)

            def log_message(self, *args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.scheme = scheme

    def url(self, path: str) -> str:
        return f"{self.scheme}://127.0.0.1:{self.server.server_address[1]}{path}"

    def add(self, path: str, body: bytes | str = b"", status: int = 200,
            content_type: str = "text/html; charset=utf-8", **kw) -> str:
        if isinstance(body, str):
            body = body.encode("utf-8")
        headers = {"Content-Type": content_type, **kw.pop("headers", {})}
        self.routes[path] = Route(status, body, headers, **kw)
        return self.url(path)

    def handle(self, prefix: str, handler) -> str:
        """Answer every path under `prefix` with `handler(path)`.

        The handler returns `(status, content_type, body)`.

        For services whose answer depends on the query — a CDX search, an API.
        """
        self.handlers.append((prefix, handler))
        return self.url(prefix)

    def redirect(self, path: str, to: str) -> str:
        self.routes[path] = Route(302, b"", {"Location": self.url(to)})
        return self.url(path)


def _serve(web: Web):
    # A short poll: shutdown() waits up to one interval, paid by every test.
    thread = threading.Thread(target=web.server.serve_forever,
                              kwargs={"poll_interval": 0.02}, daemon=True)
    thread.start()
    try:
        yield web
    finally:
        web.server.shutdown()
        web.server.server_close()


@pytest.fixture
def web():
    """A local HTTP server; `web.add(path, body, ...)` returns the URL."""
    yield from _serve(Web())


@pytest.fixture
def tls_web(tmp_path):
    """A local HTTPS server whose certificate no client can verify.

    Self-signed rather than expired, which fails verification the same way:
    `ssl.SSLCertVerificationError`. Generating an expired certificate portably
    would need a dependency the repository does not have.
    """
    if not shutil.which("openssl"):
        pytest.skip("openssl is needed to generate the test certificate")
    cert, key = tmp_path / "cert.pem", tmp_path / "key.pem"
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                    "-keyout", str(key), "-out", str(cert), "-days", "1",
                    "-subj", "/CN=127.0.0.1"],
                   check=True, capture_output=True)
    web = Web("https")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    web.server.socket = context.wrap_socket(web.server.socket, server_side=True)
    yield from _serve(web)
