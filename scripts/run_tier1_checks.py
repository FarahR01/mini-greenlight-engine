#!/usr/bin/env python3
"""
Mini Greenlight Engine — Tier 1 automated verification script.

Runs the full Tier 1 test protocol end to end:
  0. OS detection
  1. Docker Desktop running? (waits + polls, color-coded feedback)
  2. docker compose up -d + wait for all containers healthy
  3. DB init
  4. Rule engine (static JSON)
  5. LocalStack live collector
  6. API auth (no key / wrong key / correct key)
  7. Full async pipeline (gateway -> RabbitMQ -> worker -> Postgres)
  8. DOCX report generated
  9. pytest suite

Color convention (as requested):
  RED    = blocked, requires manual user action (e.g. "open Docker Desktop")
  YELLOW/ORANGE = something is off, needs a fix, but not fatal to the script
  GREEN  = check passed, continuing automatically

Usage:
    python scripts/run_tier1_checks.py
"""

import json
import os
import platform
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    class _NoColor:
        def __getattr__(self, _):
            return ""
    Fore = _NoColor()
    Style = _NoColor()

try:
    import requests
except ImportError:
    print("The 'requests' package is required. Install it with: pip install requests")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Small printing helpers — consistent color semantics throughout the script
# ---------------------------------------------------------------------------

def red(msg: str) -> None:
    print(f"{Fore.RED}{Style.BRIGHT}✗ {msg}{Style.RESET_ALL}")

def green(msg: str) -> None:
    print(f"{Fore.GREEN}{Style.BRIGHT}✓ {msg}{Style.RESET_ALL}")

def orange(msg: str) -> None:
    print(f"{Fore.YELLOW}{Style.BRIGHT}⚠ {msg}{Style.RESET_ALL}")

def info(msg: str) -> None:
    print(f"{Fore.CYAN}→ {msg}{Style.RESET_ALL}")

def header(msg: str) -> None:
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== {msg} ==={Style.RESET_ALL}")


RESULTS: list[tuple[str, bool, str]] = []  # (test_name, passed, note)

def record(name: str, passed: bool, note: str = "") -> None:
    RESULTS.append((name, passed, note))
    if passed:
        green(f"{name} — PASSED {note}")
    else:
        red(f"{name} — FAILED {note}")


# ---------------------------------------------------------------------------
# Step 0 — OS detection
# ---------------------------------------------------------------------------

def detect_os() -> str:
    system = platform.system()
    header("Step 0 — OS detection")
    info(f"Detected OS: {system} ({platform.platform()})")
    if system not in ("Windows", "Darwin", "Linux"):
        orange(f"Unrecognized OS '{system}' — proceeding anyway, but Docker commands may behave differently.")
    return system


# ---------------------------------------------------------------------------
# Step 1 — Docker Desktop / Docker daemon check
# ---------------------------------------------------------------------------

def docker_daemon_reachable() -> bool:
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def ensure_docker_running(os_name: str, poll_seconds: int = 3, timeout_seconds: int = 120) -> bool:
    header("Step 1 — Docker daemon check")

    if shutil.which("docker") is None:
        red("Docker CLI not found on this machine. Install Docker Desktop first: https://www.docker.com/products/docker-desktop/")
        return False

    if docker_daemon_reachable():
        green("Docker is already running.")
        return True

    # Docker CLI exists but the daemon isn't reachable -> user needs to open Docker Desktop manually
    if os_name == "Windows":
        red("Docker Desktop is not running. Please open Docker Desktop manually (search it in the Start menu) and wait for the whale icon in the system tray to stop animating.")
    elif os_name == "Darwin":
        red("Docker Desktop is not running. Please open Docker Desktop manually (Spotlight -> 'Docker') and wait for the whale icon in the menu bar to stabilize.")
    else:
        red("The Docker daemon is not running. Start it with: sudo systemctl start docker")

    info(f"Waiting for Docker to come online (checking every {poll_seconds}s, timeout {timeout_seconds}s)...")
    elapsed = 0
    while elapsed < timeout_seconds:
        time.sleep(poll_seconds)
        elapsed += poll_seconds
        if docker_daemon_reachable():
            green("Docker is now running. Continuing automatically.")
            return True
        print(f"  ... still waiting ({elapsed}s elapsed)", end="\r")

    red(f"Docker did not come online within {timeout_seconds}s. Start it manually and re-run this script.")
    return False


# ---------------------------------------------------------------------------
# Step 2 — docker compose up + container health
# ---------------------------------------------------------------------------

EXPECTED_CONTAINERS = ["postgres", "rabbitmq", "localstack"]  # service names from docker-compose.yml


def compose_up() -> bool:
    header("Step 2 — docker compose up -d")
    try:
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            orange(f"docker compose up returned an error:\n{result.stderr}")
            return False
        green("docker compose up -d executed.")
        return True
    except subprocess.TimeoutExpired:
        orange("docker compose up -d timed out after 120s. Check `docker compose logs` manually.")
        return False


