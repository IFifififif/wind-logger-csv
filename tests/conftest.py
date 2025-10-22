import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


if "requests" not in sys.modules:
    requests_stub = types.ModuleType("requests")

    def _unavailable(*args, **kwargs):
        raise RuntimeError("requests 库在测试桩中不可用。")

    requests_stub.get = _unavailable
    sys.modules["requests"] = requests_stub


if "dotenv" not in sys.modules:
    dotenv_stub = types.ModuleType("dotenv")

    def load_dotenv(*args, **kwargs):  # pragma: no cover - simple stub
        return False

    dotenv_stub.load_dotenv = load_dotenv
    sys.modules["dotenv"] = dotenv_stub
