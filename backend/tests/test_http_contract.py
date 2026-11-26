"""HTTP integration tests for the GoldenClok Contract Demo.

Standard library only. Each test spawns the existing ``.venv`` Uvicorn process
against a freshly seeded temporary SQLite database and talks to it with
``urllib``. No FastAPI TestClient, pytest, or new dependency is used.

Run from the repository root:

    python3 -m unittest discover -s backend/tests -v

The HTTP tests skip cleanly when ``.venv/bin/python`` or Uvicorn is unavailable.
They never touch ``backend/demo.db``; the demo database hash is checked after
the test class finishes.
"""

from __future__ import annotations

import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"
DEMO_DB = BACKEND_DIR / "demo.db"
SAMPLE_PAYLOAD = BACKEND_DIR / "examples" / "sync-request.json"

sys.path.insert(0, str(BACKEND_DIR))
import seed  # noqa: E402

TOKEN = "demo-device-token-do-not-use-in-production"
INVALID_TOKEN = "invalid-token-for-http-contract-tests"

# Canonical synthetic fixture confirmed by the Project Owner in Phase 2.7.2.
CANONICAL_GUARDIAN_PHONE = "+84000000000"

EXPECTED_ACK = ["DEMO-HR-0001", "DEMO-MED-0001", "DEMO-EVT-0002", "DEMO-EVT-0003"]