def container_name_for_service(service: str) -> str | None:
    """docker-compose prefixes container names with the project (folder) name."""
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "-q", service],
            capture_output=True, text=True, timeout=15
        )
        container_id = result.stdout.strip()
        if not container_id:
            return None
        inspect = subprocess.run(
            ["docker", "inspect", "--format", "{{.Name}}", container_id],
            capture_output=True, text=True, timeout=15
        )
        return inspect.stdout.strip().lstrip("/")
    except subprocess.TimeoutExpired:
        return None


def wait_for_containers_healthy(services: list[str], timeout_seconds: int = 90, poll_seconds: int = 5) -> bool:
    header("Step 2b — Waiting for containers to be healthy")
    elapsed = 0
    pending = set(services)

    while elapsed < timeout_seconds and pending:
        for service in list(pending):
            name = container_name_for_service(service)
            if name is None:
                orange(f"Service '{service}' has no running container yet.")
                continue
            try:
                result = subprocess.run(
                    ["docker", "inspect", "--format", "{{.State.Health.Status}}", name],
                    capture_output=True, text=True, timeout=10
                )
                status = result.stdout.strip()
            except subprocess.TimeoutExpired:
                status = "unknown"

            if status == "healthy":
                green(f"{service} ({name}) is healthy.")
                pending.discard(service)
            elif status in ("starting", ""):
                info(f"{service} ({name}) still starting...")
            elif status == "unhealthy":
                orange(f"{service} ({name}) reports UNHEALTHY. Run `docker compose logs {service}` to investigate.")
            else:
                orange(f"{service} ({name}) has no healthcheck configured or status is '{status}'. Assuming OK.")
                pending.discard(service)

        if pending:
            time.sleep(poll_seconds)
            elapsed += poll_seconds

    if pending:
        orange(f"Timed out waiting for: {', '.join(pending)}. They may still be starting — check `docker ps` manually.")
        return False

    green("All expected containers are healthy.")
    return True


# ---------------------------------------------------------------------------
# Step 3 — DB init
# ---------------------------------------------------------------------------

def init_db() -> bool:
    header("Step 3 — Database initialization")
    result = subprocess.run(
        [sys.executable, "-m", "app.db.init_db"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        orange(f"DB init failed:\n{result.stderr}\nCheck your .env DATABASE_URL / POSTGRES_* variables (see ADR 0003).")
        return False
    green("Database tables created / already present.")
    return True


# ---------------------------------------------------------------------------
# Step 4 — Rule engine (static JSON)
# ---------------------------------------------------------------------------

def safe_run(cmd: list[str], timeout: int = 60):
    """subprocess.run wrapper that never raises — returns None on any failure
    (missing executable, timeout, etc.) so a single broken tool can't crash
    the whole verification script."""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
        return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr=str(e))


def test_rule_engine() -> None:
    header("Test — Rule engine (static schema_example.json)")
    result = safe_run(
        [sys.executable, "-m", "app.cli", "scan", "--input-file", "app/rules/schema_example.json"]
    )
    passed = result.returncode == 0 and "Risk score" in result.stdout
    record("Rule engine (static JSON)", passed, result.stdout.strip().splitlines()[-1] if passed else result.stderr[:200])


# ---------------------------------------------------------------------------
# Step 5 — LocalStack collector
# ---------------------------------------------------------------------------

def run_shell_safe(cmd: list[str], timeout: int = 20):
    """Run a command that may be a .cmd/.bat wrapper on Windows (e.g. pip console
    scripts like awslocal). Falls back to shell=True on Windows, and never raises —
    returns None on any failure so callers can degrade gracefully instead of crashing."""
    is_windows = platform.system() == "Windows"
    try:
        return subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=timeout,
            shell=is_windows,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
        orange(f"Command failed to execute: {' '.join(cmd)} ({e})")
        return None


def test_localstack_collector() -> None:
    header("Test — LocalStack live collector")

    if shutil.which("awslocal") is None:
        orange("`awslocal` not found — skipping resource creation, testing scan-live against an empty LocalStack account.")
    else:
        result = run_shell_safe(["awslocal", "iam", "create-user", "--user-name", "tier1-test-user"])
        if result is None or result.returncode != 0:
            orange("Could not create test IAM user via awslocal — continuing with whatever LocalStack already has.")

        result = run_shell_safe(["awslocal", "s3", "mb", "s3://tier1-test-bucket"])
        if result is None or result.returncode != 0:
            orange("Could not create test S3 bucket via awslocal (it may already exist) — continuing.")

    result = safe_run([sys.executable, "-m", "app.cli", "scan-live"])
    passed = result.returncode == 0 and "Risk score" in result.stdout
    record("LocalStack live collector", passed, result.stdout.strip().splitlines()[-1] if passed else result.stderr[:200])


# ---------------------------------------------------------------------------
# Step 6 & 7 — API auth + full async pipeline (requires gateway + worker running)
# ---------------------------------------------------------------------------

def start_background_process(cmd: list[str], log_path: Path) -> subprocess.Popen:
    log_file = open(log_path, "w")
    return subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT)


