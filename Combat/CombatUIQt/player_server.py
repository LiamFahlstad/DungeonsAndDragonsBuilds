"""The player link: a small web server for phones and laptops on the same
Wi-Fi, showing what the Player Screen shows, read-only. It serves one page and
that page's JSON, and nothing else.

It only ever receives finished bytes (PlayerFeed.publish), never the
combatants or the log file, so it has nothing secret to leak: player_view_rows
and may_read_log_line have already decided what players may see. That's why nothing here imports Qt or
player_view. Standard library only, and it runs in a daemon thread, so it ends
with the app."""

import errno
import hashlib
import json
import socket
import socketserver
import sys
import threading
from collections.abc import Sequence
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import ip_address, ip_network
from pathlib import Path

# Fixed, so a link stays valid between sessions.
PLAYER_PORT = 8765

_PAGE_PATH = Path(__file__).with_name("player_page.html")
_SHUTDOWN_POLL_SECONDS = 0.1  # how long Stop can hold up the window
_REQUEST_TIMEOUT_SECONDS = 5  # a client that goes quiet doesn't keep its thread
# Most likely to be the Wi-Fi first. Anything else is left out, public addresses
# included, so the server can't end up facing the internet.
_PRIVATE_NETWORKS = [
    ip_network("192.168.0.0/16"),
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
]


class PlayerServerError(Exception):
    """The server couldn't start. Its text is written for the GM to read."""


class PlayerFeed:
    """The latest state for the page, as JSON and its ETag. The ETag hashes the
    JSON, not a counter: a change the players can't see (a hidden monster's HP)
    changes nothing here, so it can't be noticed in the traffic either."""

    def __init__(self):
        self._lock = threading.Lock()
        self.publish("", [])

    def publish(self, title: str, rows: list[dict], log: Sequence[dict] = ()):
        body = json.dumps({"title": title, "rows": rows, "log": list(log)}).encode()
        etag = f'"{hashlib.sha256(body).hexdigest()}"'
        with self._lock:
            self._latest = (body, etag)

    def latest(self) -> tuple[bytes, str]:
        with self._lock:
            return self._latest


class _HttpServer(ThreadingHTTPServer):
    # HTTPServer turns this on, and on Windows that lets a second copy of the
    # app bind the same port with no error, so a busy port looks like a working one.
    allow_reuse_address = False
    daemon_threads = True

    def __init__(self, address: tuple[str, int], feed: PlayerFeed, page: bytes):
        self.feed = feed
        self.page = page
        super().__init__(address, _Handler)

    def server_bind(self):
        # Not HTTPServer's: its reverse DNS lookup can hold up the window for
        # seconds, to find a name nothing here uses.
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = self.socket.getsockname()[:2]

    def handle_error(self, request, client_address):
        # A phone going to sleep mid-response is normal, not worth a traceback.
        if not isinstance(sys.exc_info()[1], (ConnectionError, TimeoutError)):
            super().handle_error(request, client_address)


class _Handler(BaseHTTPRequestHandler):
    """Exactly two routes. Never swap this for SimpleHTTPRequestHandler: that
    would serve the repo's files, monster stats and encounter logs included."""

    timeout = _REQUEST_TIMEOUT_SECONDS

    def do_GET(self):
        server = self.server
        assert isinstance(server, _HttpServer)
        # A chat app can add a tracking parameter to a pasted link.
        path = self.path.partition("?")[0]
        if path == "/":
            self._reply(200, server.page, "text/html; charset=utf-8")
        elif path == "/state":
            body, etag = server.feed.latest()
            if self.headers.get("If-None-Match") == etag:
                self._reply(304, b"", etag=etag)
            else:
                self._reply(200, body, "application/json; charset=utf-8", etag)
        else:
            self.send_error(404)

    def _reply(
        self,
        status: int,
        body: bytes,
        content_type: str | None = None,
        etag: str | None = None,
    ):
        self.send_response(status)
        self.send_header("Cache-Control", "no-store")
        if etag is not None:
            self.send_header("ETag", etag)
        if content_type is not None:
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # or every poll prints a line to the console


class PlayerServer:
    """Serves `feed` while it's started. Nothing listens until then, and it can
    be started again after a stop."""

    def __init__(self):
        self.feed = PlayerFeed()
        self._http: _HttpServer | None = None
        self._host: str | None = None
        # Kept across a stop, so a restart goes back to the address the GM
        # picked and phones already on that link recover by themselves.
        self.last_host: str | None = None

    @property
    def running(self) -> bool:
        return self._http is not None

    @property
    def host(self) -> str | None:
        """The address it listens on, while it's running."""
        return self._host

    @property
    def url(self) -> str | None:
        """The link to give the players, while it's running."""
        if self._http is None:
            return None
        return f"http://{self._host}:{self._http.server_port}"

    def start(self, host: str, port: int = PLAYER_PORT):
        """Listen on `host` alone (0 as the port picks a free one), moving
        there if it's running elsewhere. If it can't, it's left stopped and
        this raises PlayerServerError."""
        self.stop()
        try:
            http = _HttpServer((host, port), self.feed, _PAGE_PATH.read_bytes())
        except OSError as error:
            raise PlayerServerError(_start_failure(host, port, error)) from error
        self._http = http
        self._host = host
        self.last_host = host
        threading.Thread(
            target=http.serve_forever,
            kwargs={"poll_interval": _SHUTDOWN_POLL_SECONDS},
            name="player-server",
            daemon=True,
        ).start()

    def stop(self):
        http = self._http
        if http is None:
            return
        self._http = None
        self._host = None
        http.shutdown()
        http.server_close()


def _start_failure(host: str, port: int, error: OSError) -> str:
    if error.errno in (errno.EADDRINUSE, errno.EACCES):
        return (
            f"Port {port} is already in use on {host}, so the link couldn't "
            "start. Is another copy of the combat app running?"
        )
    return f"The link couldn't start on {host}, port {port}: {error.strerror}"


def rank_addresses(addresses: list[str]) -> list[str]:
    """The private addresses in `addresses`, the likeliest Wi-Fi first and
    otherwise in the order given, with no repeats."""
    unique = list(dict.fromkeys(addresses))
    return [
        address
        for network in _PRIVATE_NETWORKS
        for address in unique
        if ip_address(address) in network
    ]


def lan_addresses() -> list[str]:
    """The addresses this PC could offer the players, best guess first. Not
    socket.gethostbyname(socket.gethostname()): on Windows that can be the WSL
    adapter, which phones can't reach."""
    found = []
    # Connecting a UDP socket sends nothing, but picks the adapter the PC would
    # use to go out, which is normally the Wi-Fi.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            probe.connect(("8.8.8.8", 80))
            found.append(probe.getsockname()[0])
        except OSError:
            pass  # no route out, but the Wi-Fi may still be there
    try:
        adapters = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
    except OSError:
        adapters = []
    found += [str(info[4][0]) for info in adapters]
    return rank_addresses(found)
