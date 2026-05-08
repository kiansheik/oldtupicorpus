from __future__ import annotations

import argparse
import json
import socket
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .tooltip_overrides import DEFAULT_DB_PATH, TooltipOverrideStore

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
WILDCARD_HOSTS = {"0.0.0.0", "::", ""}


def _load_json_request(handler: SimpleHTTPRequestHandler) -> dict[str, object]:
    raw_length = handler.headers.get("Content-Length", "0")
    try:
        length = max(0, int(raw_length))
    except ValueError as exc:
        raise ValueError("Invalid Content-Length header.") from exc

    payload = handler.rfile.read(length) if length else b""
    if not payload:
        return {}

    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Request body must be valid JSON.") from exc

    if not isinstance(decoded, dict):
        raise ValueError("JSON request body must be an object.")

    return decoded


def make_handler(
    *,
    site_dir: Path,
    store: TooltipOverrideStore,
) -> type[SimpleHTTPRequestHandler]:
    class DictionaryRequestHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, directory=str(site_dir), **kwargs)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/api/tooltip-overrides":
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "entries": store.list_overrides(),
                        "db_path": str(store.db_path),
                    },
                )
                return
            super().do_GET()

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/api/tooltip-overrides":
                self.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint.")
                return

            try:
                payload = _load_json_request(self)
                tags = payload.get("tags", [])
                text = payload.get("text", "")
                if not isinstance(tags, list) or not all(
                    isinstance(tag, str) for tag in tags
                ):
                    raise ValueError("`tags` must be a JSON array of strings.")
                if not isinstance(text, str):
                    raise ValueError("`text` must be a string.")
                entry = store.save_override(tags, text)
            except ValueError as exc:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {
                        "error": str(exc),
                    },
                )
                return

            self._send_json(
                HTTPStatus.OK,
                {
                    "entry": entry,
                    "deleted": entry is None,
                },
            )

        def _send_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    return DictionaryRequestHandler


def serve_dictionary(
    *,
    host: str,
    port: int,
    site_dir: Path,
    db_path: Path,
) -> None:
    store = TooltipOverrideStore(db_path)
    handler = make_handler(site_dir=site_dir, store=store)
    server = ThreadingHTTPServer((host, port), handler)
    if host in WILDCARD_HOSTS:
        print(f"Serving dictionary on all interfaces at port {port}")
        print(
            f"Open http://<this-computer-ip>:{port} from another device on the same network."
        )
        for ip_address in _candidate_ipv4_addresses():
            print(f"Possible local URL: http://{ip_address}:{port}")
    else:
        print(f"Serving dictionary at http://{host}:{port}")
    print(f"Tooltip overrides DB: {store.db_path}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Serve the dictionary site with a local SQLite-backed tooltip API."
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind the local server to.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the local server to.",
    )
    parser.add_argument(
        "--site-dir",
        default=str(SITE_DIR),
        help="Directory containing the built static site bundle.",
    )
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_DB_PATH),
        help="Path to the SQLite database storing tooltip overrides.",
    )
    args = parser.parse_args(argv)

    serve_dictionary(
        host=args.host,
        port=args.port,
        site_dir=Path(args.site_dir),
        db_path=Path(args.db_path),
    )
    return 0


def _candidate_ipv4_addresses() -> list[str]:
    addresses: set[str] = set()
    try:
        for result in socket.getaddrinfo(
            socket.gethostname(),
            None,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        ):
            ip_address = result[4][0]
            if not ip_address.startswith("127."):
                addresses.add(ip_address)
    except OSError:
        return []
    return sorted(addresses)


if __name__ == "__main__":
    raise SystemExit(main())