# Do not let a developer proxy intercept localhost requests.
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def free_port() -> int:
    """Ask the OS for an unused localhost TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def sample_payload() -> dict:
    payload = json.loads(SAMPLE_PAYLOAD.read_text(encoding="utf-8"))
    payload.pop("_comment", None)
    return payload


class HttpContractTests(unittest.TestCase):
    demo_db_hash_before: str | None = None

    @classmethod
    def setUpClass(cls):
        if not VENV_PYTHON.is_file():
            raise unittest.SkipTest(f"missing virtualenv interpreter: {VENV_PYTHON}")
        try:
            probe = subprocess.run(
                [str(VENV_PYTHON), "-c", "import uvicorn"],
                cwd=str(REPO_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise unittest.SkipTest(f"cannot probe Uvicorn in {VENV_PYTHON}: {exc}")
        if probe.returncode != 0:
            detail = probe.stdout.decode("utf-8", "replace").strip()
            raise unittest.SkipTest(f"Uvicorn unavailable in {VENV_PYTHON}: {detail}")
        cls.demo_db_hash_before = sha256_file(DEMO_DB)

    @classmethod
    def tearDownClass(cls):
        if cls.demo_db_hash_before is None:
            return
        after = sha256_file(DEMO_DB)
        if after != cls.demo_db_hash_before:
            raise AssertionError(
                "backend/demo.db changed during the HTTP tests: "
                f"{cls.demo_db_hash_before} -> {after}"
            )

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="gc-http-")
        self.addCleanup(self._tmp.cleanup)
        self.db_path = Path(self._tmp.name) / "http-contract.db"
        seed.seed(self.db_path, reset=True)
        self.port = free_port()
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.proc: subprocess.Popen | None = None
        self._log_handle = None
        self._log_path = Path(self._tmp.name) / "uvicorn.log"
        # Register cleanup before starting so a startup failure still tears down.
        self.addCleanup(self._stop_server)
        self._start_server()

    # -- server lifecycle -------------------------------------------------
    def _start_server(self) -> None:
        self._log_handle = self._log_path.open("w+b")
        env = os.environ.copy()
        env["GOLDENCLOK_DEMO_DB"] = str(self.db_path)
        env["PYTHONUNBUFFERED"] = "1"
        self.proc = subprocess.Popen(
            [
                str(VENV_PYTHON),
                "-m",
                "uvicorn",
                "app:app",
                "--app-dir",
                "backend",
                "--host",
                "127.0.0.1",
                "--port",
                str(self.port),
            ],
            cwd=str(REPO_ROOT),
            env=env,
            stdout=self._log_handle,
            stderr=subprocess.STDOUT,
        )

        deadline = time.monotonic() + 15.0
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                break
            try:
                with OPENER.open(self.base_url + "/health", timeout=0.5) as response:
                    if response.status == 200:
                        return
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                pass
            time.sleep(0.1)

        self.fail(
            "Uvicorn did not become ready on 127.0.0.1:%s\n%s"
            % (self.port, self._server_log())
        )

    def _stop_server(self) -> None:
        proc = getattr(self, "proc", None)
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        if self._log_handle is not None:
            self._log_handle.close()
            self._log_handle = None

    def _server_log(self) -> str:
        try:
            if self._log_handle is not None:
                self._log_handle.flush()
            return self._log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return "<no server log available>"

    # -- HTTP helpers -----------------------------------------------------
    def request(self, method, path, body=None, token=TOKEN, raw_body=None):
        data = raw_body
        if data is None and body is not None:
            data = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path, data=data, method=method
        )
        request.add_header("Accept", "application/json")
        if data is not None:
            request.add_header("Content-Type", "application/json")
        if token is not None:
            request.add_header("Authorization", "Bearer " + token)
        try:
            with OPENER.open(request, timeout=5) as response:
                status = response.status
                raw = response.read()
        except urllib.error.HTTPError as exc:
            status = exc.code
            raw = exc.read()
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = None
        return status, parsed, raw

    def sync(self, payload, token=TOKEN):
        return self.request("POST", "/api/device/sync", body=payload, token=token)

    # -- database helpers -------------------------------------------------
    def _query(self, sql: str, params=()):
        conn = sqlite3.connect(str(self.db_path))
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    def _count(self, table: str) -> int:
        return int(self._query(f"SELECT COUNT(*) FROM {table}")[0][0])

    # -- tests ------------------------------------------------------------
    def test_health_and_dashboard_baseline(self):
        status, body, _ = self.request("GET", "/health", token=None)
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")
        self.assertIs(body["demo"], True)
        self.assertIsInstance(body["server_time"], int)

        status, dashboard, _ = self.request("GET", "/api/dashboard", token=None)
        self.assertEqual(status, 200)
        self.assertIs(dashboard["seeded"], True)
        for key in (
            "device",
            "wearer",
            "schedules",
            "events",
            "measurements",
            "medication_records",
            "sync_logs",
            "rejections",
        ):
            self.assertIn(key, dashboard)

        self.assertEqual(dashboard["device"]["id"], "demo-device-001")
        self.assertEqual(dashboard["device"]["disconnected_after_seconds"], 3600)
        self.assertEqual(len(dashboard["schedules"]), 3)
        self.assertEqual(
            dashboard["wearer"]["guardian_phone"], CANONICAL_GUARDIAN_PHONE
        )
        self.assertEqual(len(dashboard["events"]), 1)  # seeded LOW_BATTERY event
        self.assertEqual(dashboard["measurements"], [])
        self.assertEqual(dashboard["medication_records"], [])

    def test_valid_sync_and_replay_are_idempotent(self):
        payload = sample_payload()

        status, first, _ = self.sync(payload)
        self.assertEqual(status, 200)
        self.assertIsInstance(first["ack"], list)
        self.assertEqual(first["ack"], EXPECTED_ACK)
        self.assertEqual(first["config"]["version"], 3)
        self.assertEqual(len(first["config"]["schedule"]), 3)
        self.assertNotIn("rejected", first)
        self.assertEqual(self._count("health_measurements"), 1)
        self.assertEqual(self._count("medication_records"), 1)
        self.assertEqual(self._count("events"), 3)  # seeded event + two payload events

        status, second, _ = self.sync(payload)
        self.assertEqual(status, 200)
        self.assertEqual(second["ack"], EXPECTED_ACK)
        self.assertEqual(self._count("health_measurements"), 1)
        self.assertEqual(self._count("medication_records"), 1)
        self.assertEqual(self._count("events"), 3)

        logs = self._query(
            "SELECT total_records, accepted, duplicates, rejected "
            "FROM sync_logs ORDER BY id ASC"
        )
        self.assertEqual(logs, [(4, 4, 0, 0), (4, 0, 4, 0)])
        self.assertIsNotNone(self._query("SELECT last_sync_at FROM devices")[0][0])

    def test_authentication_failures_return_401(self):
        payload = sample_payload()

        status, body, _ = self.sync(payload, token=None)
        self.assertEqual(status, 401)
        self.assertEqual(body["error"], "unauthorized")

        status, body, _ = self.sync(payload, token=INVALID_TOKEN)
        self.assertEqual(status, 401)
        self.assertEqual(body["error"], "unauthorized")

        self.assertEqual(self._count("sync_logs"), 0)
        self.assertEqual(self._count("sync_rejections"), 0)

    def test_structural_failures_return_400(self):
        # Empty body.
        status, body, _ = self.sync(None)
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "invalid_payload")

        # Malformed JSON.
        status, body, _ = self.request(
            "POST", "/api/device/sync", token=TOKEN, raw_body=b'{"records": '
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "invalid_payload")

        # Unknown record group.
        status, body, _ = self.sync({"records": {"unknown_group": []}})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "invalid_payload")

        # Missing record_id.
        status, body, _ = self.sync(
            {"records": {"events": [{"event_type": "FALL", "occurred_at": 1}]}}
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "invalid_payload")

        # Non-object record entry.
        status, body, _ = self.sync({"records": {"events": ["not-an-object"]}})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "invalid_payload")

        self.assertEqual(self._count("sync_logs"), 0)
        self.assertEqual(self._count("sync_rejections"), 0)
        self.assertEqual(self._count("events"), 1)  # seed only
        self.assertEqual(self._count("health_measurements"), 0)
        self.assertEqual(self._count("medication_records"), 0)

    def test_mixed_records_are_rejected_but_acked(self):
        payload = {
            "config_version": 3,
            "records": {
                "events": [
                    {
                        "record_id": "HTTP-EVT-GOOD",
                        "event_type": "SOS",
                        "occurred_at": 1795000000,
                    },
                    {
                        "record_id": "HTTP-EVT-BAD",
                        "event_type": "EARTHQUAKE",
                        "occurred_at": 1795000001,
                    },
                ]
            },
        }

        status, body, _ = self.sync(payload)
        self.assertEqual(status, 200)
        self.assertEqual(body["ack"], ["HTTP-EVT-GOOD", "HTTP-EVT-BAD"])
        self.assertEqual(len(body["rejected"]), 1)
        self.assertEqual(body["rejected"][0]["record_id"], "HTTP-EVT-BAD")
        self.assertIn("event_type", body["rejected"][0]["reason"])

        self.assertEqual(self._count("events"), 2)  # seeded event + good event
        self.assertEqual(self._count("sync_rejections"), 1)
        rejection = self._query(
            "SELECT record_id, record_group FROM sync_rejections"
        )[0]
        self.assertEqual(tuple(rejection), ("HTTP-EVT-BAD", "events"))

        status, dashboard, _ = self.request("GET", "/api/dashboard", token=None)
        self.assertEqual(status, 200)
        self.assertEqual(len(dashboard["events"]), 2)
        self.assertEqual(len(dashboard["rejections"]), 1)
        self.assertEqual(dashboard["measurements"], [])
        self.assertEqual(dashboard["medication_records"], [])

    def test_config_version_handshake(self):
        # Device version equals server version: INTERIM behaviour omits config.
        status, body, _ = self.sync({"config_version": 3, "records": {}})
        self.assertEqual(status, 200)
        self.assertEqual(body["ack"], [])
        self.assertNotIn("config", body)

        # Older device version receives the full config.
        status, body, _ = self.sync({"config_version": 2, "records": {}})
        self.assertEqual(status, 200)
        self.assertIn("config", body)
        self.assertEqual(body["config"]["version"], 3)
        self.assertEqual(len(body["config"]["schedule"]), 3)

        # Missing version is treated as needing a full config.
        status, body, _ = self.sync({"records": {}})
        self.assertEqual(status, 200)
        self.assertIn("config", body)


if __name__ == "__main__":
    unittest.main()
