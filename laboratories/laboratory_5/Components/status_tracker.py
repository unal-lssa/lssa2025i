import json
import threading
from pathlib import Path

# Asegura que la carpeta simulator exista
SIMULATOR_DIR = Path(__file__).resolve().parent.parent / "simulator"
SIMULATOR_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = SIMULATOR_DIR / "status_log.json"
log_lock = threading.Lock()

def load_log():
    if not LOG_FILE.exists():
        return {}
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)

def register_status(service_name, code):
    with log_lock:
        log = load_log()
        if service_name not in log:
            log[service_name] = {}
        code_str = str(code)
        log[service_name][code_str] = log[service_name].get(code_str, 0) + 1
        save_log(log)

def reset_log():
    """Elimina todos los registros dejando el JSON limpio."""
    with log_lock:
        save_log({})
