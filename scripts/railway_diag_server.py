"""Tiny stdlib-only HTTP server for Railway healthcheck diagnosis.

Returns 200 for any GET request. No third-party deps.
Used only as a diagnostic; not the production server.
"""
from __future__ import annotations

import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        body = f"diag-ok path={self.path}\n".encode()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[diag-server] {fmt % args}\n")


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    sys.stderr.write(f"[diag-server] listening on 0.0.0.0:{port}\n")
    sys.stderr.flush()
    server.serve_forever()


if __name__ == "__main__":
    main()
