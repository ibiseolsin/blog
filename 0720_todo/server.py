import json
import mimetypes
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import db
from env import load_env

load_env()

PORT = int(os.environ.get("PORT", "8000"))
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

TASK_ID_RE = re.compile(r"^/api/tasks/(\d+)$")


class Handler(BaseHTTPRequestHandler):
    server_version = "TodoHTTP/1.0"

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _serve_static(self, path):
        if path == "/":
            path = "/index.html"
        safe_path = os.path.normpath(path).lstrip("/")
        full_path = os.path.normpath(os.path.join(PUBLIC_DIR, safe_path))
        if not full_path.startswith(PUBLIC_DIR) or not os.path.isfile(full_path):
            self._send_json(404, {"error": "not found"})
            return
        content_type, _ = mimetypes.guess_type(full_path)
        with open(full_path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/tasks":
            conn = db.get_connection()
            try:
                self._send_json(200, db.list_tasks(conn))
            finally:
                conn.close()
            return
        if parsed.path.startswith("/api/"):
            self._send_json(404, {"error": "not found"})
            return
        self._serve_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/tasks":
            self._send_json(404, {"error": "not found"})
            return
        try:
            payload = self._read_json_body()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "invalid JSON"})
            return
        title = (payload.get("title") or "").strip()
        if not title:
            self._send_json(400, {"error": "title is required"})
            return
        conn = db.get_connection()
        try:
            task = db.create_task(
                conn,
                title=title,
                description=payload.get("description"),
                due_date=payload.get("due_date"),
                tags=payload.get("tags"),
            )
        finally:
            conn.close()
        self._send_json(201, task)

    def do_PATCH(self):
        parsed = urlparse(self.path)
        match = TASK_ID_RE.match(parsed.path)
        if not match:
            self._send_json(404, {"error": "not found"})
            return
        task_id = int(match.group(1))
        try:
            payload = self._read_json_body()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "invalid JSON"})
            return
        conn = db.get_connection()
        try:
            task = db.update_task(conn, task_id, payload)
        finally:
            conn.close()
        if task is None:
            self._send_json(404, {"error": "task not found"})
            return
        self._send_json(200, task)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        match = TASK_ID_RE.match(parsed.path)
        if not match:
            self._send_json(404, {"error": "not found"})
            return
        task_id = int(match.group(1))
        conn = db.get_connection()
        try:
            deleted = db.delete_task(conn, task_id)
        finally:
            conn.close()
        if not deleted:
            self._send_json(404, {"error": "task not found"})
            return
        self._send_json(200, {"deleted": True})


def main():
    db.init_db()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Todo app running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
