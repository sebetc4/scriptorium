"""Retrieving from the web, and saying out loud what actually came back.

Core rather than a skill's, by docs/architecture.md §2: `fetch` captures one
page through it, and `sourcing` probes and downloads its pieces through it.

Written from what a real investigation hit on an uncooperative web (the
sourcing inventory, §1), where every failure was silent by default:

- **a host that filters user agents** answers 403 to a script — so a browser's
  user agent is sent from the first request;
- **an expired certificate** stops a strict client at the first link — so a
  failed certificate verification is retried unverified, and the response
  *says* it was (`tls_verified`, and `tls=unverified` on its probe line);
- **a silent redirect** lands on an index page with a 200 — so the effective
  URL is kept and printed;
- **a `.pdf` answering HTTP 200 with HTML** (a signup wall, an error page) —
  so the type is sniffed from the bytes, never taken from the name or from the
  `Content-Type` header.

An HTTP error is *answered*, not raised: probing a dead forum and learning it
is a 500 everywhere is a result. Only a transport failure raises.
"""
from __future__ import annotations

import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
TIMEOUT = 30


class NetError(Exception):
    pass


@dataclass
class Response:
    status: int
    content_type: str
    effective_url: str
    body: bytes
    tls_verified: bool = True

    @property
    def size(self) -> int:
        return len(self.body)

    @property
    def mime(self) -> str:
        """What the bytes are, whatever the name or the header claims."""
        return sniff(self.body)

    def line(self) -> str:
        """One line per URL — the probe the investigation ran with curl -w."""
        line = (f"http={self.status} size={self.size} type={self.content_type} "
                f"eff={self.effective_url}")
        return line if self.tls_verified else line + " tls=unverified"


def get(url: str, *, max_bytes: int | None = None, timeout: float = TIMEOUT,
        headers: dict[str, str] | None = None) -> Response:
    """GET `url` with a browser's headers, following redirects."""
    try:
        return _get(url, max_bytes, timeout, headers, ssl.create_default_context())
    except urllib.error.URLError as exc:
        if not isinstance(exc.reason, ssl.SSLCertVerificationError):
            raise NetError(f"{url}: {exc.reason}") from exc
    response = _get(url, max_bytes, timeout, headers, ssl._create_unverified_context())
    response.tls_verified = False
    return response


def _get(url, max_bytes, timeout, headers, context) -> Response:
    request = urllib.request.Request(url, headers={**HEADERS, **(headers or {})})
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as r:
            return _response(r, r.status, url, max_bytes)
    except urllib.error.HTTPError as exc:
        with exc:
            return _response(exc, exc.code, url, max_bytes)
    except urllib.error.URLError:
        raise
    except OSError as exc:              # a timeout, a reset connection
        raise NetError(f"{url}: {exc}") from exc


def _response(r, status: int, url: str, max_bytes: int | None) -> Response:
    body = r.read() if max_bytes is None else r.read(max_bytes + 1)
    if max_bytes is not None and len(body) > max_bytes:
        raise NetError(f"{url}: too large (over {max_bytes} bytes)")
    return Response(status, r.headers.get("Content-Type", ""),
                    r.geturl() or url, body)


def sniff(body: bytes) -> str:
    """The MIME type the bytes themselves declare.

    Covers what a capture or a download here receives — documents, pages and
    images. Anything else is `application/octet-stream`, never a guess.
    """
    if body.startswith(b"%PDF-"):
        return "application/pdf"
    if body.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if body.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if body.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if body[:4] == b"RIFF" and body[8:12] == b"WEBP":
        return "image/webp"
    # A byte-order mark and leading comments come before the markup that says
    # what the document is; both are common on generated pages.
    head = body[:2048].removeprefix(b"\xef\xbb\xbf").lstrip()
    while head.startswith(b"<!--") and b"-->" in head:
        head = head[head.index(b"-->") + 3:].lstrip()
    head = head.lower()
    if head.startswith(b"<?xml") and b"<svg" in head or head.startswith(b"<svg"):
        return "image/svg+xml"
    if head.startswith((b"<!doctype html", b"<html", b"<head", b"<body")):
        return "text/html"
    return "application/octet-stream"
