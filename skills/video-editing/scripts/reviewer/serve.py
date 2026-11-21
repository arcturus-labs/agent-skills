#!/usr/bin/env python3
"""Local rendered-video reviewer (standard library). No uploads, token, or edits.
python serve.py --project /path/to/project [--root /path/to/collection] [--port 8765]
"""
from __future__ import annotations
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit
from model import Library, ReviewError, VIDEO_TYPES

STATIC = Path(__file__).parent
ASSETS = {'/static/app.js': ('app.js', 'text/javascript; charset=utf-8'),
          '/static/style.css': ('style.css', 'text/css; charset=utf-8')}


def byte_range(value, size):
    if value is None:
        return 0, size - 1, False
    m = re.fullmatch(r'bytes=(\d{0,20})-(\d{0,20})', value)
    if not m or not any(m.groups()) or size <= 0:
        raise ReviewError('Unsatisfiable byte range', 416)
    left, right = m.groups()
    if left:
        start = int(left)
        end = min(int(right), size - 1) if right else size - 1
    else:
        length = int(right)
        if length <= 0:
            raise ReviewError('Unsatisfiable byte range', 416)
        start, end = max(0, size - length), size - 1
    if start >= size or start > end:
        raise ReviewError('Unsatisfiable byte range', 416)
    return start, end, True


def make_server(library, port=8765):
    class Handler(BaseHTTPRequestHandler):
        def do_HEAD(self):
            self.handle_read(True)

        def do_GET(self):
            self.handle_read(False)

        def do_POST(self):
            self.problem('Read-only server', 405)

        do_PUT = do_POST
        do_DELETE = do_POST
        do_OPTIONS = do_POST

        def handle_read(self, head=False):
            try:
                url = urlsplit(self.path)
                if not self.allowed(url.path):
                    raise ReviewError('Local same-origin access only', 403)
                if url.path in ('/', '/review'):
                    self.content((STATIC / 'index.html').read_bytes(), 'text/html; charset=utf-8', head=head)
                    return
                if url.path in ASSETS:
                    name, mime = ASSETS[url.path]
                    self.content((STATIC / name).read_bytes(), mime, head=head)
                    return
                q = parse_qs(url.query, keep_blank_values=True, max_num_fields=12)
                def param(key, default=''):
                    values = q.get(key, [default])
                    if len(values) != 1:
                        raise ReviewError('Duplicate query parameter')
                    return values[0]
                if url.path == '/api/projects':
                    data = {'projects': library.list_projects()}
                elif url.path == '/api/project':
                    data = library.overview(param('path'))
                elif url.path == '/api/review':
                    data, _ = library.review(param('path'), param('draft', 'project'))
                elif url.path == '/media':
                    _, video = library.review(param('path'), param('draft', 'project'), with_transcript=False)
                    if video is None:
                        raise ReviewError('No rendered video for this selection', 404)
                    self.media(video, head)
                    return
                else:
                    raise ReviewError('Not found', 404)
                self.content(json.dumps(data, ensure_ascii=False, allow_nan=False).encode(),
                             'application/json; charset=utf-8', head=head)
            except ReviewError as exc:
                self.problem(str(exc), exc.status, head)
            except (OSError, ValueError, TypeError, KeyError):
                self.problem('Unable to read project metadata; check the selected files/schema', 400, head)

        def allowed(self, path):
            port = self.server.server_address[1]
            hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
            if self.headers.get('Host') not in hosts:
                return False
            origin = self.headers.get('Origin')
            if origin and origin not in {f'http://{h}' for h in hosts}:
                return False
            if self.headers.get('Sec-Fetch-Site') == 'cross-site':
                # Clicking a chat link is allowed; embedding/fetching local data is not.
                return path in ('/', '/review') and self.headers.get('Sec-Fetch-Mode') == 'navigate'
            return True

        def content(self, body, mime, status=200, head=False):
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            if not head:
                self.wfile.write(body)

        def problem(self, message, status, head=False):
            self.content(json.dumps({'error': message}).encode(), 'application/json', status, head)

        def media(self, path, head):
            # Open once and stream from that descriptor; do not accept a file= URL.
            with path.open('rb') as stream:
                import os
                size = os.fstat(stream.fileno()).st_size
                try:
                    start, end, partial = byte_range(self.headers.get('Range'), size)
                except ReviewError:
                    self.send_response(416)
                    self.send_header('Content-Range', f'bytes */{size}')
                    self.send_header('Content-Length', '0')
                    self.end_headers()
                    return
                self.send_response(206 if partial else 200)
                self.send_header('Content-Type', VIDEO_TYPES[path.suffix.lower()])
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Length', str(max(0, end - start + 1)))
                if partial:
                    self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
                self.end_headers()
                if head:
                    return
                stream.seek(start)
                remaining = end - start + 1
                try:
                    while remaining > 0:
                        chunk = stream.read(min(1024 * 1024, remaining))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    pass  # Normal browser seek cancellation.

        def end_headers(self):
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; media-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            super().end_headers()

        def log_message(self, fmt, *args):
            pass  # URLs may contain private paths. No request/query logging by default.

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.daemon_threads = True
    return server


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', action='append', default=[], help='Explicit project directory (repeatable)')
    ap.add_argument('--root', action='append', default=[], help='Collection directory; projects below it are allowed')
    ap.add_argument('--media-root', action='append', default=[], help='Allow externally stored video under this directory')
    ap.add_argument('--port', type=int, default=8765)
    a = ap.parse_args()
    try:
        library = Library(a.project, a.root, a.media_root)
        server = make_server(library, a.port)
    except (ReviewError, OSError) as exc:
        ap.exit(1, f'{exc}\n')
    print(json.dumps({'url': f'http://127.0.0.1:{server.server_address[1]}/',
                      'projects': [str(p) for p in library.projects],
                      'roots': [str(p) for p in library.roots]}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
