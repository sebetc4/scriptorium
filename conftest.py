"""Fixtures shared by every suite in the repository.

At the repository root rather than under `tests/`: pytest loads the conftest of
every directory from the rootdir down to a test file, so one file here serves
the repository's own suite *and* each skill's suite. A skill's own conftest
carries only what is local to it — the path to its `scripts/`.
"""
from __future__ import annotations

import contextlib
import http.server
import shutil
import ssl
import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from core import doc

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "tests" / "fixtures" / "library"


@pytest.fixture
def repo() -> Path:
    """The repository root."""
    return ROOT


# --------------------------------------------------------------------------
# The fixture library — never the user's
# --------------------------------------------------------------------------
# `library/` is user content: it is reorganised at any time, and a test that
# reads it fails on a rename rather than on a defect. The suite reads documents
# of its own instead, under tests/fixtures/library/, and only through a copy:
# a build writes `.work/` inside a document and `out/` beside the library, and
# neither may land in the repository. The user's library is checked by
# `make check-library`, which writes nothing.
@pytest.fixture(scope="session")
def fixture_tree(tmp_path_factory) -> Path:
    """A copy of the fixture library, as `<tree>/library`, with `<tree>/out`.

    Copied once per session: the builds that read it are expensive, and each is
    deterministic, so sharing the copy costs no isolation that matters.
    """
    tree = tmp_path_factory.mktemp("fixtures")
    shutil.copytree(FIXTURES, tree / "library")
    (tree / "out").mkdir()
    return tree


@pytest.fixture(scope="session")
def on_fixtures(fixture_tree):
    """`doc.LIBRARY` and `doc.OUT` pointed at the copy, as a context manager.

    For a fixture wider than one test, which cannot take `monkeypatch`:
    `with on_fixtures() as library: …`.
    """
    @contextlib.contextmanager
    def patched():
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(doc, "LIBRARY", fixture_tree / "library")
            mp.setattr(doc, "OUT", fixture_tree / "out")
            yield fixture_tree / "library"
    return patched


@pytest.fixture
def fixture_library(on_fixtures) -> Path:
    """The fixture library, with `doc.LIBRARY` and `doc.OUT` on it for one test."""
    with on_fixtures() as library:
        yield library


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
