"""GoldenClok Contract Demo — FastAPI application.

Scope: the reduced, local-only Contract Demo authorized on 2026-11-23.
This is NOT the approved production architecture (Option D). No Supabase, no
React, no cloud deployment. See docs/Decisions/Phase 2 Contract Demo Scope.md.

Run (from the repository root):
    python3 -m uvicorn app:app --app-dir backend --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
# Support both `app:app --app-dir backend` and `backend.app:app` from the root.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import contract  # noqa: E402
import db  # noqa: E402

DB_PATH = Path(os.environ.get("GOLDENCLOK_DEMO_DB", BASE_DIR / "demo.db"))
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    conn = db.connect(DB_PATH)
    try:
        db.init_schema(conn)
    finally:
        conn.close()
    yield


app = FastAPI(
    title="GoldenClok Contract Demo",
    version="0.1.0-demo",
    description="Reduced, local-only demo. Simulated data only.",
    docs_url=None,  # keep the demo surface minimal
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)


def _bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    return token or None


def _invalid_payload(reason: str) -> JSONResponse:
    return JSONResponse({"error": "invalid_payload", "reason": reason}, status_code=400)


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "demo": True, "server_time": int(time.time())}


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    """Read-only demo projection for the dashboard. Not part of the firmware contract."""
    conn = db.connect(DB_PATH)
    try:
        return db.dashboard_snapshot(conn)
    finally:
        conn.close()


@app.post("/api/device/sync")
async def device_sync(request: Request) -> JSONResponse:
    """Firmware sync endpoint implementing only CONFIRMED contract semantics.

    Status codes:
      401 - missing, unknown or revoked device token (standard HTTP; not a
            contract code, but it must never be 200)
      400 - malformed JSON or structurally invalid payload
      200 - structurally valid payload, including per-record rejections
    """
    token = _bearer_token(request.headers.get("authorization"))
    if token is None:
        return JSONResponse(
            {"error": "unauthorized", "reason": "missing bearer token"}, status_code=401
        )

    raw = await request.body()
    conn = db.connect(DB_PATH)
    try:
        device = db.device_by_token_hash(conn, contract.sha256_hex(token))
        if device is None:
            return JSONResponse(
                {"error": "unauthorized", "reason": "unknown or revoked device token"},
                status_code=401,
            )

        try:
            payload = contract.parse_payload(raw)
            records = contract.collect_records(payload)
        except contract.PayloadError as exc:
            return _invalid_payload(exc.reason)

        accepted = 0
        duplicates = 0
        rejected: list[dict[str, str]] = []
        for record in records:
            contract.validate_record(record)
            if not record.accepted:
                rejected.append({"record_id": record.record_id, "reason": record.reason or ""})
                # Demo-safe trace: identifiers and reason only, never the payload.
                db.log_rejection(
                    conn,
                    device["id"],
                    record.record_id,
                    record.kind,
                    record.reason or "rejected",
                )
                continue
            # Only a real INSERT counts as accepted; an idempotent replay is a duplicate.
            if db.insert_record(conn, device["id"], record):
                accepted += 1
            else:
                duplicates += 1

        device_version = payload.get(contract.INTERIM_REQUEST_CONFIG_VERSION_KEY)
        config = None
        if contract.should_send_config(device_version, device["config_version"]):
            config = contract.build_config(
                device,
                db.wearer(conn, device["wearer_id"]),
                db.schedules(conn, device["id"]),
            )

        body = contract.build_response(ack=[r.record_id for r in records], rejected=rejected, config=config)

        db.log_sync(
            conn,
            device["id"],
            total=len(records),
            accepted=accepted,
            duplicates=duplicates,
            rejected=len(rejected),
            config_version_sent=(config or {}).get("version"),
        )
        return JSONResponse(body, status_code=200)
    finally:
        conn.close()


# Mounted last so the API routes above always win.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
