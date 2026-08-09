"""Fail-closed guard for destructive Mongezz E2E harnesses.

This module is intentionally standard-library only so callers can execute the
preflight before importing browser/network clients or performing any I/O that
can mutate application state.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

LOOPBACK_HOSTS = {"127.0.0.1", "localhost"}
ALLOWED_WRITE_TARGETS = {"local", "ci"}
BLOCK_SENTINEL = "SEC_ENV_WRITE_HARNESS_BLOCKED"
OK_SENTINEL = "SEC_ENV_WRITE_HARNESS_PREFLIGHT_OK"


@dataclass(frozen=True)
class WriteHarnessConfig:
    target: str
    supabase_url: str
    supabase_publishable_key: str
    pg_host: str
    pg_port: str
    pg_user: str
    pg_database: str


def block(reason: str) -> None:
    print(f"{BLOCK_SENTINEL}: {reason}")
    raise SystemExit(2)


def _read_env_file_value(name: str, env_file: Path) -> str:
    try:
        text = env_file.read_text()
    except FileNotFoundError:
        block(f"environment file not found: {env_file}")

    match = re.search(rf"^{re.escape(name)}\s*=\s*(.+)$", text, re.M)
    if not match:
        block(f"{name} missing from explicit environment")
    return match.group(1).strip().strip('"').strip("'")


def read_value(name: str, env_file: Path) -> str:
    direct = os.environ.get(name, "").strip()
    if direct:
        return direct
    return _read_env_file_value(name, env_file)


def _normalize_host(value: str) -> str:
    return value.strip().lower().rstrip(".")


def _validate_supabase_url(value: str) -> str:
    try:
        parsed = urlparse(value)
        host = _normalize_host(parsed.hostname or "")
        port = parsed.port
    except ValueError:
        block("VITE_SUPABASE_URL is invalid")

    if parsed.scheme != "http":
        block("VITE_SUPABASE_URL must use http for the isolated local stack")
    if host not in LOOPBACK_HOSTS or port != 54321:
        block("VITE_SUPABASE_URL must target loopback port 54321")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        block("VITE_SUPABASE_URL contains unsupported credentials/query/fragment")
    if parsed.path not in {"", "/"}:
        block("VITE_SUPABASE_URL must target the Supabase root")
    return value.rstrip("/")


def require_write_harness() -> WriteHarnessConfig:
    """Validate explicit destructive-test intent before any write-capable I/O."""

    # This marker must be an explicit process-level opt-in. Do not accept it from
    # .env files, where a stale value could accidentally persist across sessions.
    if os.environ.get("MONGEZZ_E2E_WRITE_TEST") != "1":
        block("MONGEZZ_E2E_WRITE_TEST must equal 1")

    env_file = Path(os.environ.get("MONGEZZ_E2E_ENV_FILE", ".env"))
    target = read_value("MONGEZZ_DEPLOY_TARGET", env_file)
    if target not in ALLOWED_WRITE_TARGETS:
        block("MONGEZZ_DEPLOY_TARGET must be local or ci")

    pg_host = _normalize_host(os.environ.get("PGHOST", ""))
    pg_hostaddr = _normalize_host(os.environ.get("PGHOSTADDR", ""))
    pg_port = os.environ.get("PGPORT", "").strip()
    pg_user = os.environ.get("PGUSER", "").strip()
    pg_database = os.environ.get("PGDATABASE", "").strip()

    if pg_host not in LOOPBACK_HOSTS:
        block("PGHOST must be loopback")
    if pg_hostaddr and pg_hostaddr not in {"127.0.0.1", "::1"}:
        block("PGHOSTADDR must be unset or loopback")
    if os.environ.get("PGSERVICE", "").strip() or os.environ.get("PGSERVICEFILE", "").strip():
        block("PGSERVICE and PGSERVICEFILE are not allowed for destructive E2E")
    if pg_port != "54322":
        block("PGPORT must equal the isolated Supabase port 54322")
    if pg_user != "postgres" or pg_database != "postgres":
        block("PGUSER and PGDATABASE must match the isolated Supabase defaults")

    supabase_url = _validate_supabase_url(read_value("VITE_SUPABASE_URL", env_file))
    publishable_key = read_value("VITE_SUPABASE_PUBLISHABLE_KEY", env_file)
    if not publishable_key:
        block("VITE_SUPABASE_PUBLISHABLE_KEY must be explicit")

    return WriteHarnessConfig(
        target=target,
        supabase_url=supabase_url,
        supabase_publishable_key=publishable_key,
        pg_host=pg_host,
        pg_port=pg_port,
        pg_user=pg_user,
        pg_database=pg_database,
    )


def browser_request_is_isolated(method: str, url_value: str, is_navigation: bool = False) -> bool:
    """Keep destructive browser navigations/writes on the isolated loopback app."""

    try:
        parsed = urlparse(url_value)
        host = _normalize_host(parsed.hostname or "")
    except ValueError:
        return False

    # Session-bearing top-level/frame navigations must never leave the isolated app.
    if is_navigation and host not in LOOPBACK_HOSTS:
        return False

    if host.endswith(".supabase.co"):
        return False

    supabase_path = parsed.path.startswith(("/rest/v1", "/auth/v1", "/storage/v1", "/functions/v1"))
    if supabase_path and host not in LOOPBACK_HOSTS:
        return False

    if method.upper() not in {"GET", "HEAD", "OPTIONS"} and host not in LOOPBACK_HOSTS:
        return False

    return True


def _psql_env(config: WriteHarnessConfig) -> dict[str, str]:
    env = dict(os.environ)
    # Explicit command-line connection args below are authoritative. Remove all
    # alternate routing/startup selectors so inherited runner state cannot steer
    # libpq/psql elsewhere.
    for name in (
        "PGHOST",
        "PGHOSTADDR",
        "PGPORT",
        "PGUSER",
        "PGDATABASE",
        "PGSERVICE",
        "PGSERVICEFILE",
        "PSQLRC",
    ):
        env.pop(name, None)
    return env


def _psql_command(config: WriteHarnessConfig, *args: str) -> list[str]:
    return [
        "psql",
        "-X",
        "-h",
        config.pg_host,
        "-p",
        config.pg_port,
        "-U",
        config.pg_user,
        "-d",
        config.pg_database,
        *args,
    ]


def psql_one(config: WriteHarnessConfig, sql: str) -> str:
    result = subprocess.run(
        _psql_command(config, "-At", "-q", "-c", sql),
        capture_output=True,
        text=True,
        env=_psql_env(config),
    )
    if result.returncode != 0:
        raise RuntimeError(f"psql failed: {result.stderr.strip()}")
    return result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""


def psql_exec(config: WriteHarnessConfig, sql: str) -> None:
    result = subprocess.run(
        _psql_command(config, "-q", "-v", "ON_ERROR_STOP=1", "-c", sql),
        capture_output=True,
        text=True,
        env=_psql_env(config),
    )
    if result.returncode != 0:
        raise RuntimeError(f"psql exec failed: {result.stderr.strip()}")


def preflight_only() -> None:
    config = require_write_harness()
    if browser_request_is_isolated("POST", "https://forbidden.supabase.co/rest/v1/orders"):
        block("browser isolation invariant accepted a known remote Supabase write")
    if browser_request_is_isolated("GET", "https://simple-store-aid.lovable.app/app", True):
        block("browser isolation invariant accepted a known remote navigation")
    # The config object is intentionally not printed because it contains a public
    # key and operational endpoint details that do not belong in routine logs.
    _ = config
    print(f"{OK_SENTINEL}: isolated destructive E2E target verified")


if __name__ == "__main__":
    if "--preflight-only" not in sys.argv:
        block("write_harness_guard.py may only be executed directly with --preflight-only")
    preflight_only()