def wait_for_http(url: str, timeout_seconds: int = 30) -> bool:
    elapsed = 0
    while elapsed < timeout_seconds:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code < 500:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
        elapsed += 1
    return False


def test_api_and_pipeline(api_key: str) -> None:
    header("Test — API auth + full async pipeline")

    logs_dir = Path("results/_tier1_logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    info("Starting gateway (uvicorn) in the background...")
    gateway_proc = start_background_process(
        [sys.executable, "-m", "uvicorn", "app.gateway.main:app", "--port", "8000"],
        logs_dir / "gateway.log"
    )
    info("Starting worker in the background...")
    worker_proc = start_background_process(
        [sys.executable, "-m", "app.worker.consumer"],
        logs_dir / "worker.log"
    )

    try:
        if not wait_for_http("http://localhost:8000/health", timeout_seconds=30):
            record("Gateway startup", False, "gateway did not respond on /health within 30s — check results/_tier1_logs/gateway.log")
            return
        record("Gateway startup", True)

        payload_path = Path("app/rules/scan_request_example.json")
        if not payload_path.exists():
            orange(f"{payload_path} not found — building a minimal fallback payload.")
            payload = {
                "vendor_name": "Tier1 Test Vendor",
                "cloud_state": {"vendor_name": "Tier1 Test Vendor", "cloud_provider": "gcp", "iam_users": []}
            }
        else:
            payload = json.loads(payload_path.read_text())

        # 1. No API key -> expect 422
        r = requests.post("http://localhost:8000/scan", json=payload)
        record("Auth: rejects missing API key (422)", r.status_code == 422, f"got {r.status_code}")

        # 2. Wrong API key -> expect 401
        r = requests.post("http://localhost:8000/scan", json=payload, headers={"X-API-Key": "wrong-key"})
        record("Auth: rejects wrong API key (401)", r.status_code == 401, f"got {r.status_code}")

        # 3. Correct API key -> expect 200 + job_id
        r = requests.post("http://localhost:8000/scan", json=payload, headers={"X-API-Key": api_key})
        ok = r.status_code == 200 and "job_id" in r.json()
        record("Auth: accepts correct API key (200)", ok, f"got {r.status_code}")
        if not ok:
            return

        job_id = r.json()["job_id"]
        info(f"Job submitted: {job_id}. Waiting for the worker to process it...")

        # Poll /scans/{job_id} until it appears (worker needs a moment to consume + process)
        found = False
        for _ in range(20):
            time.sleep(1)
            check = requests.get(f"http://localhost:8000/scans/{job_id}", headers={"X-API-Key": api_key})
            if check.status_code == 200:
                found = True
                break
        record("Pipeline: gateway -> RabbitMQ -> worker -> Postgres", found,
               "result retrieved from /scans/{job_id}" if found else "timed out after 20s — check results/_tier1_logs/worker.log")

        # DOCX report check
        docx_files = list(Path("results").glob(f"{job_id}*.docx"))
        record("DOCX report generated", len(docx_files) > 0,
               str(docx_files[0]) if docx_files else "no matching .docx file found in results/")

    finally:
        info("Stopping background gateway and worker processes...")
        gateway_proc.terminate()
        worker_proc.terminate()
        try:
            gateway_proc.wait(timeout=10)
            worker_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            gateway_proc.kill()
            worker_proc.kill()


# ---------------------------------------------------------------------------
# Step 8 — pytest suite
# ---------------------------------------------------------------------------

def run_pytest() -> None:
    header("Test — pytest suite")
    result = safe_run([sys.executable, "-m", "pytest", "tests/", "-v"], timeout=120)
    passed = result.returncode == 0
    last_line = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else result.stderr[:200]
    record("pytest suite", passed, last_line)
    if not passed:
        print(result.stdout[-2000:])  # show the tail of the output for debugging


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    header("SUMMARY")
    total = len(RESULTS)
    passed_count = sum(1 for _, p, _ in RESULTS if p)
    for name, passed, note in RESULTS:
        line = f"{name:<45} {'PASS' if passed else 'FAIL'}  {note}"
        if passed:
            print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{line}{Style.RESET_ALL}")
    print()
    if passed_count == total:
        green(f"{passed_count}/{total} checks passed. Tier 1 is fully validated — ready for Tier 2.")
    else:
        orange(f"{passed_count}/{total} checks passed. Fix the FAILED items above before moving to Tier 2.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"{Style.BRIGHT}Mini Greenlight Engine — Tier 1 verification{Style.RESET_ALL}\n")

    os_name = detect_os()

    if not ensure_docker_running(os_name):
        sys.exit(1)

    if not compose_up():
        sys.exit(1)

    wait_for_containers_healthy(EXPECTED_CONTAINERS)

    if not init_db():
        orange("Continuing despite DB init issues — later tests may fail as a result.")

    test_rule_engine()
    test_localstack_collector()

    api_key = os.getenv("GREENLIGHT_API_KEY", "dev-secret-key-12345")
    test_api_and_pipeline(api_key)

    run_pytest()

    print_summary()


if __name__ == "__main__":
    main()