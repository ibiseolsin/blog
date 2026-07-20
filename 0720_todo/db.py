import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from env import load_env

load_env()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

REST_URL = f"{SUPABASE_URL}/rest/v1"


class SupabaseError(RuntimeError):
    pass


class _Session:
    def close(self):
        pass


def get_connection():
    return _Session()


def _request(method, path, params=None, body=None, prefer=None):
    query = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"{REST_URL}/{path}{query}"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")
        raise SupabaseError(f"{method} {path} -> {e.code}: {detail}") from e
    if not raw:
        return []
    return json.loads(raw)


def init_db():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY가 .env에 설정되지 않았습니다."
        )
    try:
        _request("GET", "tasks", params={"select": "id", "limit": "1"})
    except SupabaseError as e:
        raise RuntimeError(
            f"Supabase 연결 확인 실패: {e}\n"
            "supabase/schema.sql을 Supabase SQL Editor에서 실행했는지, "
            ".env의 SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY가 올바른지 확인하세요."
        ) from e


def _row_to_task(row):
    tags = sorted(
        tt["tags"]["name"]
        for tt in (row.get("task_tags") or [])
        if tt.get("tags")
    )
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row.get("description"),
        "is_done": bool(row["is_done"]),
        "due_date": row.get("due_date"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "tags": tags,
    }


def list_tasks(conn):
    rows = _request(
        "GET",
        "tasks",
        params={
            "select": "*,task_tags(tags(name))",
            "order": "is_done.asc,due_date.asc.nullslast,id.asc",
        },
    )
    return [_row_to_task(r) for r in rows]


def get_task(conn, task_id):
    rows = _request(
        "GET",
        "tasks",
        params={"id": f"eq.{task_id}", "select": "*,task_tags(tags(name))"},
    )
    return _row_to_task(rows[0]) if rows else None


def _get_or_create_tag_id(name):
    name = name.strip()
    rows = _request(
        "POST",
        "tags",
        params={"on_conflict": "name"},
        body={"name": name},
        prefer="resolution=merge-duplicates,return=representation",
    )
    return rows[0]["id"]


def _set_task_tags(task_id, tag_names):
    _request("DELETE", "task_tags", params={"task_id": f"eq.{task_id}"})
    seen = set()
    for name in tag_names or []:
        name = (name or "").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        tag_id = _get_or_create_tag_id(name)
        _request(
            "POST",
            "task_tags",
            body={"task_id": task_id, "tag_id": tag_id},
            prefer="resolution=ignore-duplicates",
        )


def create_task(conn, title, description=None, due_date=None, tags=None):
    rows = _request(
        "POST",
        "tasks",
        body={"title": title, "description": description, "due_date": due_date},
        prefer="return=representation",
    )
    task_id = rows[0]["id"]
    _set_task_tags(task_id, tags)
    return get_task(conn, task_id)


def update_task(conn, task_id, fields):
    if get_task(conn, task_id) is None:
        return None
    patch = {}
    for key in ("title", "description", "due_date"):
        if key in fields:
            patch[key] = fields[key]
    if "is_done" in fields:
        patch["is_done"] = bool(fields["is_done"])
    if patch:
        patch["updated_at"] = datetime.now(timezone.utc).isoformat()
        _request("PATCH", "tasks", params={"id": f"eq.{task_id}"}, body=patch)
    if "tags" in fields:
        _set_task_tags(task_id, fields["tags"])
    return get_task(conn, task_id)


def delete_task(conn, task_id):
    rows = _request(
        "DELETE",
        "tasks",
        params={"id": f"eq.{task_id}"},
        prefer="return=representation",
    )
    return len(rows) > 0
