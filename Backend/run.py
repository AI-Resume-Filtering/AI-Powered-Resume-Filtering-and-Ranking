import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from shutil import which
from urllib.parse import urlparse

from dotenv import load_dotenv

# Limit native math library thread usage before any NumPy/OpenBLAS imports.
for env_var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(env_var, "1")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _is_port_open(host: str, port: int, timeout: float = 0.6) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _parse_mongo_target(uri: str) -> tuple[str, int] | tuple[None, None]:
    # Only auto-start for direct local mongodb://host:port URIs.
    if not uri or not uri.startswith("mongodb://"):
        return None, None

    parsed = urlparse(uri)
    host = parsed.hostname
    port = parsed.port or 27017
    if not host:
        return None, None
    return host, port


def _find_mongod_exe() -> str | None:
    env_path = os.getenv("MONGOD_PATH", "").strip()
    if env_path and os.path.exists(env_path):
        return env_path

    candidates = [
        r"C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe",
        r"C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe",
        r"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    return which("mongod")


def _ensure_local_mongo_started() -> None:
    auto_start = os.getenv("AUTO_START_MONGO", "true").strip().lower() in {"1", "true", "yes", "on"}
    if not auto_start:
        return

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    host, port = _parse_mongo_target(mongo_uri)
    if not host:
        return

    local_hosts = {"localhost", "127.0.0.1", "::1"}
    if host not in local_hosts:
        return

    if _is_port_open(host, port):
        print(f"[startup] MongoDB already running on {host}:{port}")
        return

    mongod_exe = _find_mongod_exe()
    if not mongod_exe:
        print("[startup] mongod executable not found. Install MongoDB or set MONGOD_PATH.")
        return

    workspace_root = Path(PROJECT_ROOT).parent
    db_path = Path(os.getenv("MONGO_DBPATH", str(workspace_root / "mongodb-data")))
    log_path = Path(os.getenv("MONGO_LOGPATH", str(workspace_root / "mongodb-log" / "mongod.log")))
    db_path.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    args = [
        mongod_exe,
        "--dbpath", str(db_path),
        "--logpath", str(log_path),
        "--logappend",
        "--bind_ip", "127.0.0.1",
        "--port", str(port),
    ]

    creation_flags = 0
    if os.name == "nt":
        creation_flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)

    try:
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creation_flags)
    except OSError as exc:
        print(f"[startup] Failed to start MongoDB: {exc}")
        return

    for _ in range(12):
        if _is_port_open(host, port):
            print(f"[startup] MongoDB started on {host}:{port}")
            return
        time.sleep(0.5)

    print(f"[startup] MongoDB did not start on {host}:{port}. Check log: {log_path}")


# Eagerly warm up SBERT model at backend startup
try:
    from Ai_Scoring.Ai_Scoring.semantic_matcher import _get_model
    _get_model()
    print("[startup] SBERT model loaded and cached.")
except Exception as e:
    print(f"[startup] SBERT model warmup failed: {e}")


from app import create_app

load_dotenv()
app = create_app() if __name__ != "__main__" else None


if __name__ == "__main__":
    _ensure_local_mongo_started()
    app = create_app()
    flask_debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5000, debug=flask_debug)
